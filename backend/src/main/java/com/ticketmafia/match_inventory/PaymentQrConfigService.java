package com.ticketmafia.match_inventory;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.util.Optional;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
class PaymentQrConfigService {
    private final JdbcTemplate jdbcTemplate;
    private final AdminAuditService auditService;
    private final AdminIdempotencyService idempotencyService;

    PaymentQrConfigService(JdbcTemplate jdbcTemplate, AdminAuditService auditService,
                           AdminIdempotencyService idempotencyService) {
        this.jdbcTemplate = jdbcTemplate;
        this.auditService = auditService;
        this.idempotencyService = idempotencyService;
    }

    // Sprint: v1 | Feature: FR-007,BR-004,NFR-004 | US: US-007 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
    // Contract: erd-v1.md ENT-007 one-default QR invariant; sequence-v1.md SEQ-002 payment_qr_configs
    @Transactional
    QrConfigResponse setDefault(UUID actorUserId, String name, String qrAssetRef, String idempotencyKey,
                                String requestId, String traceId) {
        var replay = idempotencyService.findResource("ADMIN_QR_DEFAULT_SET", idempotencyKey, actorUserId)
                .flatMap(this::findQrConfig);
        if (replay.isPresent()) {
            return replay.get();
        }
        String normalizedName = Optional.ofNullable(name).map(String::trim).orElse("");
        String normalizedAsset = Optional.ofNullable(qrAssetRef).map(String::trim).orElse("");
        if (normalizedName.isBlank() || normalizedName.length() > 80 || normalizedAsset.isBlank()) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.QR_CONFIG_INVALID_REQUEST,
                    "QR name and asset reference are required.", "name,qrAssetRef");
        }
        jdbcTemplate.update("UPDATE payment_qr_configs SET is_default = FALSE, updated_at = NOW() WHERE is_default = TRUE");
        UUID id = UUID.randomUUID();
        jdbcTemplate.update("""
                INSERT INTO payment_qr_configs(id, name, qr_asset_ref, is_default, created_by)
                VALUES (?, ?, ?, TRUE, ?)
                """, id, normalizedName, normalizedAsset, actorUserId);
        idempotencyService.record("ADMIN_QR_DEFAULT_SET", idempotencyKey, actorUserId, id,
                ErrorCode.QR_CONFIG_INVALID_REQUEST);
        auditService.record(actorUserId, "PAYMENT_QR_DEFAULT_SET", "PAYMENT_QR_CONFIG", id, requestId, traceId,
                "{\"name\":\"%s\"}".formatted(normalizedName.replace("\"", "")));
        return new QrConfigResponse(id, normalizedName, normalizedAsset, true);
    }

    int defaultCount() {
        Integer count = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM payment_qr_configs WHERE is_default = TRUE",
                Integer.class);
        return count == null ? 0 : count;
    }

    record QrConfigResponse(UUID id, String name, String qrAssetRef, boolean isDefault) {
    }

    private Optional<QrConfigResponse> findQrConfig(UUID id) {
        return jdbcTemplate.query("""
                SELECT id, name, qr_asset_ref, is_default
                FROM payment_qr_configs
                WHERE id = ?
                """, (rs, rowNum) -> new QrConfigResponse(
                rs.getObject("id", UUID.class),
                rs.getString("name"),
                rs.getString("qr_asset_ref"),
                rs.getBoolean("is_default")), id).stream().findFirst();
    }
}
