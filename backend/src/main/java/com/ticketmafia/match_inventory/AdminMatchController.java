package com.ticketmafia.match_inventory;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ApiResponse;
import com.ticketmafia.shared.ErrorCode;
import com.ticketmafia.shared.RequestTraceFilter;
import jakarta.servlet.http.HttpServletRequest;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/admin/matches")
public class AdminMatchController {
    private final AdminActor adminActor;
    private final MatchAdminService matchAdminService;
    private final SeatGenerationService seatGenerationService;
    private final PriceVersionService priceVersionService;

    AdminMatchController(AdminActor adminActor, MatchAdminService matchAdminService,
                         SeatGenerationService seatGenerationService, PriceVersionService priceVersionService) {
        this.adminActor = adminActor;
        this.matchAdminService = matchAdminService;
        this.seatGenerationService = seatGenerationService;
        this.priceVersionService = priceVersionService;
    }

    // Sprint: v1 | Feature: FR-006,BR-008,NFR-004 | US: US-006 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
    // Contract: api-specs-v1.md API-010 POST /api/v1/admin/matches; sequence-v1.md SEQ-002
    @PostMapping
    ApiResponse<MatchAdminService.MatchResponse> createMatch(
            @RequestHeader("Authorization") String authorization,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @RequestBody CreateMatchRequest request,
            HttpServletRequest servletRequest) {
        requireIdempotency(idempotencyKey, ErrorCode.ADMIN_MATCH_INVALID_REQUEST);
        UUID actorUserId = adminActor.requireAdminUser(authorization);
        return new ApiResponse<>(matchAdminService.createMatch(actorUserId, request.name(), parseInstant(request.startsAt()),
                parseStatus(request.status()), idempotencyKey, requestId(servletRequest), traceId(servletRequest)));
    }

    // Sprint: v1 | Feature: FR-007,BR-008,NFR-004 | US: US-007 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
    // Contract: api-specs-v1.md API-011 POST /api/v1/admin/matches/{matchId}/seats/generate; sequence-v1.md SEQ-002
    @PostMapping("/{matchId}/seats/generate")
    ApiResponse<SeatGenerationService.SeatGenerationResponse> generateSeats(
            @RequestHeader("Authorization") String authorization,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @PathVariable UUID matchId,
            @RequestBody GenerateSeatsRequest request,
            HttpServletRequest servletRequest) {
        requireIdempotency(idempotencyKey, ErrorCode.SEAT_GENERATE_INVALID_REQUEST);
        UUID actorUserId = adminActor.requireAdminUser(authorization);
        return new ApiResponse<>(seatGenerationService.generate(actorUserId, matchId, request.sectionCode(),
                request.floorNo(), request.isVip(), request.seatCount(), idempotencyKey, requestId(servletRequest),
                traceId(servletRequest)));
    }

    // Sprint: v1 | Feature: FR-007,BR-004,NFR-004 | US: US-007 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
    // Contract: api-specs-v1.md API-012 POST /api/v1/admin/matches/{matchId}/prices; AC-013/AC-014 future checkout snapshot rule
    @PostMapping("/{matchId}/prices")
    ApiResponse<PriceVersionService.PriceVersionResponse> setPrice(
            @RequestHeader("Authorization") String authorization,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @PathVariable UUID matchId,
            @RequestBody SetPriceRequest request,
            HttpServletRequest servletRequest) {
        requireIdempotency(idempotencyKey, ErrorCode.PRICE_INVALID_REQUEST);
        UUID actorUserId = adminActor.requireAdminUser(authorization);
        return new ApiResponse<>(priceVersionService.setPrice(actorUserId, matchId, request.sectionCode(),
                request.floorNo(), request.isVip(), request.priceVnd(), idempotencyKey, requestId(servletRequest),
                traceId(servletRequest)));
    }

    private void requireIdempotency(String idempotencyKey, ErrorCode errorCode) {
        if (idempotencyKey == null || idempotencyKey.isBlank() || idempotencyKey.length() > 120) {
            throw new ApiException(HttpStatus.BAD_REQUEST, errorCode,
                    "Idempotency-Key header is required for admin mutations.", "Idempotency-Key");
        }
    }

    private Instant parseInstant(String value) {
        // if (value == null || value.isBlank()) {
        //     return null;
        // }
        try {
            return Instant.parse(value);
        } catch (RuntimeException exception) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.ADMIN_MATCH_INVALID_REQUEST,
                    "startsAt must be an ISO UTC datetime.", "startsAt");
        }
    }

    private MatchStatus parseStatus(String value) {
        try {
            return MatchStatus.valueOf(value);
        } catch (RuntimeException exception) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.ADMIN_MATCH_INVALID_REQUEST,
                    "status must be one of the supported sale states.", "status");
        }
    }

    private String requestId(HttpServletRequest request) {
        return (String) request.getAttribute(RequestTraceFilter.REQUEST_ID_ATTRIBUTE);
    }

    private String traceId(HttpServletRequest request) {
        return (String) request.getAttribute(RequestTraceFilter.TRACE_ID_ATTRIBUTE);
    }

    record CreateMatchRequest(String name, String startsAt, String status) {
    }

    record GenerateSeatsRequest(String sectionCode, Integer floorNo, Boolean isVip, Integer seatCount) {
    }

    record SetPriceRequest(String sectionCode, Integer floorNo, Boolean isVip, BigDecimal priceVnd) {
    }
}
