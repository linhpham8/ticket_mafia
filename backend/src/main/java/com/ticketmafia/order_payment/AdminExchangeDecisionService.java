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
import java.util.Locale;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AdminExchangeDecisionService {
    private final JdbcTemplate jdbcTemplate;
    private final OrderIdempotencyService idempotencyService;
    private final TicketIssuanceService ticketIssuanceService;
    private final AuditService auditService;
    private final Clock clock;

    @Autowired
    AdminExchangeDecisionService(JdbcTemplate jdbcTemplate, OrderIdempotencyService idempotencyService,
                                 TicketIssuanceService ticketIssuanceService, AuditService auditService) {
        this(jdbcTemplate, idempotencyService, ticketIssuanceService, auditService, Clock.systemUTC());
    }

    AdminExchangeDecisionService(JdbcTemplate jdbcTemplate, OrderIdempotencyService idempotencyService,
                                 TicketIssuanceService ticketIssuanceService, AuditService auditService, Clock clock) {
        this.jdbcTemplate = jdbcTemplate;
        this.idempotencyService = idempotencyService;
        this.ticketIssuanceService = ticketIssuanceService;
        this.auditService = auditService;
        this.clock = clock;
    }

    // Sprint: v1 | Feature: FR-012,BR-007,BR-008,NFR-002 | US: US-012 | Task Group: TG 1.6 Seat Exchange and Local Demo Runtime
    // Contract: api-specs-v1.md API-015; erd-v1.md ENT-003/ENT-004/ENT-005/ENT-008/ENT-010; sequence-v1.md SEQ-004 [TX BEGIN/COMMIT]
    @Transactional
    public ExchangeDecisionResponse decide(ExchangeDecisionCommand command) {
        requireIdempotency(command.idempotencyKey());
        Decision decision = parseDecision(command.decisionValue());
        String normalizedNote = normalizeNote(command.note());
        String requestHash = requestHash(command.orderId(), decision, normalizedNote);
        var replay = idempotencyService.findResource("ADMIN_EXCHANGE_DECISION", command.idempotencyKey(),
                        requestHash, command.adminUserId(), ErrorCode.EXCHANGE_DECISION_INVALID_REQUEST)
                .flatMap(this::findDecisionResult);
        if (replay.isPresent()) {
            return replay.get();
        }

        ExchangeOrder order = lockExchangeOrder(command.orderId());
        Instant now = clock.instant();
        if (!"PENDING_ADMIN_CONFIRM".equals(order.status()) || !order.adminConfirmExpiresAt().isAfter(now)) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.EXCHANGE_NOT_PENDING_CONFIRM,
                    "Exchange order is not pending admin confirmation.", order.status());
        }

        ExchangeDecisionResponse response = decision == Decision.CONFIRM
                ? confirm(order, now)
                : reject(order, now);
        auditService.recordSuccess(command.adminUserId(), "ADMIN_EXCHANGE_" + decision.name(), "ORDER", order.id(),
                command.requestId(), command.traceId(), metadata(decision, normalizedNote, response));
        idempotencyService.record("ADMIN_EXCHANGE_DECISION", command.idempotencyKey(), requestHash,
                command.adminUserId(), order.id(), ErrorCode.EXCHANGE_DECISION_INVALID_REQUEST);
        return response;
    }

    private ExchangeDecisionResponse confirm(ExchangeOrder order, Instant now) {
        UUID newTicketId = ticketIssuanceService.issueExchangeTicket(order.id(), order.userId(), order.newSeatId());
        jdbcTemplate.update("UPDATE orders SET status = 'ISSUED', updated_at = ? WHERE id = ?",
                Timestamp.from(now), order.id());
        jdbcTemplate.update("""
                UPDATE tickets
                SET status = 'EXCHANGED', exchanged_to_ticket_id = ?, updated_at = ?
                WHERE id = ? AND status = 'ISSUED'
                """, newTicketId, Timestamp.from(now), order.oldTicketId());
        jdbcTemplate.update("""
                UPDATE seats
                SET status = 'AVAILABLE', active_order_item_id = NULL, updated_at = ?
                WHERE id = ?
                """, Timestamp.from(now), order.oldSeatId());
        jdbcTemplate.update("""
                UPDATE order_items
                SET active = FALSE
                WHERE order_id = ? AND seat_id = ? AND active = TRUE
                """, order.oldOrderId(), order.oldSeatId());
        jdbcTemplate.update("""
                UPDATE seats
                SET status = 'ISSUED', updated_at = ?
                WHERE id = ?
                """, Timestamp.from(now), order.newSeatId());
        return new ExchangeDecisionResponse(order.id(), "ISSUED", order.oldTicketId(), newTicketId);
    }

    private ExchangeDecisionResponse reject(ExchangeOrder order, Instant now) {
        jdbcTemplate.update("""
                UPDATE seats
                SET status = 'AVAILABLE', active_order_item_id = NULL, updated_at = ?
                WHERE id = ?
                """, Timestamp.from(now), order.newSeatId());
        jdbcTemplate.update("UPDATE order_items SET active = FALSE WHERE order_id = ? AND active = TRUE", order.id());
        jdbcTemplate.update("UPDATE orders SET status = 'REJECTED', updated_at = ? WHERE id = ?",
                Timestamp.from(now), order.id());
        return new ExchangeDecisionResponse(order.id(), "REJECTED", null, null);
    }

    private ExchangeOrder lockExchangeOrder(UUID orderId) {
        return jdbcTemplate.query("""
                SELECT o.id, o.user_id, o.status, o.admin_confirm_expires_at, o.original_ticket_id,
                       t.order_id AS old_order_id, t.seat_id AS old_seat_id, oi.seat_id AS new_seat_id
                FROM orders o
                JOIN tickets t ON t.id = o.original_ticket_id
                JOIN order_items oi ON oi.order_id = o.id AND oi.active = TRUE
                WHERE o.id = ? AND o.type = 'EXCHANGE'
                FOR UPDATE
                """, (rs, rowNum) -> new ExchangeOrder(
                rs.getObject("id", UUID.class),
                rs.getObject("user_id", UUID.class),
                rs.getString("status"),
                rs.getTimestamp("admin_confirm_expires_at").toInstant(),
                rs.getObject("original_ticket_id", UUID.class),
                rs.getObject("old_order_id", UUID.class),
                rs.getObject("old_seat_id", UUID.class),
                rs.getObject("new_seat_id", UUID.class)), orderId).stream().findFirst()
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, ErrorCode.ORDER_NOT_FOUND,
                        "Exchange order was not found.", "orderId"));
    }

    private java.util.Optional<ExchangeDecisionResponse> findDecisionResult(UUID orderId) {
        return jdbcTemplate.query("""
                SELECT o.id, o.status, o.original_ticket_id,
                       (SELECT t.id FROM tickets t WHERE t.order_id = o.id ORDER BY t.issued_at, t.id LIMIT 1) AS new_ticket_id
                FROM orders o
                WHERE o.id = ? AND o.type = 'EXCHANGE'
                """, (rs, rowNum) -> new ExchangeDecisionResponse(
                rs.getObject("id", UUID.class),
                rs.getString("status"),
                rs.getObject("original_ticket_id", UUID.class),
                rs.getObject("new_ticket_id", UUID.class)), orderId).stream().findFirst();
    }

    private Decision parseDecision(String value) {
        try {
            return Decision.valueOf(value == null ? "" : value.toUpperCase(Locale.ROOT));
        } catch (RuntimeException exception) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.EXCHANGE_DECISION_INVALID_REQUEST,
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
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.EXCHANGE_DECISION_INVALID_REQUEST,
                    "Idempotency-Key header is required for exchange decisions.", "Idempotency-Key");
        }
    }

    private String metadata(Decision decision, String note, ExchangeDecisionResponse response) {
        return """
                {"decision":"%s","notePresent":%s,"oldTicketId":"%s","newTicketId":"%s"}
                """.formatted(decision.name(), !note.isBlank(), response.oldTicketId(), response.newTicketId()).trim();
    }

    private String requestHash(UUID orderId, Decision decision, String note) {
        String canonical = "orderId=%s;decision=%s;note=%s".formatted(orderId, decision, note);
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(canonical.getBytes(StandardCharsets.UTF_8));
            return java.util.HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 is required for admin exchange idempotency.", exception);
        }
    }

    public record ExchangeDecisionResponse(UUID orderId, String orderStatus, UUID oldTicketId, UUID newTicketId) {
    }

    public record ExchangeDecisionCommand(UUID adminUserId, UUID orderId, String decisionValue, String note,
                                          String idempotencyKey, String requestId, String traceId) {
    }

    private enum Decision {
        CONFIRM,
        REJECT
    }

    private record ExchangeOrder(UUID id, UUID userId, String status, Instant adminConfirmExpiresAt,
                                 UUID oldTicketId, UUID oldOrderId, UUID oldSeatId, UUID newSeatId) {
    }
}
