package com.ticketmafia.match_inventory;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
class AdminIdempotencyService {
    private final JdbcTemplate jdbcTemplate;

    AdminIdempotencyService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    // Sprint: v1 | Feature: FR-006,FR-007,NFR-004 | US: US-006,US-007 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
    // Contract: project-reference-v1.md PR-005 stores Idempotency-Key for protected admin mutations
    void record(String scope, String idempotencyKey, UUID actorUserId, UUID resourceId, ErrorCode duplicateErrorCode) {
        Instant now = Instant.now();
        try {
            jdbcTemplate.update("""
                    INSERT INTO idempotency_records(scope, idempotency_key, user_id, request_hash, resource_id, response_status, expires_at)
                    VALUES (?, ?, ?, ?, ?, 200, ?)
                    """, scope, idempotencyKey, actorUserId, scope + ":" + idempotencyKey, resourceId,
                    Timestamp.from(now.plusSeconds(86_400)));
        } catch (DuplicateKeyException exception) {
            throw new ApiException(HttpStatus.CONFLICT, duplicateErrorCode,
                    "Idempotency-Key was already used for this operation.", "Idempotency-Key");
        }
    }

    Optional<UUID> findResource(String scope, String idempotencyKey, UUID actorUserId) {
        return jdbcTemplate.query("""
                SELECT resource_id
                FROM idempotency_records
                WHERE scope = ? AND idempotency_key = ? AND user_id = ?
                """, (rs, rowNum) -> rs.getObject("resource_id", UUID.class), scope, idempotencyKey, actorUserId)
                .stream().findFirst();
    }
}
