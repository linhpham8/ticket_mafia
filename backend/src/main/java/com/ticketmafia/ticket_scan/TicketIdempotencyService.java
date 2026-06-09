package com.ticketmafia.ticket_scan;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.sql.Timestamp;
import java.time.Clock;
import java.util.Optional;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
class TicketIdempotencyService {
    private final JdbcTemplate jdbcTemplate;
    private final Clock clock;

    @Autowired
    TicketIdempotencyService(JdbcTemplate jdbcTemplate) {
        this(jdbcTemplate, Clock.systemUTC());
    }

    TicketIdempotencyService(JdbcTemplate jdbcTemplate, Clock clock) {
        this.jdbcTemplate = jdbcTemplate;
        this.clock = clock;
    }

    // Sprint: v1 | Feature: FR-010,BR-006 | US: US-011 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
    // Contract: project-reference-v1.md PR-005 requires Idempotency-Key records for ticket scan mutations
    void record(String idempotencyKey, String requestHash, UUID actorUserId, UUID ticketId) {
        try {
            jdbcTemplate.update("""
                    INSERT INTO idempotency_records(scope, idempotency_key, user_id, request_hash, resource_id, response_status, expires_at)
                    VALUES ('TICKET_SCAN', ?, ?, ?, ?, 200, ?)
                    """, idempotencyKey, actorUserId, requestHash, ticketId,
                    Timestamp.from(clock.instant().plusSeconds(86_400)));
        } catch (DuplicateKeyException exception) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.SCAN_TOKEN_INVALID,
                    "Idempotency-Key was already used for this operation.", "Idempotency-Key");
        }
    }

    Optional<UUID> findResource(String idempotencyKey, String requestHash, UUID actorUserId) {
        return jdbcTemplate.query("""
                SELECT resource_id, request_hash
                FROM idempotency_records
                WHERE scope = 'TICKET_SCAN' AND idempotency_key = ? AND user_id = ?
                """, (rs, rowNum) -> new IdempotencyRecord(
                        rs.getObject("resource_id", UUID.class),
                        rs.getString("request_hash")), idempotencyKey, actorUserId)
                .stream().findFirst()
                .map(record -> {
                    if (!requestHash.equals(record.requestHash())) {
                        throw new ApiException(HttpStatus.CONFLICT, ErrorCode.SCAN_TOKEN_INVALID,
                                "Idempotency-Key was already used with a different request.", "Idempotency-Key");
                    }
                    return record.resourceId();
                });
    }

    private record IdempotencyRecord(UUID resourceId, String requestHash) {
    }
}
