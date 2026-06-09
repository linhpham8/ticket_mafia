package com.ticketmafia.match_inventory;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class SeatGenerationService {
    private final JdbcTemplate jdbcTemplate;
    private final MatchAdminService matchAdminService;
    private final AdminAuditService auditService;
    private final AdminIdempotencyService idempotencyService;

    SeatGenerationService(JdbcTemplate jdbcTemplate, MatchAdminService matchAdminService, AdminAuditService auditService,
                          AdminIdempotencyService idempotencyService) {
        this.jdbcTemplate = jdbcTemplate;
        this.matchAdminService = matchAdminService;
        this.auditService = auditService;
        this.idempotencyService = idempotencyService;
    }

    // Sprint: v1 | Feature: FR-007,BR-008,NFR-004 | US: US-007 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
    // Contract: api-specs-v1.md API-011; erd-v1.md ENT-003; sequence-v1.md SEQ-002
    @Transactional
    public SeatGenerationResponse generate(UUID actorUserId, UUID matchId, String sectionCode, Integer floorNo,
                                           Boolean isVip, Integer seatCount, String idempotencyKey, String requestId,
                                           String traceId) {
        if (!matchAdminService.matchExists(matchId)) {
            throw new ApiException(HttpStatus.NOT_FOUND, ErrorCode.MATCH_NOT_FOUND, "Match was not found.", "matchId");
        }
        InventorySlice slice = InventoryValidation.slice(sectionCode, floorNo, isVip,
                ErrorCode.SEAT_GENERATE_INVALID_REQUEST);
        int count = InventoryValidation.seatCount(seatCount);
        if (idempotencyService.findResource("ADMIN_SEATS_GENERATE", idempotencyKey, actorUserId).isPresent()) {
            return findGeneratedSeats(matchId, slice);
        }
        Integer existing = jdbcTemplate.queryForObject("""
                SELECT COUNT(*) FROM seats
                WHERE match_id = ? AND section_code = ? AND floor_no = ? AND is_vip = ?
                """, Integer.class, matchId, slice.sectionCode(), slice.floorNo(), slice.isVip());
        if (existing != null && existing > 0) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.SEATS_ALREADY_EXIST,
                    "Seats already exist for this inventory slice.", "sectionCode,floorNo,isVip");
        }
        List<UUID> seatIds = new ArrayList<>(count);
        List<String> seatCodes = new ArrayList<>(count);
        for (int index = 1; index <= count; index++) {
            UUID seatId = UUID.randomUUID();
            String seatCode = seatCode(slice, index);
            jdbcTemplate.update("""
                    INSERT INTO seats(id, match_id, section_code, floor_no, seat_code, is_vip, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'AVAILABLE')
                    """, seatId, matchId, slice.sectionCode(), slice.floorNo(), seatCode, slice.isVip());
            seatIds.add(seatId);
            seatCodes.add(seatCode);
        }
        auditService.record(actorUserId, "SEATS_GENERATED", "MATCH", matchId, requestId, traceId,
                "{\"section\":\"%s\",\"floor\":%d,\"isVip\":%s,\"count\":%d}"
                        .formatted(slice.sectionCode(), slice.floorNo(), slice.isVip(), count));
        idempotencyService.record("ADMIN_SEATS_GENERATE", idempotencyKey, actorUserId, matchId,
                ErrorCode.SEAT_GENERATE_INVALID_REQUEST);
        return new SeatGenerationResponse(count, seatIds, seatCodes);
    }

    static String seatCode(InventorySlice slice, int oneBasedIndex) {
        String prefix = slice.isVip() ? "VIP" : "T" + slice.floorNo();
        return "%s-%s-%03d".formatted(slice.sectionCode(), prefix, oneBasedIndex);
    }

    private SeatGenerationResponse findGeneratedSeats(UUID matchId, InventorySlice slice) {
        var seats = jdbcTemplate.query("""
                SELECT id, seat_code
                FROM seats
                WHERE match_id = ? AND section_code = ? AND floor_no = ? AND is_vip = ?
                ORDER BY seat_code
                """, (rs, rowNum) -> new SeatRecord(
                rs.getObject("id", UUID.class),
                rs.getString("seat_code")), matchId, slice.sectionCode(), slice.floorNo(), slice.isVip());
        return new SeatGenerationResponse(seats.size(), seats.stream().map(SeatRecord::id).toList(),
                seats.stream().map(SeatRecord::seatCode).toList());
    }

    public record SeatGenerationResponse(int generatedCount, List<UUID> seatIds, List<String> seatCodes) {
    }

    private record SeatRecord(UUID id, String seatCode) {
    }
}
