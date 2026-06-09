package com.ticketmafia.ticket_scan;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.time.Instant;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class TicketDetailService {
    private final JdbcTemplate jdbcTemplate;
    private final QrTokenService qrTokenService;

    TicketDetailService(JdbcTemplate jdbcTemplate, QrTokenService qrTokenService) {
        this.jdbcTemplate = jdbcTemplate;
        this.qrTokenService = qrTokenService;
    }

    // Sprint: v1 | Feature: FR-009,BR-006,NFR-003 | US: US-010 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
    // Contract: api-specs-v1.md API-009 GET /api/v1/tickets/{ticketId}; nfr-v1.md NFR-003 no PII in QR token
    public TicketDetail detail(UUID userId, UUID ticketId) {
        TicketRecord ticket = findTicket(ticketId);
        if (!ticket.userId().equals(userId)) {
            throw new ApiException(HttpStatus.FORBIDDEN, ErrorCode.TICKET_FORBIDDEN,
                    "User does not own this ticket.", "ticketId");
        }
        String qrToken = "ISSUED".equals(ticket.status()) ? qrTokenService.issueToken(ticket.ticketId()) : null;
        return new TicketDetail(ticket.ticketId(), new MatchSummary(ticket.matchId(), ticket.matchName()),
                ticket.seatCode(), ticket.status(), qrToken, ticket.issuedAt(), ticket.scannedAt());
    }

    private TicketRecord findTicket(UUID ticketId) {
        return jdbcTemplate.query("""
                SELECT t.id ticket_id, t.user_id, t.status, t.issued_at, t.scanned_at,
                       m.id match_id, m.name match_name, s.seat_code
                FROM tickets t
                JOIN orders o ON o.id = t.order_id
                JOIN matches m ON m.id = o.match_id
                JOIN seats s ON s.id = t.seat_id
                WHERE t.id = ?
                """, (rs, rowNum) -> new TicketRecord(
                        rs.getObject("ticket_id", UUID.class),
                        rs.getObject("user_id", UUID.class),
                        rs.getString("status"),
                        rs.getTimestamp("issued_at").toInstant(),
                        rs.getTimestamp("scanned_at") == null ? null : rs.getTimestamp("scanned_at").toInstant(),
                        rs.getObject("match_id", UUID.class),
                        rs.getString("match_name"),
                        rs.getString("seat_code")), ticketId)
                .stream().findFirst()
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, ErrorCode.TICKET_NOT_FOUND,
                        "Ticket was not found.", "ticketId"));
    }

    public record TicketDetail(UUID ticketId, MatchSummary match, String seatCode, String status, String qrToken,
                               Instant issuedAt, Instant scannedAt) {
    }

    public record MatchSummary(UUID id, String name) {
    }

    private record TicketRecord(UUID ticketId, UUID userId, String status, Instant issuedAt, Instant scannedAt,
                                UUID matchId, String matchName, String seatCode) {
    }
}
