package com.ticketmafia.match_inventory;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.UUID;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class MatchAdminService {
    private final JdbcTemplate jdbcTemplate;
    private final AdminAuditService auditService;
    private final AdminIdempotencyService idempotencyService;

    MatchAdminService(JdbcTemplate jdbcTemplate, AdminAuditService auditService,
                      AdminIdempotencyService idempotencyService) {
        this.jdbcTemplate = jdbcTemplate;
        this.auditService = auditService;
        this.idempotencyService = idempotencyService;
    }

    // Sprint: v1 | Feature: FR-006,BR-008,NFR-004 | US: US-006 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
    // Contract: api-specs-v1.md API-010; erd-v1.md ENT-002; sequence-v1.md SEQ-002
    @Transactional
    public MatchResponse createMatch(UUID actorUserId, String name, Instant startsAt, MatchStatus status,
                                     String idempotencyKey, String requestId, String traceId) {
        var replay = idempotencyService.findResource("ADMIN_MATCH_CREATE", idempotencyKey, actorUserId)
                .flatMap(this::findMatch);
        if (replay.isPresent()) {
            return replay.get();
        }
        String normalizedName = name == null ? "" : name.trim();
        if (normalizedName.length() < 3 || normalizedName.length() > 120 || status == null) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.ADMIN_MATCH_INVALID_REQUEST,
                    "Match name and status are required.", "name,status");
        }
        UUID matchId = UUID.randomUUID();
        try {
            jdbcTemplate.update("""
                    INSERT INTO matches(id, name, starts_at, status)
                    VALUES (?, ?, ?, ?)
                    """, matchId, normalizedName, startsAt == null ? null : Timestamp.from(startsAt), status.name());
        } catch (DuplicateKeyException exception) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.MATCH_DUPLICATE,
                    "A match with the same name and start time already exists.", "name,startsAt");
        }
        idempotencyService.record("ADMIN_MATCH_CREATE", idempotencyKey, actorUserId, matchId,
                ErrorCode.ADMIN_MATCH_INVALID_REQUEST);
        auditService.record(actorUserId, "MATCH_CREATED", "MATCH", matchId, requestId, traceId,
                "{\"status\":\"%s\"}".formatted(status.name()));
        return new MatchResponse(matchId, normalizedName, startsAt, status);
    }

    boolean matchExists(UUID matchId) {
        Integer count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM matches WHERE id = ?", Integer.class, matchId);
        return count != null && count > 0;
    }

    MatchStatus findStatus(UUID matchId) {
        String value = jdbcTemplate.query("SELECT status FROM matches WHERE id = ?",
                (rs, rowNum) -> rs.getString("status"), matchId).stream().findFirst()
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, ErrorCode.MATCH_NOT_FOUND,
                        "Match was not found.", "matchId"));
        return MatchStatus.valueOf(value);
    }

    private java.util.Optional<MatchResponse> findMatch(UUID matchId) {
        return jdbcTemplate.query("""
                SELECT id, name, starts_at, status
                FROM matches
                WHERE id = ?
                """, (rs, rowNum) -> new MatchResponse(
                rs.getObject("id", UUID.class),
                rs.getString("name"),
                rs.getTimestamp("starts_at") == null ? null : rs.getTimestamp("starts_at").toInstant(),
                MatchStatus.valueOf(rs.getString("status"))), matchId).stream().findFirst();
    }

    public record MatchResponse(UUID id, String name, Instant startsAt, MatchStatus status) {
    }
}
