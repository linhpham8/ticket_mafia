package com.ticketmafia.order_payment;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CheckoutService {
    private final JdbcTemplate jdbcTemplate;
    private final OrderIdempotencyService idempotencyService;
    private final Clock clock;
    private final Duration holdDuration;

    @Autowired
    CheckoutService(JdbcTemplate jdbcTemplate, OrderIdempotencyService idempotencyService,
                    @Value("${ticketing.hold.duration:PT10M}") Duration holdDuration) {
        this(jdbcTemplate, idempotencyService, Clock.systemUTC(), holdDuration);
    }

    CheckoutService(JdbcTemplate jdbcTemplate, OrderIdempotencyService idempotencyService, Clock clock,
                    Duration holdDuration) {
        this.jdbcTemplate = jdbcTemplate;
        this.idempotencyService = idempotencyService;
        this.clock = clock;
        this.holdDuration = holdDuration;
    }

    // Sprint: v1 | Feature: FR-004,BR-002,BR-003,BR-004,NFR-002 | US: US-004 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
    // Contract: api-specs-v1.md API-005; erd-v1.md ENT-004/ENT-005; sequence-v1.md SEQ-003 [TX BEGIN/COMMIT]
    @Transactional
    public CheckoutResponse checkout(UUID userId, UUID matchId, List<UUID> requestedSeatIds, String idempotencyKey) {
        requireIdempotency(idempotencyKey, ErrorCode.CHECKOUT_INVALID_REQUEST);
        List<UUID> seatIds = normalizedSeatIds(requestedSeatIds);
        String requestHash = requestHash(matchId, seatIds);
        var replay = idempotencyService.findResource("ORDER_CHECKOUT", idempotencyKey, requestHash, userId,
                        ErrorCode.CHECKOUT_INVALID_REQUEST)
                .flatMap(orderId -> findCheckout(orderId, userId));
        if (replay.isPresent()) {
            return replay.get();
        }
        assertMatchIsSellable(matchId);
        PaymentQr paymentQr = defaultPaymentQr();
        List<SeatSnapshot> seats = lockedAvailableSeats(matchId, seatIds);
        if (seats.size() != seatIds.size()) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.SEAT_UNAVAILABLE,
                    "One or more selected seats are no longer available.", "seatIds");
        }
        BigDecimal total = seats.stream().map(SeatSnapshot::priceSnapshotVnd)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        UUID orderId = UUID.randomUUID();
        Instant now = clock.instant();
        Instant holdExpiresAt = now.plus(holdDuration);
        jdbcTemplate.update("""
                INSERT INTO orders(id, user_id, match_id, type, status, total_amount_vnd, hold_expires_at, created_at, updated_at)
                VALUES (?, ?, ?, 'PURCHASE', 'HELD', ?, ?, ?, ?)
                """, orderId, userId, matchId, total, Timestamp.from(holdExpiresAt), Timestamp.from(now),
                Timestamp.from(now));
        List<CheckoutItem> items = new ArrayList<>(seats.size());
        for (SeatSnapshot seat : seats) {
            UUID itemId = UUID.randomUUID();
            try {
                jdbcTemplate.update("""
                        INSERT INTO order_items(id, order_id, seat_id, price_snapshot_vnd, active)
                        VALUES (?, ?, ?, ?, TRUE)
                        """, itemId, orderId, seat.id(), seat.priceSnapshotVnd());
            } catch (DuplicateKeyException exception) {
                throw new ApiException(HttpStatus.CONFLICT, ErrorCode.SEAT_UNAVAILABLE,
                        "Seat already has an active order item.", seat.id().toString());
            }
            int updated = jdbcTemplate.update("""
                    UPDATE seats
                    SET status = 'HELD', active_order_item_id = ?, updated_at = ?
                    WHERE id = ? AND status = 'AVAILABLE'
                    """, itemId, Timestamp.from(now), seat.id());
            if (updated != 1) {
                throw new ApiException(HttpStatus.CONFLICT, ErrorCode.SEAT_UNAVAILABLE,
                        "Seat was no longer available.", seat.id().toString());
            }
            items.add(new CheckoutItem(seat.id(), seat.seatCode(), seat.priceSnapshotVnd()));
        }
        idempotencyService.record("ORDER_CHECKOUT", idempotencyKey, requestHash, userId, orderId,
                ErrorCode.CHECKOUT_INVALID_REQUEST);
        return new CheckoutResponse(orderId, "HELD", holdExpiresAt, total, items, paymentQr);
    }

    private List<UUID> normalizedSeatIds(List<UUID> requestedSeatIds) {
        if (requestedSeatIds == null) {
            throw new ApiException(HttpStatus.UNPROCESSABLE_ENTITY, ErrorCode.CHECKOUT_LIMIT_EXCEEDED,
                    "Select 1 to 5 seats.", "seatIds");
        }
        List<UUID> unique = new ArrayList<>(new LinkedHashSet<>(requestedSeatIds));
        if (unique.isEmpty() || unique.size() > 5 || unique.size() != requestedSeatIds.size()) {
            throw new ApiException(HttpStatus.UNPROCESSABLE_ENTITY, ErrorCode.CHECKOUT_LIMIT_EXCEEDED,
                    "Select 1 to 5 distinct seats.", "seatIds");
        }
        return unique;
    }

    private void assertMatchIsSellable(UUID matchId) {
        String status = jdbcTemplate.query("""
                SELECT status
                FROM matches
                WHERE id = ?
                """, (rs, rowNum) -> rs.getString("status"), matchId).stream().findFirst()
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, ErrorCode.CHECKOUT_RESOURCE_NOT_FOUND,
                        "Match was not found.", "matchId"));
        if (!"OPEN_FOR_SALE".equals(status)) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.SEAT_UNAVAILABLE,
                    "Match is not open for checkout.", status);
        }
    }

    private PaymentQr defaultPaymentQr() {
        return jdbcTemplate.query("""
                SELECT qr_asset_ref
                FROM payment_qr_configs
                WHERE is_default = TRUE
                """, (rs, rowNum) -> new PaymentQr(rs.getString("qr_asset_ref")))
                .stream().findFirst()
                .orElseThrow(() -> new ApiException(HttpStatus.CONFLICT, ErrorCode.CHECKOUT_RESOURCE_NOT_FOUND,
                        "Default payment QR is not configured.", "paymentQr"));
    }

    private List<SeatSnapshot> lockedAvailableSeats(UUID matchId, List<UUID> seatIds) {
        return jdbcTemplate.query("""
                SELECT s.id, s.seat_code,
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
                WHERE s.match_id = ? AND s.status = 'AVAILABLE' AND s.id IN (%s)
                FOR UPDATE
                """.formatted(placeholders(seatIds.size())), this::mapSeatSnapshot, append(matchId, seatIds));
    }

    private java.util.Optional<CheckoutResponse> findCheckout(UUID orderId, UUID userId) {
        return jdbcTemplate.query("""
                SELECT o.id, o.status, o.hold_expires_at, o.total_amount_vnd, q.qr_asset_ref
                FROM orders o
                CROSS JOIN payment_qr_configs q
                WHERE o.id = ? AND o.user_id = ? AND q.is_default = TRUE
                """, (rs, rowNum) -> new CheckoutResponse(
                rs.getObject("id", UUID.class),
                rs.getString("status"),
                rs.getTimestamp("hold_expires_at").toInstant(),
                rs.getBigDecimal("total_amount_vnd"),
                findItems(orderId),
                new PaymentQr(rs.getString("qr_asset_ref"))), orderId, userId).stream().findFirst();
    }

    private List<CheckoutItem> findItems(UUID orderId) {
        return jdbcTemplate.query("""
                SELECT s.id, s.seat_code, oi.price_snapshot_vnd
                FROM order_items oi
                JOIN seats s ON s.id = oi.seat_id
                WHERE oi.order_id = ?
                ORDER BY s.seat_code
                """, (rs, rowNum) -> new CheckoutItem(
                rs.getObject("id", UUID.class),
                rs.getString("seat_code"),
                rs.getBigDecimal("price_snapshot_vnd")), orderId);
    }

    private SeatSnapshot mapSeatSnapshot(ResultSet rs, int rowNum) throws SQLException {
        BigDecimal price = rs.getBigDecimal("price_vnd");
        if (price == null || price.compareTo(BigDecimal.ZERO) <= 0) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.CHECKOUT_RESOURCE_NOT_FOUND,
                    "Active price is not configured for selected seat.", rs.getObject("id", UUID.class).toString());
        }
        return new SeatSnapshot(rs.getObject("id", UUID.class), rs.getString("seat_code"), price);
    }

    private void requireIdempotency(String idempotencyKey, ErrorCode errorCode) {
        if (idempotencyKey == null || idempotencyKey.isBlank() || idempotencyKey.length() > 120) {
            throw new ApiException(HttpStatus.BAD_REQUEST, errorCode,
                    "Idempotency-Key header is required for order mutations.", "Idempotency-Key");
        }
    }

    private String placeholders(int size) {
        return String.join(",", java.util.Collections.nCopies(size, "?"));
    }

    private Object[] append(UUID matchId, List<UUID> seatIds) {
        Object[] args = new Object[seatIds.size() + 1];
        args[0] = matchId;
        for (int i = 0; i < seatIds.size(); i++) {
            args[i + 1] = seatIds.get(i);
        }
        return args;
    }

    private String requestHash(UUID matchId, List<UUID> seatIds) {
        String canonical = "matchId=%s;seatIds=%s".formatted(matchId,
                seatIds.stream().map(UUID::toString).sorted().toList());
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(canonical.getBytes(StandardCharsets.UTF_8));
            return java.util.HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 is required for checkout idempotency.", exception);
        }
    }

    public record CheckoutResponse(UUID orderId, String status, Instant holdExpiresAt, BigDecimal totalAmountVnd,
                                   List<CheckoutItem> items, PaymentQr paymentQr) {
    }

    public record CheckoutItem(UUID seatId, String seatCode, BigDecimal priceSnapshotVnd) {
    }

    public record PaymentQr(String assetRef) {
    }

    private record SeatSnapshot(UUID id, String seatCode, BigDecimal priceSnapshotVnd) {
    }
}
