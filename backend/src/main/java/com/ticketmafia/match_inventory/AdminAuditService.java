package com.ticketmafia.match_inventory;

import java.util.UUID;
import javax.sql.DataSource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
class AdminAuditService {
    private final JdbcTemplate jdbcTemplate;
    private final boolean h2;

    AdminAuditService(JdbcTemplate jdbcTemplate, DataSource dataSource) {
        this.jdbcTemplate = jdbcTemplate;
        this.h2 = detectH2(dataSource);
    }

    // Sprint: v1 | Feature: FR-006,FR-007,NFR-004 | US: US-006,US-007 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
    // Contract: sequence-v1.md SEQ-002 audit_logs write for admin inventory mutations
    void record(UUID actorUserId, String action, String resourceType, UUID resourceId, String requestId, String traceId,
                String metadataJson) {
        String sql = h2 ? """
                INSERT INTO audit_logs(actor_user_id, action, resource_type, resource_id, result, request_id, trace_id, metadata)
                VALUES (?, ?, ?, ?, 'SUCCESS', ?, ?, ?)
                """ : """
                INSERT INTO audit_logs(actor_user_id, action, resource_type, resource_id, result, request_id, trace_id, metadata)
                VALUES (?, ?, ?, ?, 'SUCCESS', ?, ?, ?::jsonb)
                """;
        jdbcTemplate.update(sql, actorUserId, action, resourceType, resourceId, requestId, traceId, metadataJson);
    }

    private boolean detectH2(DataSource dataSource) {
        try (var connection = dataSource.getConnection()) {
            return connection.getMetaData().getDatabaseProductName().toLowerCase().contains("h2");
        } catch (Exception exception) {
            return false;
        }
    }
}
