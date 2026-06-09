package com.ticketmafia.exchange;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.notNullValue;
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
class ExchangeApiIntegrationTest {
    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private UserSession admin;
    private UserSession fanOne;
    private UserSession fanTwo;
    private UUID matchId;
    private UUID oldSeatId;
    private UUID higherSeatId;
    private UUID equalSeatId;
    private UUID cheaperSeatId;

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
        admin = insertUser("admin-exchange@example.test", "ADMIN");
        fanOne = insertUser("fan-exchange-1@example.test", "CUSTOMER");
        fanTwo = insertUser("fan-exchange-2@example.test", "CUSTOMER");
        seedMatchInventory();
    }

    @Test
    void higherPricedExchangeCheckoutHoldsReplacementSeatAndAdminConfirmRetiresOldTicket() throws Exception {
        String oldOrderId = createIssuedOrder(fanOne.token(), "exchange-happy-old", List.of(oldSeatId));
        String oldTicketId = ticketIdForOrder(oldOrderId);

        MvcResult checkout = exchangeCheckout(fanOne.token(), oldTicketId, higherSeatId, "exchange-happy-checkout")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.type").value("EXCHANGE"))
                .andExpect(jsonPath("$.data.priceDifferenceVnd").value(50000.0))
                .andExpect(jsonPath("$.data.paymentQr.assetRef").value("asset://payment/default"))
                .andReturn();
        String exchangeOrderId = readJson(checkout, "$.data.orderId");

        exchangeCheckout(fanOne.token(), oldTicketId, higherSeatId, "exchange-happy-checkout")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.orderId").value(exchangeOrderId));

        assertThat(jdbcTemplate.queryForObject("SELECT status FROM tickets WHERE id = ?", String.class,
                UUID.fromString(oldTicketId))).isEqualTo("ISSUED");
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, higherSeatId))
                .isEqualTo("PENDING_ADMIN_CONFIRM");

        MvcResult decision = exchangeDecision(exchangeOrderId, "exchange-happy-decision", "CONFIRM", "paid")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.orderStatus").value("ISSUED"))
                .andExpect(jsonPath("$.data.oldTicketId").value(oldTicketId))
                .andExpect(jsonPath("$.data.newTicketId", notNullValue()))
                .andReturn();
        String newTicketId = readJson(decision, "$.data.newTicketId");

        assertThat(jdbcTemplate.queryForObject("SELECT status FROM tickets WHERE id = ?", String.class,
                UUID.fromString(oldTicketId))).isEqualTo("EXCHANGED");
        assertThat(jdbcTemplate.queryForObject("SELECT exchanged_to_ticket_id FROM tickets WHERE id = ?", UUID.class,
                UUID.fromString(oldTicketId))).isEqualTo(UUID.fromString(newTicketId));
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, oldSeatId))
                .isEqualTo("AVAILABLE");
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, higherSeatId))
                .isEqualTo("ISSUED");
        assertThat(jdbcTemplate.queryForObject("SELECT active FROM order_items WHERE order_id = ? AND seat_id = ?",
                Boolean.class, UUID.fromString(oldOrderId), oldSeatId)).isFalse();
        assertThat(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM audit_logs WHERE resource_id = ? AND action = ?",
                Integer.class, UUID.fromString(exchangeOrderId), "ADMIN_EXCHANGE_CONFIRM")).isEqualTo(1);
    }

    @Test
    void equalPricedExchangeRequiresNoPaymentQrAndRejectKeepsOldTicketIssued() throws Exception {
        String oldOrderId = createIssuedOrder(fanOne.token(), "exchange-equal-old", List.of(oldSeatId));
        String oldTicketId = ticketIdForOrder(oldOrderId);
        String exchangeOrderId = readJson(exchangeCheckout(fanOne.token(), oldTicketId, equalSeatId,
                        "exchange-equal-checkout")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.priceDifferenceVnd").value(0))
                .andExpect(jsonPath("$.data.paymentQr.assetRef").isEmpty())
                .andReturn(), "$.data.orderId");

        exchangeDecision(exchangeOrderId, "exchange-equal-reject", "REJECT", "not paid")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.orderStatus").value("REJECTED"))
                .andExpect(jsonPath("$.data.oldTicketId").isEmpty())
                .andExpect(jsonPath("$.data.newTicketId").isEmpty());

        assertThat(jdbcTemplate.queryForObject("SELECT status FROM tickets WHERE id = ?", String.class,
                UUID.fromString(oldTicketId))).isEqualTo("ISSUED");
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, equalSeatId))
                .isEqualTo("AVAILABLE");
        assertThat(jdbcTemplate.queryForObject("SELECT active FROM order_items WHERE order_id = ?",
                Boolean.class, UUID.fromString(exchangeOrderId))).isFalse();
    }

    @Test
    void cheaperUnavailableAndUnauthorizedExchangeTargetsAreBlockedBeforeCheckout() throws Exception {
        String oldOrderId = createIssuedOrder(fanOne.token(), "exchange-guard-old", List.of(oldSeatId));
        String oldTicketId = ticketIdForOrder(oldOrderId);

        exchangeCheckout(fanOne.token(), oldTicketId, cheaperSeatId, "exchange-cheaper")
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.error.code").value("EXCHANGE_CHEAPER_SEAT_NOT_ALLOWED"));

        exchangeCheckout(fanOne.token(), oldTicketId, oldSeatId, "exchange-unavailable")
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.error.code").value("EXCHANGE_STATE_CONFLICT"));

        exchangeCheckout(fanTwo.token(), oldTicketId, higherSeatId, "exchange-not-owner")
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error.code").value("TICKET_FORBIDDEN"));

        mockMvc.perform(post("/api/v1/tickets/{ticketId}/exchange/checkout", oldTicketId)
                        .header("Authorization", "Bearer " + fanOne.token())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"newSeatId\":\"%s\"}".formatted(higherSeatId)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("EXCHANGE_INVALID_REQUEST"));

        assertThat(jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM orders WHERE original_ticket_id = ?", Integer.class, UUID.fromString(oldTicketId)))
                .isZero();
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM tickets WHERE id = ?", String.class,
                UUID.fromString(oldTicketId))).isEqualTo("ISSUED");
    }

    private String createIssuedOrder(String customerToken, String keyPrefix, List<UUID> seatIds) throws Exception {
        String orderId = readJson(checkout(customerToken, keyPrefix + "-checkout", seatIds)
                .andExpect(status().isOk()).andReturn(), "$.data.orderId");
        mockMvc.perform(post("/api/v1/orders/{orderId}/payment-completed", orderId)
                        .header("Authorization", "Bearer " + customerToken)
                        .header("Idempotency-Key", keyPrefix + "-payment")
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk());
        mockMvc.perform(post("/api/v1/admin/orders/{orderId}/decision", orderId)
                        .header("Authorization", "Bearer " + admin.token())
                        .header("Idempotency-Key", keyPrefix + "-decision")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"decision\":\"CONFIRM\",\"note\":\"paid\"}"))
                .andExpect(status().isOk());
        return orderId;
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

    private org.springframework.test.web.servlet.ResultActions exchangeCheckout(String token, String ticketId,
                                                                               UUID newSeatId, String idempotencyKey)
            throws Exception {
        return mockMvc.perform(post("/api/v1/tickets/{ticketId}/exchange/checkout", ticketId)
                .header("Authorization", "Bearer " + token)
                .header("Idempotency-Key", idempotencyKey)
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"newSeatId\":\"%s\"}".formatted(newSeatId)));
    }

    private org.springframework.test.web.servlet.ResultActions exchangeDecision(String orderId, String idempotencyKey,
                                                                               String decision, String note)
            throws Exception {
        return mockMvc.perform(post("/api/v1/admin/exchanges/{orderId}/decision", orderId)
                .header("Authorization", "Bearer " + admin.token())
                .header("Idempotency-Key", idempotencyKey)
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"decision\":\"%s\",\"note\":\"%s\"}".formatted(decision, note)));
    }

    private String ticketIdForOrder(String orderId) {
        return jdbcTemplate.queryForObject("SELECT id FROM tickets WHERE order_id = ?", UUID.class,
                UUID.fromString(orderId)).toString();
    }

    private void seedMatchInventory() {
        Instant now = Instant.now();
        matchId = UUID.randomUUID();
        jdbcTemplate.update("""
                INSERT INTO matches(id, name, starts_at, status, created_at, updated_at)
                VALUES (?, 'TG 1.6 Match', ?, 'OPEN_FOR_SALE', ?, ?)
                """, matchId, Timestamp.from(now.plusSeconds(86_400)), Timestamp.from(now), Timestamp.from(now));
        oldSeatId = insertSeat("A-T1-001", "A", 1, false);
        equalSeatId = insertSeat("A-T1-002", "A", 1, false);
        higherSeatId = insertSeat("B-T1-001", "B", 1, false);
        cheaperSeatId = insertSeat("C-T1-001", "C", 1, false);
        insertPrice("A", 1, false, BigDecimal.valueOf(100000));
        insertPrice("B", 1, false, BigDecimal.valueOf(150000));
        insertPrice("C", 1, false, BigDecimal.valueOf(80000));
        jdbcTemplate.update("""
                INSERT INTO payment_qr_configs(id, name, qr_asset_ref, is_default, created_by)
                VALUES (?, 'Default QR', 'asset://payment/default', TRUE, ?)
                """, UUID.randomUUID(), admin.userId());
    }

    private UUID insertSeat(String seatCode, String section, int floorNo, boolean vip) {
        UUID seatId = UUID.randomUUID();
        jdbcTemplate.update("""
                INSERT INTO seats(id, match_id, section_code, floor_no, seat_code, is_vip, status)
                VALUES (?, ?, ?, ?, ?, ?, 'AVAILABLE')
                """, seatId, matchId, section, floorNo, seatCode, vip);
        return seatId;
    }

    private void insertPrice(String section, int floorNo, boolean vip, BigDecimal price) {
        jdbcTemplate.update("""
                INSERT INTO price_versions(id, match_id, section_code, floor_no, is_vip, price_vnd, active_from, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, UUID.randomUUID(), matchId, section, floorNo, vip, price, Timestamp.from(Instant.now()),
                admin.userId());
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
