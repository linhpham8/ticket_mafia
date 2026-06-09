package com.ticketmafia.order_payment;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.sql.Timestamp;
import java.time.Clock;
import java.util.Optional;
import java.util.UUID;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
class OrderIdempotencyService {
    private final JdbcTemplate jdbcTemplate;
    private final Clock clock;

    @Autowired
    OrderIdempotencyService(JdbcTemplate jdbcTemplate) {
        this(jdbcTemplate, Clock.systemUTC());
    }

    OrderIdempotencyService(JdbcTemplate jdbcTemplate, Clock clock) {
        this.jdbcTemplate = jdbcTemplate;
        this.clock = clock;
    }

    // Sprint: v1 | Feature: FR-004,FR-005,NFR-002 | US: US-004,US-005 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
    // Contract: project-reference-v1.md PR-005 requires Idempotency-Key records for order mutations
    void record(String scope, String idempotencyKey, String requestHash, UUID userId, UUID resourceId,
                ErrorCode duplicateErrorCode) {
        try {
            jdbcTemplate.update("""
                    INSERT INTO idempotency_records(scope, idempotency_key, user_id, request_hash, resource_id, response_status, expires_at)
                    VALUES (?, ?, ?, ?, ?, 200, ?)
                    """, scope, idempotencyKey, userId, requestHash, resourceId,
                    Timestamp.from(clock.instant().plusSeconds(86_400)));
        } catch (DuplicateKeyException exception) {
            throw new ApiException(HttpStatus.CONFLICT, duplicateErrorCode,
                    "Idempotency-Key was already used for this operation.", "Idempotency-Key");
        }
    }

    Optional<UUID> findResource(String scope, String idempotencyKey, String requestHash, UUID userId,
                                ErrorCode mismatchErrorCode) {
        return jdbcTemplate.query("""
                SELECT resource_id, request_hash
                FROM idempotency_records
                WHERE scope = ? AND idempotency_key = ? AND user_id = ?
                """, (rs, rowNum) -> new IdempotencyRecord(
                        rs.getObject("resource_id", UUID.class),
                        rs.getString("request_hash")), scope, idempotencyKey, userId)
                .stream().findFirst()
                .map(record -> {
                    if (!requestHash.equals(record.requestHash())) {
                        throw new ApiException(HttpStatus.CONFLICT, mismatchErrorCode,
                                "Idempotency-Key was already used with a different request.", "Idempotency-Key");
                    }
                    return record.resourceId();
                });
    }

    Optional<UUID> findResource(String scope, String idempotencyKey, UUID userId) {
        return jdbcTemplate.query("""
                SELECT resource_id
                FROM idempotency_records
                WHERE scope = ? AND idempotency_key = ? AND user_id = ?
                """, (rs, rowNum) -> rs.getObject("resource_id", UUID.class), scope, idempotencyKey, userId)
                .stream().findFirst();
    }

    private record IdempotencyRecord(UUID resourceId, String requestHash) {
    }
}
