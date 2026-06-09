package com.ticketmafia.match_inventory;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.math.BigDecimal;
import java.sql.Timestamp;
import java.time.Clock;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class PriceVersionService {
    private final JdbcTemplate jdbcTemplate;
    private final MatchAdminService matchAdminService;
    private final AdminAuditService auditService;
    private final AdminIdempotencyService idempotencyService;
    private final Clock clock;

    @Autowired
    PriceVersionService(JdbcTemplate jdbcTemplate, MatchAdminService matchAdminService, AdminAuditService auditService,
                        AdminIdempotencyService idempotencyService) {
        this(jdbcTemplate, matchAdminService, auditService, idempotencyService, Clock.systemUTC());
    }

    PriceVersionService(JdbcTemplate jdbcTemplate, MatchAdminService matchAdminService, AdminAuditService auditService,
                        AdminIdempotencyService idempotencyService, Clock clock) {
        this.jdbcTemplate = jdbcTemplate;
        this.matchAdminService = matchAdminService;
        this.auditService = auditService;
        this.idempotencyService = idempotencyService;
        this.clock = clock;
    }

    // Sprint: v1 | Feature: FR-007,BR-004,NFR-004 | US: US-007 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
    // Contract: api-specs-v1.md API-012; erd-v1.md ENT-006 append-only price_versions; AC-013/AC-014 snapshot source
    @Transactional
    public PriceVersionResponse setPrice(UUID actorUserId, UUID matchId, String sectionCode, Integer floorNo,
                                         Boolean isVip, BigDecimal priceVnd, String idempotencyKey, String requestId,
                                         String traceId) {
        var replay = idempotencyService.findResource("ADMIN_PRICE_SET", idempotencyKey, actorUserId)
                .flatMap(this::findPriceVersion);
        if (replay.isPresent()) {
            return replay.get();
        }
        MatchStatus status = matchAdminService.findStatus(matchId);
        if (status == MatchStatus.CANCELLED || status == MatchStatus.CLOSED) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.MATCH_PRICE_LOCKED,
                    "Price cannot be changed for a closed or cancelled match.", status.name());
        }
        InventorySlice slice = InventoryValidation.slice(sectionCode, floorNo, isVip, ErrorCode.PRICE_INVALID_REQUEST);
        BigDecimal price = InventoryValidation.price(priceVnd);
        UUID priceVersionId = UUID.randomUUID();
        Instant activeFrom = clock.instant();
        jdbcTemplate.update("""
                INSERT INTO price_versions(id, match_id, section_code, floor_no, is_vip, price_vnd, active_from, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, priceVersionId, matchId, slice.sectionCode(), slice.floorNo(), slice.isVip(), price,
                Timestamp.from(activeFrom), actorUserId);
        auditService.record(actorUserId, "PRICE_VERSION_CREATED", "MATCH", matchId, requestId, traceId,
                "{\"section\":\"%s\",\"floor\":%d,\"isVip\":%s,\"priceVnd\":%s}"
                        .formatted(slice.sectionCode(), slice.floorNo(), slice.isVip(), price.toPlainString()));
        idempotencyService.record("ADMIN_PRICE_SET", idempotencyKey, actorUserId, priceVersionId,
                ErrorCode.PRICE_INVALID_REQUEST);
        return new PriceVersionResponse(priceVersionId, activeFrom);
    }

    Optional<BigDecimal> latestPrice(UUID matchId, String sectionCode, int floorNo, boolean isVip) {
        return jdbcTemplate.query("""
                SELECT price_vnd
                FROM price_versions
                WHERE match_id = ? AND section_code = ? AND floor_no = ? AND is_vip = ?
                ORDER BY active_from DESC, created_at DESC
                LIMIT 1
                """, (rs, rowNum) -> rs.getBigDecimal("price_vnd"), matchId, sectionCode, floorNo, isVip)
                .stream().findFirst();
    }

    private Optional<PriceVersionResponse> findPriceVersion(UUID priceVersionId) {
        return jdbcTemplate.query("""
                SELECT id, active_from
                FROM price_versions
                WHERE id = ?
                """, (rs, rowNum) -> new PriceVersionResponse(
                rs.getObject("id", UUID.class),
                rs.getTimestamp("active_from").toInstant()), priceVersionId).stream().findFirst();
    }

    public record PriceVersionResponse(UUID priceVersionId, Instant activeFrom) {
    }
}
