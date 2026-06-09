package com.ticketmafia.ticket_scan;

import com.ticketmafia.audit.AuditService;
import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.Timestamp;
import java.time.Clock;
import java.time.Instant;
import java.util.HexFormat;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TicketScanService {
    private final JdbcTemplate jdbcTemplate;
    private final QrTokenService qrTokenService;
    private final TicketIdempotencyService idempotencyService;
    private final AuditService auditService;
    private final Clock clock;

    @Autowired
    TicketScanService(JdbcTemplate jdbcTemplate, QrTokenService qrTokenService,
                      TicketIdempotencyService idempotencyService, AuditService auditService) {
        this(jdbcTemplate, qrTokenService, idempotencyService, auditService, Clock.systemUTC());
    }

    TicketScanService(JdbcTemplate jdbcTemplate, QrTokenService qrTokenService,
                      TicketIdempotencyService idempotencyService, AuditService auditService, Clock clock) {
        this.jdbcTemplate = jdbcTemplate;
        this.qrTokenService = qrTokenService;
        this.idempotencyService = idempotencyService;
        this.auditService = auditService;
        this.clock = clock;
    }

    // Sprint: v1 | Feature: FR-010,BR-006 | US: US-011 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
    // Contract: api-specs-v1.md API-013 POST /api/v1/tickets/scan; sequence-v1.md SEQ-005 [TX BEGIN/COMMIT] atomic scan
    @Transactional
    public ScanResponse scan(ScanCommand command) {
        requireIdempotency(command.idempotencyKey());
        String scanSource = normalizeScanSource(command.scanSource());
        if (!qrTokenService.isWellFormed(command.qrToken())) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.SCAN_TOKEN_INVALID,
                    "qrToken must be a signed ticket token.", "qrToken");
        }
        String requestHash = requestHash(command.qrToken(), scanSource);
        var replay = idempotencyService.findResource(command.idempotencyKey(), requestHash, command.actorUserId())
                .flatMap(this::findScannedTicket);
        if (replay.isPresent()) {
            return replay.get();
        }
        TicketScanRecord ticket = lockTicketByToken(command.qrToken());
        if (!"ISSUED".equals(ticket.status())) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.TICKET_ALREADY_SCANNED,
                    "Ticket is not valid for first scan.", ticket.status());
        }
        Instant now = clock.instant();
        jdbcTemplate.update("""
                UPDATE tickets
                SET status = 'USED_SCANNED', scanned_at = ?, updated_at = ?
                WHERE id = ? AND status = 'ISSUED'
                """, Timestamp.from(now), Timestamp.from(now), ticket.ticketId());
        jdbcTemplate.update("UPDATE seats SET status = 'USED_SCANNED', updated_at = ? WHERE id = ?",
                Timestamp.from(now), ticket.seatId());
        auditService.recordSuccess(command.actorUserId(), "TICKET_SCAN", "TICKET", ticket.ticketId(),
                command.requestId(), command.traceId(), metadata(scanSource));
        idempotencyService.record(command.idempotencyKey(), requestHash, command.actorUserId(), ticket.ticketId());
        return new ScanResponse(ticket.ticketId(), "USED_SCANNED", now);
    }

    private TicketScanRecord lockTicketByToken(String qrToken) {
        return jdbcTemplate.query("""
                SELECT id, seat_id, status
                FROM tickets
                WHERE qr_token_hash = ?
                FOR UPDATE
                """, (rs, rowNum) -> new TicketScanRecord(
                        rs.getObject("id", UUID.class),
                        rs.getObject("seat_id", UUID.class),
                        rs.getString("status")), qrTokenService.hashToken(qrToken))
                .stream().findFirst()
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, ErrorCode.TICKET_NOT_FOUND,
                        "Ticket token was not found.", "qrToken"));
    }

    private java.util.Optional<ScanResponse> findScannedTicket(UUID ticketId) {
        return jdbcTemplate.query("""
                SELECT id, status, scanned_at
                FROM tickets
                WHERE id = ?
                """, (rs, rowNum) -> new ScanResponse(
                        rs.getObject("id", UUID.class),
                        rs.getString("status"),
                        rs.getTimestamp("scanned_at") == null ? null : rs.getTimestamp("scanned_at").toInstant()),
                ticketId).stream().findFirst();
    }

    private void requireIdempotency(String idempotencyKey) {
        if (idempotencyKey == null || idempotencyKey.isBlank() || idempotencyKey.length() > 120) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.SCAN_TOKEN_INVALID,
                    "Idempotency-Key header is required for ticket scan.", "Idempotency-Key");
        }
    }

    private String normalizeScanSource(String scanSource) {
        String normalized = scanSource == null || scanSource.isBlank() ? "demo-gate" : scanSource.trim();
        if (normalized.length() > 120) {
            throw new ApiException(HttpStatus.UNPROCESSABLE_ENTITY, ErrorCode.VALIDATION_ERROR,
                    "scanSource must be at most 120 characters.", "scanSource");
        }
        return normalized;
    }

    private String metadata(String scanSource) {
        return """
                {"scanSource":"%s"}
                """.formatted(escapeJson(scanSource)).trim();
    }

    private String escapeJson(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private String requestHash(String qrToken, String scanSource) {
        String canonical = "qrToken=%s;scanSource=%s".formatted(qrToken, scanSource);
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(canonical.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 is required for ticket scan idempotency.", exception);
        }
    }

    public record ScanResponse(UUID ticketId, String status, Instant scannedAt) {
    }

    public record ScanCommand(UUID actorUserId, String qrToken, String scanSource, String idempotencyKey,
                              String requestId, String traceId) {
    }

    private record TicketScanRecord(UUID ticketId, UUID seatId, String status) {
    }
}
