package com.ticketmafia.admin_confirmation;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.jayway.jsonpath.JsonPath;
import com.ticketmafia.order_payment.ExpiredHoldReleaseService;
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
class AdminOrderDecisionApiIntegrationTest {
    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private ExpiredHoldReleaseService expiredHoldReleaseService;

    private UUID adminId;
    private String adminToken;
    private UUID matchId;
    private String customerToken;
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
        UserSession admin = insertUser("admin-confirm@example.test", "ADMIN");
        adminId = admin.userId();
        adminToken = admin.token();
        UserSession customer = insertUser("fan-confirm@example.test", "CUSTOMER");
        customerToken = customer.token();
        seedMatchInventory();
    }

    @Test
    void adminConfirmPendingOrderIssuesTicketsAndWritesAudit() throws Exception {
        String orderId = createPendingOrder("checkout-admin-confirm", "pay-admin-confirm",
                List.of(seatOneId, seatTwoId));

        MvcResult decision = adminDecision(orderId, "admin-confirm-1", "CONFIRM", "Da nhan tien")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.orderId").value(orderId))
                .andExpect(jsonPath("$.data.status").value("ISSUED"))
                .andExpect(jsonPath("$.data.ticketIds", hasSize(2)))
                .andReturn();

        adminDecision(orderId, "admin-confirm-1", "CONFIRM", "Da nhan tien")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.ticketIds", hasSize(2)));

        assertThat(readJson(decision, "$.data.ticketIds[0]").toString()).isNotBlank();
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM orders WHERE id = ?", String.class,
                UUID.fromString(orderId))).isEqualTo("ISSUED");
        assertThat(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM tickets WHERE order_id = ?", Integer.class,
                UUID.fromString(orderId))).isEqualTo(2);
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, seatOneId))
                .isEqualTo("ISSUED");
        assertThat(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM audit_logs WHERE resource_id = ? AND action = ?",
                Integer.class, UUID.fromString(orderId), "ADMIN_ORDER_CONFIRM")).isEqualTo(1);
    }

    @Test
    void adminRejectAndConfirmationExpiryReleaseSeats() throws Exception {
        String rejectOrderId = createPendingOrder("checkout-admin-reject", "pay-admin-reject", List.of(seatOneId));

        adminDecision(rejectOrderId, "admin-reject-1", "REJECT", "Sai noi dung chuyen khoan")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("REJECTED"))
                .andExpect(jsonPath("$.data.ticketIds", hasSize(0)));

        assertThat(jdbcTemplate.queryForObject("SELECT status FROM orders WHERE id = ?", String.class,
                UUID.fromString(rejectOrderId))).isEqualTo("REJECTED");
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, seatOneId))
                .isEqualTo("AVAILABLE");
        assertThat(jdbcTemplate.queryForObject("SELECT active FROM order_items WHERE order_id = ?", Boolean.class,
                UUID.fromString(rejectOrderId))).isFalse();

        String expiredOrderId = createPendingOrder("checkout-admin-expire", "pay-admin-expire", List.of(seatTwoId));
        jdbcTemplate.update("""
                UPDATE orders
                SET admin_confirm_expires_at = ?
                WHERE id = ?
                """, Timestamp.from(Instant.now().minusSeconds(60)), UUID.fromString(expiredOrderId));

        assertThat(expiredHoldReleaseService.releaseExpiredAdminConfirmations()).isEqualTo(1);
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM orders WHERE id = ?", String.class,
                UUID.fromString(expiredOrderId))).isEqualTo("CANCELLED");
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, seatTwoId))
                .isEqualTo("AVAILABLE");
    }

    @Test
    void adminDecisionRequiresPendingStateAdminRoleAndStableIdempotencyPayload() throws Exception {
        String orderId = createPendingOrder("checkout-admin-guard", "pay-admin-guard", List.of(seatOneId));

        adminDecision(orderId, "admin-guard-1", "CONFIRM", "")
                .andExpect(status().isOk());

        adminDecision(orderId, "admin-guard-2", "REJECT", "")
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.error.code").value("ORDER_NOT_PENDING_CONFIRM"));

        String secondOrderId = createPendingOrder("checkout-admin-guard-2", "pay-admin-guard-2", List.of(seatTwoId));
        adminDecision(secondOrderId, "admin-guard-3", "INVALID", "")
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("ADMIN_DECISION_INVALID_REQUEST"));

        mockMvc.perform(post("/api/v1/admin/orders/{orderId}/decision", secondOrderId)
                        .header("Authorization", "Bearer " + customerToken)
                        .header("Idempotency-Key", "admin-guard-4")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"decision\":\"CONFIRM\"}"))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error.code").value("ADMIN_FORBIDDEN"));
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

    private String createPendingOrder(String checkoutKey, String paymentKey, List<UUID> seatIds) throws Exception {
        String orderId = readJson(checkout(customerToken, checkoutKey, seatIds)
                .andExpect(status().isOk()).andReturn(), "$.data.orderId");
        mockMvc.perform(post("/api/v1/orders/{orderId}/payment-completed", orderId)
                        .header("Authorization", "Bearer " + customerToken)
                        .header("Idempotency-Key", paymentKey)
                        .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("PENDING_ADMIN_CONFIRM"));
        return orderId;
    }

    private org.springframework.test.web.servlet.ResultActions adminDecision(String orderId, String idempotencyKey,
                                                                            String decision, String note)
            throws Exception {
        return mockMvc.perform(post("/api/v1/admin/orders/{orderId}/decision", orderId)
                .header("Authorization", "Bearer " + adminToken)
                .header("Idempotency-Key", idempotencyKey)
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"decision\":\"%s\",\"note\":\"%s\"}".formatted(decision, note)));
    }

    private void seedMatchInventory() {
        Instant now = Instant.now();
        matchId = UUID.randomUUID();
        jdbcTemplate.update("""
                INSERT INTO matches(id, name, starts_at, status, created_at, updated_at)
                VALUES (?, 'TG 1.4 Match', ?, 'OPEN_FOR_SALE', ?, ?)
                """, matchId, Timestamp.from(now.plusSeconds(86_400)), Timestamp.from(now), Timestamp.from(now));
        seatOneId = insertSeat("A-T1-001");
        seatTwoId = insertSeat("A-T1-002");
        jdbcTemplate.update("""
                INSERT INTO price_versions(id, match_id, section_code, floor_no, is_vip, price_vnd, active_from, created_by)
                VALUES (?, ?, 'A', 1, FALSE, ?, ?, ?)
                """, UUID.randomUUID(), matchId, BigDecimal.valueOf(120000), Timestamp.from(now), adminId);
        jdbcTemplate.update("""
                INSERT INTO payment_qr_configs(id, name, qr_asset_ref, is_default, created_by)
                VALUES (?, 'Default QR', 'asset://payment/default', TRUE, ?)
                """, UUID.randomUUID(), adminId);
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
