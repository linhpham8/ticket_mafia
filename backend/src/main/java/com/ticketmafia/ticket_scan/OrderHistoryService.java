package com.ticketmafia.ticket_scan;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class OrderHistoryService {
    private static final int DEFAULT_LIMIT = 20;
    private static final int MAX_LIMIT = 50;
    private final JdbcTemplate jdbcTemplate;

    OrderHistoryService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    // Sprint: v1 | Feature: FR-009,BR-001 | US: US-009 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
    // Contract: api-specs-v1.md API-008 GET /api/v1/orders; project-reference-v1.md PR-004/PR-005 ownership boundary
    public HistoryPage list(UUID userId, String status, String cursor, Integer limit) {
        int normalizedLimit = normalizeLimit(limit);
        String normalizedStatus = normalizeStatus(status);
        Cursor decodedCursor = decodeCursor(cursor);
        List<OrderPageRow> pageRows = queryOrderPage(userId, normalizedStatus, decodedCursor, normalizedLimit + 1);
        boolean hasNext = pageRows.size() > normalizedLimit;
        List<OrderPageRow> returnedOrders = hasNext ? pageRows.subList(0, normalizedLimit) : pageRows;
        Map<UUID, MutableOrderHistoryRow> grouped = new LinkedHashMap<>();
        for (OrderPageRow row : returnedOrders) {
            grouped.put(row.orderId(), new MutableOrderHistoryRow(row.orderId(), row.status(), row.matchName(),
                    row.totalAmountVnd(), row.createdAt(), new java.util.ArrayList<>()));
        }
        for (HistoryTicketRow row : queryTicketsFor(returnedOrders)) {
            MutableOrderHistoryRow order = grouped.get(row.orderId());
            if (row.ticketId() != null) {
                order.tickets().add(new TicketSummary(row.ticketId(), row.ticketStatus(), row.seatCode()));
            }
        }
        String nextCursor = hasNext && !returnedOrders.isEmpty()
                ? encodeCursor(returnedOrders.get(returnedOrders.size() - 1))
                : null;
        return new HistoryPage(grouped.values().stream().map(MutableOrderHistoryRow::toResponse).toList(),
                new PageMeta(nextCursor));
    }

    private List<OrderPageRow> queryOrderPage(UUID userId, String status, Cursor cursor, int limit) {
        String statusPredicate = status == null ? "" : """
                 AND (o.status = ? OR EXISTS (
                   SELECT 1 FROM tickets tx WHERE tx.order_id = o.id AND tx.status = ?
                 ))
                """;
        String cursorPredicate = cursor == null ? "" : """
                 AND (o.created_at < ? OR (o.created_at = ? AND o.id > ?))
                """;
        String sql = """
                SELECT o.id order_id, o.status order_status, m.name match_name, o.total_amount_vnd, o.created_at
                FROM orders o
                JOIN matches m ON m.id = o.match_id
                WHERE o.user_id = ?
                %s
                %s
                ORDER BY o.created_at DESC, o.id
                LIMIT ?
                """.formatted(statusPredicate, cursorPredicate);
        List<Object> args = new java.util.ArrayList<>();
        args.add(userId);
        if (status != null) {
            args.add(status);
            args.add(status);
        }
        if (cursor != null) {
            args.add(Timestamp.from(cursor.createdAt()));
            args.add(Timestamp.from(cursor.createdAt()));
            args.add(cursor.orderId());
        }
        args.add(limit);

        return jdbcTemplate.query(sql, (rs, rowNum) -> new OrderPageRow(
                rs.getObject("order_id", UUID.class),
                rs.getString("order_status"),
                rs.getString("match_name"),
                rs.getBigDecimal("total_amount_vnd"),
                rs.getTimestamp("created_at").toInstant()), args.toArray());
    }

    private List<HistoryTicketRow> queryTicketsFor(List<OrderPageRow> orders) {
        if (orders.isEmpty()) {
            return List.of();
        }
        String placeholders = orders.stream().map(ignored -> "?").collect(java.util.stream.Collectors.joining(","));
        String sql = """
                SELECT t.order_id, t.id ticket_id, t.status ticket_status, s.seat_code
                FROM tickets t
                JOIN seats s ON s.id = t.seat_id
                WHERE t.order_id IN (%s)
                ORDER BY t.order_id, t.issued_at, t.id
                """.formatted(placeholders);
        Object[] args = orders.stream().map(OrderPageRow::orderId).toArray();
        return jdbcTemplate.query(sql, (rs, rowNum) -> new HistoryTicketRow(
                rs.getObject("order_id", UUID.class),
                rs.getObject("ticket_id", UUID.class),
                rs.getString("ticket_status"),
                rs.getString("seat_code")), args);
    }

    private int normalizeLimit(Integer limit) {
        int normalized = limit == null ? DEFAULT_LIMIT : limit;
        if (normalized < 1 || normalized > MAX_LIMIT) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.ORDER_QUERY_INVALID,
                    "limit must be between 1 and 50.", "limit");
        }
        return normalized;
    }

    private Cursor decodeCursor(String cursor) {
        if (cursor == null || cursor.isBlank()) {
            return null;
        }
        try {
            String decoded = new String(Base64.getUrlDecoder().decode(cursor), StandardCharsets.UTF_8);
            String[] parts = decoded.split("\\|", 2);
            return new Cursor(Instant.parse(parts[0]), UUID.fromString(parts[1]));
        } catch (RuntimeException exception) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.ORDER_QUERY_INVALID,
                    "cursor is invalid.", "cursor");
        }
    }

    private String encodeCursor(OrderPageRow row) {
        String raw = row.createdAt() + "|" + row.orderId();
        return Base64.getUrlEncoder().withoutPadding().encodeToString(raw.getBytes(StandardCharsets.UTF_8));
    }

    private String normalizeStatus(String status) {
        if (status == null || status.isBlank()) {
            return null;
        }
        String normalized = status.toUpperCase(Locale.ROOT);
        List<String> allowed = List.of("HELD", "PENDING_ADMIN_CONFIRM", "ISSUED", "REJECTED", "CANCELLED",
                "EXPIRED", "USED_SCANNED", "EXCHANGED");
        if (!allowed.contains(normalized)) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.ORDER_QUERY_INVALID,
                    "status is not a valid order or ticket status.", "status");
        }
        return normalized;
    }

    public record HistoryPage(List<OrderHistoryRow> data, PageMeta meta) {
    }

    public record PageMeta(String nextCursor) {
    }

    public record OrderHistoryRow(UUID orderId, String status, String matchName, BigDecimal totalAmountVnd,
                                  Instant createdAt, List<TicketSummary> tickets) {
    }

    public record TicketSummary(UUID ticketId, String status, String seatCode) {
    }

    private record MutableOrderHistoryRow(UUID orderId, String status, String matchName, BigDecimal totalAmountVnd,
                                          Instant createdAt, List<TicketSummary> tickets) {
        OrderHistoryRow toResponse() {
            return new OrderHistoryRow(orderId, status, matchName, totalAmountVnd, createdAt, List.copyOf(tickets));
        }
    }

    private record OrderPageRow(UUID orderId, String status, String matchName, BigDecimal totalAmountVnd,
                                Instant createdAt) {
    }

    private record HistoryTicketRow(UUID orderId, UUID ticketId, String ticketStatus, String seatCode) {
    }

    private record Cursor(Instant createdAt, UUID orderId) {
    }
}
