package com.ticketmafia.order_payment;

import com.ticketmafia.audit.AuditService;
import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import com.ticketmafia.ticket_scan.TicketIssuanceService;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.Timestamp;
import java.time.Clock;
import java.time.Instant;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AdminOrderDecisionService {
    private final JdbcTemplate jdbcTemplate;
    private final OrderIdempotencyService idempotencyService;
    private final TicketIssuanceService ticketIssuanceService;
    private final AuditService auditService;
    private final Clock clock;

    @Autowired
    AdminOrderDecisionService(JdbcTemplate jdbcTemplate, OrderIdempotencyService idempotencyService,
                              TicketIssuanceService ticketIssuanceService, AuditService auditService) {
        this(jdbcTemplate, idempotencyService, ticketIssuanceService, auditService, Clock.systemUTC());
    }

    AdminOrderDecisionService(JdbcTemplate jdbcTemplate, OrderIdempotencyService idempotencyService,
                              TicketIssuanceService ticketIssuanceService, AuditService auditService, Clock clock) {
        this.jdbcTemplate = jdbcTemplate;
        this.idempotencyService = idempotencyService;
        this.ticketIssuanceService = ticketIssuanceService;
        this.auditService = auditService;
        this.clock = clock;
    }

    // Sprint: v1 | Feature: FR-008,BR-005,NFR-004 | US: US-008 | Task Group: TG 1.4 Admin Payment Confirmation and Audit
    // Contract: api-specs-v1.md API-007; erd-v1.md ENT-004/ENT-008/ENT-010; sequence-v1.md SEQ-004 [TX BEGIN/COMMIT]
    @Transactional
    public DecisionResponse decide(DecisionCommand command) {
        requireIdempotency(command.idempotencyKey());
        Decision decision = parseDecision(command.decisionValue());
        String normalizedNote = normalizeNote(command.note());
        String requestHash = requestHash(command.orderId(), decision, normalizedNote);
        var replay = idempotencyService.findResource("ADMIN_ORDER_DECISION", command.idempotencyKey(), requestHash,
                        command.adminUserId(), ErrorCode.ADMIN_DECISION_INVALID_REQUEST)
                .flatMap(this::findDecisionResult);
        if (replay.isPresent()) {
            return replay.get();
        }
        OrderState order = lockOrder(command.orderId());
        Instant now = clock.instant();
        if (!"PURCHASE".equals(order.type()) || !"PENDING_ADMIN_CONFIRM".equals(order.status())
                || order.adminConfirmExpiresAt() == null || !order.adminConfirmExpiresAt().isAfter(now)) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.ORDER_NOT_PENDING_CONFIRM,
                "Order is not pending admin confirmation.", order.status());
        }

        List<UUID> ticketIds = decision == Decision.CONFIRM
                ? confirm(order, now)
                : reject(order, now);
        auditService.recordSuccess(command.adminUserId(), "ADMIN_ORDER_" + decision.name(), "ORDER", order.id(),
                command.requestId(), command.traceId(), metadata(decision, normalizedNote, ticketIds.size()));
        idempotencyService.record("ADMIN_ORDER_DECISION", command.idempotencyKey(), requestHash,
                command.adminUserId(), order.id(), ErrorCode.ADMIN_DECISION_INVALID_REQUEST);
        return new DecisionResponse(order.id(), decision == Decision.CONFIRM ? "ISSUED" : "REJECTED", ticketIds);
    }

    private List<UUID> confirm(OrderState order, Instant now) {
        List<UUID> ticketIds = ticketIssuanceService.issuePurchaseTickets(order.id(), order.userId());
        jdbcTemplate.update("UPDATE orders SET status = 'ISSUED', updated_at = ? WHERE id = ?",
                Timestamp.from(now), order.id());
        jdbcTemplate.update("""
                UPDATE seats
                SET status = 'ISSUED', updated_at = ?
                WHERE active_order_item_id IN (
                  SELECT id FROM order_items WHERE order_id = ? AND active = TRUE
                )
                """, Timestamp.from(now), order.id());
        return ticketIds;
    }

    private List<UUID> reject(OrderState order, Instant now) {
        releaseSeats(order.id(), now);
        jdbcTemplate.update("UPDATE orders SET status = 'REJECTED', updated_at = ? WHERE id = ?",
                Timestamp.from(now), order.id());
        return List.of();
    }

    void cancelExpiredPendingOrder(UUID orderId, Instant now) {
        releaseSeats(orderId, now);
        jdbcTemplate.update("UPDATE orders SET status = 'CANCELLED', updated_at = ? WHERE id = ?",
                Timestamp.from(now), orderId);
    }

    private void releaseSeats(UUID orderId, Instant now) {
        jdbcTemplate.update("""
                UPDATE seats
                SET status = 'AVAILABLE', active_order_item_id = NULL, updated_at = ?
                WHERE active_order_item_id IN (
                  SELECT id FROM order_items WHERE order_id = ? AND active = TRUE
                )
                """, Timestamp.from(now), orderId);
        jdbcTemplate.update("UPDATE order_items SET active = FALSE WHERE order_id = ? AND active = TRUE", orderId);
    }

    private OrderState lockOrder(UUID orderId) {
        return jdbcTemplate.query("""
                SELECT id, user_id, type, status, admin_confirm_expires_at
                FROM orders
                WHERE id = ?
                FOR UPDATE
                """, (rs, rowNum) -> new OrderState(
                rs.getObject("id", UUID.class),
                rs.getObject("user_id", UUID.class),
                rs.getString("type"),
                rs.getString("status"),
                rs.getTimestamp("admin_confirm_expires_at") == null
                        ? null : rs.getTimestamp("admin_confirm_expires_at").toInstant()), orderId)
                .stream().findFirst()
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, ErrorCode.ORDER_NOT_FOUND,
                        "Order was not found.", "orderId"));
    }

    private java.util.Optional<DecisionResponse> findDecisionResult(UUID orderId) {
        return jdbcTemplate.query("""
                SELECT id, status
                FROM orders
                WHERE id = ?
                """, (rs, rowNum) -> new DecisionResponse(
                rs.getObject("id", UUID.class),
                rs.getString("status"),
                findTicketIds(orderId)), orderId).stream().findFirst();
    }

    private List<UUID> findTicketIds(UUID orderId) {
        return jdbcTemplate.query("""
                SELECT id
                FROM tickets
                WHERE order_id = ?
                ORDER BY issued_at, id
                """, (rs, rowNum) -> rs.getObject("id", UUID.class), orderId);
    }

    private Decision parseDecision(String value) {
        try {
            return Decision.valueOf(value == null ? "" : value.toUpperCase(Locale.ROOT));
        } catch (RuntimeException exception) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.ADMIN_DECISION_INVALID_REQUEST,
                    "decision must be CONFIRM or REJECT.", "decision");
        }
    }

    private String normalizeNote(String note) {
        if (note == null) {
            return "";
        }
        String normalized = note.trim();
        if (normalized.length() > 500) {
            throw new ApiException(HttpStatus.UNPROCESSABLE_ENTITY, ErrorCode.VALIDATION_ERROR,
                    "note must be at most 500 characters.", "note");
        }
        return normalized;
    }

    private void requireIdempotency(String idempotencyKey) {
        if (idempotencyKey == null || idempotencyKey.isBlank() || idempotencyKey.length() > 120) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.ADMIN_DECISION_INVALID_REQUEST,
                    "Idempotency-Key header is required for admin decisions.", "Idempotency-Key");
        }
    }

    private String metadata(Decision decision, String note, int ticketCount) {
        return """
                {"decision":"%s","notePresent":%s,"ticketCount":%d}
                """.formatted(decision.name(), !note.isBlank(), ticketCount).trim();
    }

    private String requestHash(UUID orderId, Decision decision, String note) {
        String canonical = "orderId=%s;decision=%s;note=%s".formatted(orderId, decision, note);
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(canonical.getBytes(StandardCharsets.UTF_8));
            return java.util.HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 is required for admin decision idempotency.", exception);
        }
    }

    public record DecisionResponse(UUID orderId, String status, List<UUID> ticketIds) {
    }

    public record DecisionCommand(UUID adminUserId, UUID orderId, String decisionValue, String note,
                                  String idempotencyKey, String requestId, String traceId) {
    }

    private enum Decision {
        CONFIRM,
        REJECT
    }

    private record OrderState(UUID id, UUID userId, String type, String status, Instant adminConfirmExpiresAt) {
    }
}
