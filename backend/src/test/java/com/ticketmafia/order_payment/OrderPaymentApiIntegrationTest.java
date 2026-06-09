package com.ticketmafia.order_payment;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.nullValue;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.blankOrNullString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.jayway.jsonpath.JsonPath;
import java.math.BigDecimal;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class OrderPaymentApiIntegrationTest {
    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private ExpiredHoldReleaseService expiredHoldReleaseService;

    private UUID adminId;
    private UUID matchId;
    private UUID secondMatchId;
    private String customerToken;
    private String otherCustomerToken;
    private UUID customerId;
    private UUID otherCustomerId;
    private UUID seatOneId;
    private UUID seatTwoId;

    @BeforeEach
    void setUp() {
        jdbcTemplate.update("DELETE FROM audit_logs");
        jdbcTemplate.update("DELETE FROM tickets");
        jdbcTemplate.update("DELETE FROM order_items");
        jdbcTemplate.update("DELETE FROM orders");
        jdbcTemplate.update("DELETE FROM payment_qr_configs");
        jdbcTemplate.update("DELETE FROM price_versions");
        jdbcTemplate.update("DELETE FROM seats");
        jdbcTemplate.update("DELETE FROM matches");
        jdbcTemplate.update("DELETE FROM sessions");
        jdbcTemplate.update("DELETE FROM idempotency_records");
        jdbcTemplate.update("DELETE FROM users");
        UserSession admin = insertUser("admin-order@example.test", "ADMIN");
        adminId = admin.userId();
        UserSession customer = insertUser("fan-order@example.test", "CUSTOMER");
        customerId = customer.userId();
        customerToken = customer.token();
        UserSession otherCustomer = insertUser("other-fan-order@example.test", "CUSTOMER");
        otherCustomerId = otherCustomer.userId();
        otherCustomerToken = otherCustomer.token();
        seedMatchInventory();
    }

    @Test
    void matchListAndSeatMapExposeOnlySellableInventoryWithCurrentPrice() throws Exception {
        MvcResult firstPage = mockMvc.perform(get("/api/v1/matches").param("limit", "1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data", hasSize(1)))
                .andExpect(jsonPath("$.data[0].id").value(matchId.toString()))
                .andExpect(jsonPath("$.data[0].status").value("OPEN_FOR_SALE"))
                .andExpect(jsonPath("$.meta.nextCursor", not(blankOrNullString())))
                .andReturn();

        String nextCursor = readJson(firstPage, "$.meta.nextCursor");
        mockMvc.perform(get("/api/v1/matches").param("limit", "1").param("cursor", nextCursor))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data", hasSize(1)))
                .andExpect(jsonPath("$.data[0].id").value(secondMatchId.toString()))
                .andExpect(jsonPath("$.meta.nextCursor").value(nullValue()));

        mockMvc.perform(get("/api/v1/matches/{matchId}/seats", matchId)
                        .param("section", "A")
                        .param("floorNo", "1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.match.status").value("OPEN_FOR_SALE"))
                .andExpect(jsonPath("$.data.seats", hasSize(2)))
                .andExpect(jsonPath("$.data.seats[0].priceVnd").value(120000.00));
    }

    @Test
    void checkoutHoldsSeatsSnapshotsPriceAndReplaysIdempotencyKey() throws Exception {
        MvcResult first = checkout(customerToken, "checkout-key-1", List.of(seatOneId, seatTwoId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.orderId", not(blankOrNullString())))
                .andExpect(jsonPath("$.data.status").value("HELD"))
                .andExpect(jsonPath("$.data.items", hasSize(2)))
                .andExpect(jsonPath("$.data.totalAmountVnd").value(240000.00))
                .andExpect(jsonPath("$.data.paymentQr.assetRef").value("asset://payment/default"))
                .andReturn();

        String orderId = readJson(first, "$.data.orderId");
        checkout(customerToken, "checkout-key-1", List.of(seatOneId, seatTwoId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.orderId").value(orderId));

        checkout(customerToken, "checkout-key-1", List.of(seatOneId))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.error.code").value("CHECKOUT_INVALID_REQUEST"));

        assertThat(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM orders", Integer.class)).isEqualTo(1);
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, seatOneId))
                .isEqualTo("HELD");
    }

    @Test
    void checkoutBlocksSixSeatsAndUnavailableSeats() throws Exception {
        List<UUID> sixSeats = List.of(seatOneId, seatTwoId, UUID.randomUUID(), UUID.randomUUID(), UUID.randomUUID(),
                UUID.randomUUID());
        checkout(customerToken, "checkout-too-many", sixSeats)
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.error.code").value("CHECKOUT_LIMIT_EXCEEDED"));

        checkout(customerToken, "checkout-key-2", List.of(seatOneId)).andExpect(status().isOk());
        checkout(otherCustomerToken, "checkout-key-3", List.of(seatOneId))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.error.code").value("SEAT_UNAVAILABLE"));
    }

    @Test
    void paymentCompletionMovesHeldOrderToPendingAndRequiresOwnership() throws Exception {
        String orderId = readJson(checkout(customerToken, "checkout-key-4", List.of(seatOneId))
                .andExpect(status().isOk()).andReturn(), "$.data.orderId");

        mockMvc.perform(post("/api/v1/orders/{orderId}/payment-completed", orderId)
                        .header("Authorization", "Bearer " + otherCustomerToken)
                        .header("Idempotency-Key", "pay-other")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error.code").value("ORDER_FORBIDDEN"));

        mockMvc.perform(post("/api/v1/orders/{orderId}/payment-completed", orderId)
                        .header("Authorization", "Bearer " + customerToken)
                        .header("Idempotency-Key", "pay-complete-1")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("PENDING_ADMIN_CONFIRM"))
                .andExpect(jsonPath("$.data.adminConfirmExpiresAt", not(blankOrNullString())));

        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, seatOneId))
                .isEqualTo("PENDING_ADMIN_CONFIRM");
    }

    @Test
    void releaseExpiredHoldsReturnsSeatsToAvailable() throws Exception {
        String orderId = readJson(checkout(customerToken, "checkout-expire", List.of(seatOneId))
                .andExpect(status().isOk()).andReturn(), "$.data.orderId");
        jdbcTemplate.update("""
                UPDATE orders
                SET hold_expires_at = ?
                WHERE id = ?
                """, Timestamp.from(Instant.now().minusSeconds(60)), UUID.fromString(orderId));

        assertThat(expiredHoldReleaseService.releaseExpiredHolds()).isEqualTo(1);

        assertThat(jdbcTemplate.queryForObject("SELECT status FROM orders WHERE id = ?", String.class,
                UUID.fromString(orderId))).isEqualTo("EXPIRED");
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, seatOneId))
                .isEqualTo("AVAILABLE");
        assertThat(jdbcTemplate.queryForObject("SELECT active FROM order_items WHERE order_id = ?", Boolean.class,
                UUID.fromString(orderId))).isFalse();
    }

    private org.springframework.test.web.servlet.ResultActions checkout(String token, String idempotencyKey,
                                                                       List<UUID> seatIds) throws Exception {
        String seats = seatIds.stream().map(UUID::toString).map(id -> "\"" + id + "\"")
                .collect(java.util.stream.Collectors.joining(","));
        return mockMvc.perform(post("/api/v1/orders/checkout")
                .header("Authorization", "Bearer " + token)
                .header("Idempotency-Key", idempotencyKey)
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"matchId\":\"%s\",\"seatIds\":[%s]}".formatted(matchId, seats)));
    }

    private void seedMatchInventory() {
        Instant now = Instant.now();
        matchId = UUID.randomUUID();
        secondMatchId = UUID.randomUUID();
        jdbcTemplate.update("""
                INSERT INTO matches(id, name, starts_at, status, created_at, updated_at)
                VALUES (?, 'TG 1.3 Match', ?, 'OPEN_FOR_SALE', ?, ?)
                """, matchId, Timestamp.from(now.plusSeconds(86_400)), Timestamp.from(now), Timestamp.from(now));
        jdbcTemplate.update("""
                INSERT INTO matches(id, name, starts_at, status, created_at, updated_at)
                VALUES (?, 'TG 1.3 Match Page Two', ?, 'OPEN_FOR_SALE', ?, ?)
                """, secondMatchId, Timestamp.from(now.plusSeconds(172_800)), Timestamp.from(now), Timestamp.from(now));
        seatOneId = insertSeat("A-T1-001");
        seatTwoId = insertSeat("A-T1-002");
        jdbcTemplate.update("""
                INSERT INTO price_versions(id, match_id, section_code, floor_no, is_vip, price_vnd, active_from, created_by)
                VALUES (?, ?, 'A', 1, FALSE, 100000, ?, ?)
                """, UUID.randomUUID(), matchId, Timestamp.from(now.minusSeconds(60)), adminId);
        jdbcTemplate.update("""
                INSERT INTO price_versions(id, match_id, section_code, floor_no, is_vip, price_vnd, active_from, created_by)
                VALUES (?, ?, 'A', 1, FALSE, 120000, ?, ?)
                """, UUID.randomUUID(), matchId, Timestamp.from(now), adminId);
        jdbcTemplate.update("""
                INSERT INTO payment_qr_configs(id, name, qr_asset_ref, is_default, created_by)
                VALUES (?, 'Default QR', 'asset://payment/default', TRUE, ?)
                """, UUID.randomUUID(), adminId);
        jdbcTemplate.update("""
                INSERT INTO matches(id, name, status, created_at, updated_at)
                VALUES (?, 'Closed Match', 'CLOSED', ?, ?)
                """, UUID.randomUUID(), Timestamp.from(now), Timestamp.from(now));
    }

    private UUID insertSeat(String seatCode) {
        UUID seatId = UUID.randomUUID();
        jdbcTemplate.update("""
                INSERT INTO seats(id, match_id, section_code, floor_no, seat_code, is_vip, status)
                VALUES (?, ?, 'A', 1, ?, FALSE, 'AVAILABLE')
                """, seatId, matchId, seatCode);
        return seatId;
    }

    private UserSession insertUser(String identifier, String role) {
        UUID userId = UUID.randomUUID();
        String token = UUID.randomUUID().toString();
        Instant now = Instant.now();
        jdbcTemplate.update("""
                INSERT INTO users(id, identifier, identifier_type, role, status, created_at, updated_at)
                VALUES (?, ?, 'EMAIL', ?, 'ACTIVE', ?, ?)
                """, userId, identifier, role, Timestamp.from(now), Timestamp.from(now));
        jdbcTemplate.update("""
                INSERT INTO sessions(id, user_id, access_token, expires_at, last_seen_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, UUID.randomUUID(), userId, token, Timestamp.from(now.plusSeconds(900)), Timestamp.from(now),
                Timestamp.from(now));
        return new UserSession(userId, token);
    }

    private String readJson(MvcResult result, String path) throws Exception {
        return JsonPath.read(result.getResponse().getContentAsString(), path);
    }

    private record UserSession(UUID userId, String token) {
    }
}
