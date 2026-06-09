package com.ticketmafia.order_payment;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.Timestamp;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PaymentCompletionService {
    private final JdbcTemplate jdbcTemplate;
    private final OrderIdempotencyService idempotencyService;
    private final Clock clock;
    private final Duration adminConfirmDuration;

    @Autowired
    PaymentCompletionService(JdbcTemplate jdbcTemplate, OrderIdempotencyService idempotencyService,
                             @Value("${ticketing.admin-confirm.duration:PT10M}") Duration adminConfirmDuration) {
        this(jdbcTemplate, idempotencyService, Clock.systemUTC(), adminConfirmDuration);
    }

    PaymentCompletionService(JdbcTemplate jdbcTemplate, OrderIdempotencyService idempotencyService, Clock clock,
                             Duration adminConfirmDuration) {
        this.jdbcTemplate = jdbcTemplate;
        this.idempotencyService = idempotencyService;
        this.clock = clock;
        this.adminConfirmDuration = adminConfirmDuration;
    }

    // Sprint: v1 | Feature: FR-005,BR-005,NFR-002 | US: US-005 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
    // Contract: api-specs-v1.md API-006; erd-v1.md ENT-004/ENT-005; sequence-v1.md SEQ-003 payment completion transaction
    @Transactional
    public PaymentCompletedResponse complete(UUID userId, UUID orderId, String idempotencyKey) {
        requireIdempotency(idempotencyKey);
        String requestHash = requestHash(orderId);
        var replay = idempotencyService.findResource("ORDER_PAYMENT_COMPLETED", idempotencyKey, requestHash, userId,
                        ErrorCode.PAYMENT_COMPLETION_INVALID_REQUEST)
                .flatMap(resourceId -> findPending(resourceId, userId));
        if (replay.isPresent()) {
            return replay.get();
        }
        OrderState order = lockOrder(orderId);
        if (!order.userId().equals(userId)) {
            throw new ApiException(HttpStatus.FORBIDDEN, ErrorCode.ORDER_FORBIDDEN,
                    "Order does not belong to the authenticated user.", "orderId");
        }
        Instant now = clock.instant();
        if (!"HELD".equals(order.status()) || !order.holdExpiresAt().isAfter(now)) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.ORDER_NOT_HELD,
                    "Order is not in an active HELD state.", order.status());
        }
        Instant adminConfirmExpiresAt = now.plus(adminConfirmDuration);
        jdbcTemplate.update("""
                UPDATE orders
                SET status = 'PENDING_ADMIN_CONFIRM', admin_confirm_expires_at = ?, updated_at = ?
                WHERE id = ?
                """, Timestamp.from(adminConfirmExpiresAt), Timestamp.from(now), orderId);
        jdbcTemplate.update("""
                UPDATE seats
                SET status = 'PENDING_ADMIN_CONFIRM', updated_at = ?
                WHERE active_order_item_id IN (
                  SELECT id FROM order_items WHERE order_id = ? AND active = TRUE
                )
                """, Timestamp.from(now), orderId);
        idempotencyService.record("ORDER_PAYMENT_COMPLETED", idempotencyKey, requestHash, userId, orderId,
                ErrorCode.PAYMENT_COMPLETION_INVALID_REQUEST);
        return new PaymentCompletedResponse(orderId, "PENDING_ADMIN_CONFIRM", adminConfirmExpiresAt);
    }

    private OrderState lockOrder(UUID orderId) {
        return jdbcTemplate.query("""
                SELECT id, user_id, status, hold_expires_at
                FROM orders
                WHERE id = ?
                FOR UPDATE
                """, (rs, rowNum) -> new OrderState(
                rs.getObject("id", UUID.class),
                rs.getObject("user_id", UUID.class),
                rs.getString("status"),
                rs.getTimestamp("hold_expires_at").toInstant()), orderId).stream().findFirst()
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, ErrorCode.ORDER_NOT_FOUND,
                        "Order was not found.", "orderId"));
    }

    private java.util.Optional<PaymentCompletedResponse> findPending(UUID orderId, UUID userId) {
        return jdbcTemplate.query("""
                SELECT id, status, admin_confirm_expires_at
                FROM orders
                WHERE id = ? AND user_id = ?
                """, (rs, rowNum) -> new PaymentCompletedResponse(
                rs.getObject("id", UUID.class),
                rs.getString("status"),
                rs.getTimestamp("admin_confirm_expires_at").toInstant()), orderId, userId).stream().findFirst();
    }

    private void requireIdempotency(String idempotencyKey) {
        if (idempotencyKey == null || idempotencyKey.isBlank() || idempotencyKey.length() > 120) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.PAYMENT_COMPLETION_INVALID_REQUEST,
                    "Idempotency-Key header is required for payment completion.", "Idempotency-Key");
        }
    }

    private String requestHash(UUID orderId) {
        String canonical = "orderId=%s".formatted(orderId);
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(canonical.getBytes(StandardCharsets.UTF_8));
            return java.util.HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 is required for payment idempotency.", exception);
        }
    }

    public record PaymentCompletedResponse(UUID orderId, String status, Instant adminConfirmExpiresAt) {
    }

    private record OrderState(UUID id, UUID userId, String status, Instant holdExpiresAt) {
    }
}
