package com.ticketmafia.match_inventory;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.math.BigDecimal;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class MatchBrowseService {
    private final JdbcTemplate jdbcTemplate;

    MatchBrowseService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    // Sprint: v1 | Feature: FR-002 | US: US-002 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
    // Contract: api-specs-v1.md API-003; erd-v1.md ENT-002; sequence-v1.md SEQ-002 public browsing path
    public MatchListPage listOpenMatches(String status, String cursor, int limit) {
        if (!"OPEN_FOR_SALE".equals(status) || limit < 1 || limit > 50) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.MATCH_QUERY_INVALID,
                    "Only OPEN_FOR_SALE matches can be listed publicly with limit 1-50.", "status,limit");
        }
        int offset = decodeOffset(cursor);
        List<MatchRow> rows = jdbcTemplate.query("""
                SELECT id, name, starts_at, status
                FROM matches
                WHERE status = 'OPEN_FOR_SALE'
                ORDER BY starts_at NULLS LAST, created_at DESC
                LIMIT ?
                OFFSET ?
                """, this::mapMatch, limit + 1, offset);
        String nextCursor = rows.size() > limit ? encodeOffset(offset + limit) : null;
        List<MatchRow> pageRows = rows.size() > limit ? rows.subList(0, limit) : rows;
        return new MatchListPage(pageRows, new MatchListMeta(nextCursor));
    }

    // Sprint: v1 | Feature: FR-003,BR-003,BR-004 | US: US-003 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
    // Contract: api-specs-v1.md API-004; erd-v1.md ENT-003/ENT-006 current seat state and active price
    public SeatMapResponse seatMap(UUID matchId, String section, Integer floorNo) {
        MatchSummary match = findSellableMatch(matchId);
        if (section != null && !section.matches("[ABCD]")) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.SEAT_QUERY_INVALID,
                    "section must be A, B, C, or D.", "section");
        }
        if (floorNo != null && floorNo != 1 && floorNo != 2) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.SEAT_QUERY_INVALID,
                    "floorNo must be 1 or 2.", "floorNo");
        }
        Object[] args = section == null && floorNo == null ? new Object[]{matchId}
                : section != null && floorNo == null ? new Object[]{matchId, section}
                : section == null ? new Object[]{matchId, floorNo}
                : new Object[]{matchId, section, floorNo};
        String filter = section == null && floorNo == null ? ""
                : section != null && floorNo == null ? " AND s.section_code = ?"
                : section == null ? " AND s.floor_no = ?"
                : " AND s.section_code = ? AND s.floor_no = ?";
        List<SeatRow> seats = jdbcTemplate.query("""
                SELECT s.id, s.seat_code, s.section_code, s.floor_no, s.is_vip, s.status,
                       COALESCE((
                         SELECT pv.price_vnd
                         FROM price_versions pv
                         WHERE pv.match_id = s.match_id
                           AND pv.section_code = s.section_code
                           AND pv.floor_no = s.floor_no
                           AND pv.is_vip = s.is_vip
                         ORDER BY pv.active_from DESC, pv.created_at DESC
                         LIMIT 1
                       ), 0) AS price_vnd
                FROM seats s
                WHERE s.match_id = ?%s
                ORDER BY s.section_code, s.floor_no, s.is_vip DESC, s.seat_code
                """.formatted(filter), this::mapSeat, args);
        return new SeatMapResponse(match, seats);
    }

    private MatchSummary findSellableMatch(UUID matchId) {
        return jdbcTemplate.query("""
                SELECT id, status
                FROM matches
                WHERE id = ?
                """, (rs, rowNum) -> new MatchSummary(rs.getObject("id", UUID.class), rs.getString("status")),
                matchId).stream().findFirst()
                .map(match -> {
                    if (!"OPEN_FOR_SALE".equals(match.status())) {
                        throw new ApiException(HttpStatus.CONFLICT, ErrorCode.MATCH_NOT_SELLABLE,
                                "Match is not open for sale.", match.status());
                    }
                    return match;
                })
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, ErrorCode.MATCH_NOT_FOUND,
                        "Match was not found.", "matchId"));
    }

    private MatchRow mapMatch(ResultSet rs, int rowNum) throws SQLException {
        return new MatchRow(
                rs.getObject("id", UUID.class),
                rs.getString("name"),
                rs.getTimestamp("starts_at") == null ? null : rs.getTimestamp("starts_at").toInstant(),
                rs.getString("status"));
    }

    private SeatRow mapSeat(ResultSet rs, int rowNum) throws SQLException {
        return new SeatRow(
                rs.getObject("id", UUID.class),
                rs.getString("seat_code"),
                rs.getString("section_code"),
                rs.getInt("floor_no"),
                rs.getBoolean("is_vip"),
                rs.getString("status"),
                rs.getBigDecimal("price_vnd"));
    }

    public record MatchRow(UUID id, String name, Instant startsAt, String status) {
    }

    public record SeatMapResponse(MatchSummary match, List<SeatRow> seats) {
    }

    public record MatchSummary(UUID id, String status) {
    }

    public record SeatRow(UUID id, String seatCode, String sectionCode, int floorNo, boolean isVip, String status,
                          BigDecimal priceVnd) {
    }

    private int decodeOffset(String cursor) {
        if (cursor == null || cursor.isBlank()) {
            return 0;
        }
        try {
            String decoded = new String(Base64.getUrlDecoder().decode(cursor), StandardCharsets.UTF_8);
            int offset = Integer.parseInt(decoded);
            if (offset < 0) {
                throw new NumberFormatException("negative cursor");
            }
            return offset;
        } catch (IllegalArgumentException exception) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.MATCH_QUERY_INVALID,
                    "cursor must be an opaque cursor returned by the match list endpoint.", "cursor");
        }
    }

    private String encodeOffset(int offset) {
        return Base64.getUrlEncoder().withoutPadding()
                .encodeToString(Integer.toString(offset).getBytes(StandardCharsets.UTF_8));
    }

    public record MatchListPage(List<MatchRow> data, MatchListMeta meta) {
    }

    public record MatchListMeta(String nextCursor) {
    }
}
