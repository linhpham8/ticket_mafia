package com.ticketmafia.ticket_scan;

import java.sql.Timestamp;
import java.time.Clock;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class TicketIssuanceService {
    private final JdbcTemplate jdbcTemplate;
    private final QrTokenService qrTokenService;
    private final Clock clock;

    @Autowired
    TicketIssuanceService(JdbcTemplate jdbcTemplate, QrTokenService qrTokenService) {
        this(jdbcTemplate, qrTokenService, Clock.systemUTC());
    }

    TicketIssuanceService(JdbcTemplate jdbcTemplate, QrTokenService qrTokenService, Clock clock) {
        this.jdbcTemplate = jdbcTemplate;
        this.qrTokenService = qrTokenService;
        this.clock = clock;
    }

    // Sprint: v1 | Feature: FR-008,BR-005 | US: US-008 | Task Group: TG 1.4 Admin Payment Confirmation and Audit
    // Contract: erd-v1.md ENT-008; sequence-v1.md SEQ-004 confirm purchase inserts tickets in the same transaction
    public List<UUID> issuePurchaseTickets(UUID orderId, UUID userId) {
        Instant now = clock.instant();
        List<TicketSeed> seeds = jdbcTemplate.query("""
                SELECT oi.seat_id
                FROM order_items oi
                WHERE oi.order_id = ? AND oi.active = TRUE
                ORDER BY oi.created_at, oi.id
                """, (rs, rowNum) -> new TicketSeed(rs.getObject("seat_id", UUID.class)), orderId);
        return seeds.stream()
                .map(seed -> insertTicket(orderId, userId, seed.seatId(), now))
                .toList();
    }

    // Sprint: v1 | Feature: FR-012,BR-007 | US: US-012 | Task Group: TG 1.6 Seat Exchange and Local Demo Runtime
    // Contract: api-specs-v1.md API-015; sequence-v1.md SEQ-004 confirm exchange inserts one replacement ticket
    public UUID issueExchangeTicket(UUID orderId, UUID userId, UUID seatId) {
        return insertTicket(orderId, userId, seatId, clock.instant());
    }

    private UUID insertTicket(UUID orderId, UUID userId, UUID seatId, Instant now) {
        UUID ticketId = UUID.randomUUID();
        jdbcTemplate.update("""
                INSERT INTO tickets(id, order_id, seat_id, user_id, status, qr_token_hash, issued_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'ISSUED', ?, ?, ?, ?)
                """, ticketId, orderId, seatId, userId, qrTokenService.hashToken(qrTokenService.issueToken(ticketId)),
                Timestamp.from(now), Timestamp.from(now),
                Timestamp.from(now));
        return ticketId;
    }

    private record TicketSeed(UUID seatId) {
    }
}
