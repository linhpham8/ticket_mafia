package com.ticketmafia.match_inventory;

import com.ticketmafia.shared.ApiResponse;
import com.ticketmafia.shared.PaginatedApiResponse;
import java.util.List;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/matches")
public class MatchBrowseController {
    private final MatchBrowseService matchBrowseService;

    MatchBrowseController(MatchBrowseService matchBrowseService) {
        this.matchBrowseService = matchBrowseService;
    }

    // Sprint: v1 | Feature: FR-002 | US: US-002 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
    // Contract: api-specs-v1.md API-003 GET /api/v1/matches; project-reference-v1.md PR-003
    @GetMapping
    PaginatedApiResponse<List<MatchBrowseService.MatchRow>, MatchBrowseService.MatchListMeta> listMatches(
            @RequestParam(defaultValue = "OPEN_FOR_SALE") String status,
            @RequestParam(required = false) String cursor,
            @RequestParam(defaultValue = "20") int limit) {
        MatchBrowseService.MatchListPage page = matchBrowseService.listOpenMatches(status, cursor, limit);
        return new PaginatedApiResponse<>(page.data(), page.meta());
    }

    // Sprint: v1 | Feature: FR-003,BR-003 | US: US-003 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
    // Contract: api-specs-v1.md API-004 GET /api/v1/matches/{matchId}/seats; erd-v1.md ENT-003/ENT-006
    @GetMapping("/{matchId}/seats")
    ApiResponse<MatchBrowseService.SeatMapResponse> seatMap(
            @PathVariable UUID matchId,
            @RequestParam(required = false) String section,
            @RequestParam(required = false) Integer floorNo) {
        return new ApiResponse<>(matchBrowseService.seatMap(matchId, section, floorNo));
    }
}
