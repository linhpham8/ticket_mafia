package com.ticketmafia.order_payment;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ExchangeCheckoutService {
    private final JdbcTemplate jdbcTemplate;
    private final OrderIdempotencyService idempotencyService;
    private final Clock clock;
    private final Duration holdDuration;

    @Autowired
    ExchangeCheckoutService(JdbcTemplate jdbcTemplate, OrderIdempotencyService idempotencyService,
                            @Value("${ticketing.hold.duration:PT10M}") Duration holdDuration) {
        this(jdbcTemplate, idempotencyService, Clock.systemUTC(), holdDuration);
    }

    ExchangeCheckoutService(JdbcTemplate jdbcTemplate, OrderIdempotencyService idempotencyService, Clock clock,
                            Duration holdDuration) {
        this.jdbcTemplate = jdbcTemplate;
        this.idempotencyService = idempotencyService;
        this.clock = clock;
        this.holdDuration = holdDuration;
    }

    // Sprint: v1 | Feature: FR-011,BR-007,NFR-002 | US: US-012 | Task Group: TG 1.6 Seat Exchange and Local Demo Runtime
    // Contract: api-specs-v1.md API-014; erd-v1.md ENT-003/ENT-004/ENT-005/ENT-008; sequence-v1.md SEQ-003 exchange hold transaction
    @Transactional
    public ExchangeCheckoutResponse checkout(UUID userId, UUID ticketId, UUID newSeatId, String idempotencyKey) {
        requireIdempotency(idempotencyKey, ErrorCode.EXCHANGE_INVALID_REQUEST);
        // if (newSeatId == null) {
        //     throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.EXCHANGE_INVALID_REQUEST,
        //             "newSeatId is required.", "newSeatId");
        // }
        String requestHash = requestHash(ticketId, newSeatId);
        var replay = idempotencyService.findResource("EXCHANGE_CHECKOUT", idempotencyKey, requestHash, userId,
                        ErrorCode.EXCHANGE_INVALID_REQUEST)
                .flatMap(orderId -> findExchangeCheckout(orderId, userId));
        if (replay.isPresent()) {
            return replay.get();
        }

        TicketForExchange ticket = lockIssuedTicket(userId, ticketId);
        SeatForExchange replacement = lockReplacementSeat(ticket.matchId(), newSeatId);
        if (replacement.priceVnd().compareTo(ticket.originalPriceVnd()) < 0) {
            throw new ApiException(HttpStatus.UNPROCESSABLE_ENTITY, ErrorCode.EXCHANGE_CHEAPER_SEAT_NOT_ALLOWED,
                    "Replacement seat must be equal-or-higher priced.", "newSeatId");
        }

        BigDecimal difference = replacement.priceVnd().subtract(ticket.originalPriceVnd());
        UUID orderId = UUID.randomUUID();
        UUID itemId = UUID.randomUUID();
        Instant now = clock.instant();
        Instant holdExpiresAt = now.plus(holdDuration);
        jdbcTemplate.update("""
                INSERT INTO orders(id, user_id, match_id, type, status, total_amount_vnd, hold_expires_at,
                                   admin_confirm_expires_at, original_ticket_id, created_at, updated_at)
                VALUES (?, ?, ?, 'EXCHANGE', 'PENDING_ADMIN_CONFIRM', ?, ?, ?, ?, ?, ?)
                """, orderId, userId, ticket.matchId(), difference, Timestamp.from(holdExpiresAt),
                Timestamp.from(holdExpiresAt), ticket.ticketId(), Timestamp.from(now), Timestamp.from(now));
        try {
            jdbcTemplate.update("""
                    INSERT INTO order_items(id, order_id, seat_id, price_snapshot_vnd, active)
                    VALUES (?, ?, ?, ?, TRUE)
                    """, itemId, orderId, replacement.seatId(), replacement.priceVnd());
        } catch (DuplicateKeyException exception) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.EXCHANGE_STATE_CONFLICT,
                    "Replacement seat already has an active hold.", replacement.seatId().toString());
        }
        int updated = jdbcTemplate.update("""
                UPDATE seats
                SET status = 'PENDING_ADMIN_CONFIRM', active_order_item_id = ?, updated_at = ?
                WHERE id = ? AND status = 'AVAILABLE'
                """, itemId, Timestamp.from(now), replacement.seatId());
        // if (updated != 1) {
        //     throw new ApiException(HttpStatus.CONFLICT, ErrorCode.EXCHANGE_STATE_CONFLICT,
        //             "Replacement seat is no longer available.", replacement.seatId().toString());
        // }
        idempotencyService.record("EXCHANGE_CHECKOUT", idempotencyKey, requestHash, userId, orderId,
                ErrorCode.EXCHANGE_INVALID_REQUEST);
        return new ExchangeCheckoutResponse(orderId, "EXCHANGE", difference, holdExpiresAt,
                new PaymentQr(difference.compareTo(BigDecimal.ZERO) > 0 ? defaultPaymentQrAssetRef() : null));
    }

    private TicketForExchange lockIssuedTicket(UUID userId, UUID ticketId) {
        return jdbcTemplate.query("""
                SELECT t.id AS ticket_id, t.user_id, t.status, t.seat_id AS old_seat_id, o.match_id,
                       oi.price_snapshot_vnd AS original_price_vnd
                FROM tickets t
                JOIN orders o ON o.id = t.order_id
                JOIN order_items oi ON oi.order_id = t.order_id AND oi.seat_id = t.seat_id
                WHERE t.id = ?
                FOR UPDATE
                """, this::mapTicketForExchange, ticketId).stream().findFirst()
                .map(ticket -> {
                    if (!ticket.userId().equals(userId)) {
                        throw new ApiException(HttpStatus.FORBIDDEN, ErrorCode.TICKET_FORBIDDEN,
                                "Ticket does not belong to the authenticated user.", "ticketId");
                    }
                    if (!"ISSUED".equals(ticket.status())) {
                        throw new ApiException(HttpStatus.CONFLICT, ErrorCode.EXCHANGE_STATE_CONFLICT,
                                "Only issued tickets can be exchanged.", ticket.status());
                    }
                    return ticket;
                })
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, ErrorCode.TICKET_OR_SEAT_NOT_FOUND,
                        "Ticket was not found.", "ticketId"));
    }

    private SeatForExchange lockReplacementSeat(UUID matchId, UUID newSeatId) {
        return jdbcTemplate.query("""
                SELECT s.id, s.seat_code,
                       COALESCE((
                         SELECT pv.price_vnd
                         FROM price_versions pv
                         WHERE pv.match_id = s.match_id
                           AND pv.section_code = s.section_code
                           AND pv.floor_no = s.floor_no
                           AND pv.is_vip = s.is_vip
                         ORDER BY pv.active_from DESC, pv.created_at DESC
                         LIMIT 1
                       ), 0) AS price_vnd
                FROM seats s
                WHERE s.match_id = ? AND s.id = ? AND s.status = 'AVAILABLE'
                FOR UPDATE
                """, this::mapSeatForExchange, matchId, newSeatId).stream().findFirst()
                .orElseThrow(() -> new ApiException(HttpStatus.CONFLICT, ErrorCode.EXCHANGE_STATE_CONFLICT,
                        "Replacement seat is unavailable.", "newSeatId"));
    }

    private java.util.Optional<ExchangeCheckoutResponse> findExchangeCheckout(UUID orderId, UUID userId) {
        return jdbcTemplate.query("""
                SELECT o.id, o.type, o.total_amount_vnd, o.hold_expires_at
                FROM orders o
                WHERE o.id = ? AND o.user_id = ? AND o.type = 'EXCHANGE'
                """, (rs, rowNum) -> new ExchangeCheckoutResponse(
                rs.getObject("id", UUID.class),
                rs.getString("type"),
                rs.getBigDecimal("total_amount_vnd"),
                rs.getTimestamp("hold_expires_at").toInstant(),
                new PaymentQr(rs.getBigDecimal("total_amount_vnd").compareTo(BigDecimal.ZERO) > 0
                        ? defaultPaymentQrAssetRef() : null)), orderId, userId).stream().findFirst();
    }

    private String defaultPaymentQrAssetRef() {
        return jdbcTemplate.query("""
                SELECT qr_asset_ref
                FROM payment_qr_configs
                WHERE is_default = TRUE
                """, (rs, rowNum) -> rs.getString("qr_asset_ref")).stream().findFirst()
                .orElseThrow(() -> new ApiException(HttpStatus.CONFLICT, ErrorCode.TICKET_OR_SEAT_NOT_FOUND,
                        "Default payment QR is not configured.", "paymentQr"));
    }

    private TicketForExchange mapTicketForExchange(ResultSet rs, int rowNum) throws SQLException {
        return new TicketForExchange(
                rs.getObject("ticket_id", UUID.class),
                rs.getObject("user_id", UUID.class),
                rs.getString("status"),
                rs.getObject("old_seat_id", UUID.class),
                rs.getObject("match_id", UUID.class),
                rs.getBigDecimal("original_price_vnd"));
    }

    private SeatForExchange mapSeatForExchange(ResultSet rs, int rowNum) throws SQLException {
        BigDecimal price = rs.getBigDecimal("price_vnd");
        if (price == null || price.compareTo(BigDecimal.ZERO) <= 0) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.TICKET_OR_SEAT_NOT_FOUND,
                    "Active price is not configured for replacement seat.", rs.getObject("id", UUID.class).toString());
        }
        return new SeatForExchange(rs.getObject("id", UUID.class), rs.getString("seat_code"), price);
    }

    private void requireIdempotency(String idempotencyKey, ErrorCode errorCode) {
        if (idempotencyKey == null || idempotencyKey.isBlank() || idempotencyKey.length() > 120) {
            throw new ApiException(HttpStatus.BAD_REQUEST, errorCode,
                    "Idempotency-Key header is required for exchange checkout.", "Idempotency-Key");
        }
    }

    private String requestHash(UUID ticketId, UUID newSeatId) {
        String canonical = "ticketId=%s;newSeatId=%s".formatted(ticketId, newSeatId);
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(canonical.getBytes(StandardCharsets.UTF_8));
            return java.util.HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 is required for exchange idempotency.", exception);
        }
    }

    public record ExchangeCheckoutResponse(UUID orderId, String type, BigDecimal priceDifferenceVnd,
                                           Instant holdExpiresAt, PaymentQr paymentQr) {
    }

    public record PaymentQr(String assetRef) {
    }

    private record TicketForExchange(UUID ticketId, UUID userId, String status, UUID oldSeatId, UUID matchId,
                                     BigDecimal originalPriceVnd) {
    }

    private record SeatForExchange(UUID seatId, String seatCode, BigDecimal priceVnd) {
    }
}
