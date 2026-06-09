package com.ticketmafia.audit;

import java.util.UUID;
import javax.sql.DataSource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class AuditService {
    private final JdbcTemplate jdbcTemplate;
    private final boolean h2;

    public AuditService(JdbcTemplate jdbcTemplate, DataSource dataSource) {
        this.jdbcTemplate = jdbcTemplate;
        this.h2 = detectH2(dataSource);
    }

    // Sprint: v1 | Feature: FR-008,NFR-004 | US: US-008 | Task Group: TG 1.4 Admin Payment Confirmation and Audit
    // Contract: erd-v1.md ENT-010; sequence-v1.md SEQ-004 inserts audit_logs inside the decision transaction
    public void recordSuccess(UUID actorUserId, String action, String resourceType, UUID resourceId, String requestId,
                              String traceId, String metadataJson) {
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
