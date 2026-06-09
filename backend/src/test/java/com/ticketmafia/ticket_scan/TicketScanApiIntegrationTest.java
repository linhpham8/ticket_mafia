package com.ticketmafia.ticket_scan;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.containsString;
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
class TicketScanApiIntegrationTest {
    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private String adminToken;
    private UserSession fanOne;
    private UserSession fanTwo;
    private UUID matchId;
    private UUID seatOneId;
    private UUID seatTwoId;
    private UUID seatThreeId;

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
        UserSession admin = insertUser("admin-scan@example.test", "ADMIN");
        adminToken = admin.token();
        fanOne = insertUser("fan1@example.test", "CUSTOMER");
        fanTwo = insertUser("fan2@example.test", "CUSTOMER");
        seedMatchInventory(admin.userId());
    }

    @Test
    void purchaseHistoryShowsOnlyCurrentUserRecordsAndEmptyStateDoesNotLeakOtherUserData() throws Exception {
        String fanOneOrderId = createIssuedOrder(fanOne.token(), "fan-one", List.of(seatOneId));

        mockMvc.perform(get("/api/v1/orders")
                        .header("Authorization", "Bearer " + fanOne.token()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data", hasSize(1)))
                .andExpect(jsonPath("$.data[0].orderId").value(fanOneOrderId))
                .andExpect(jsonPath("$.data[0].status").value("ISSUED"))
                .andExpect(jsonPath("$.data[0].matchName").value("TG 1.5 Match"))
                .andExpect(jsonPath("$.data[0].tickets", hasSize(1)));

        mockMvc.perform(get("/api/v1/orders")
                        .header("Authorization", "Bearer " + fanTwo.token()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data", hasSize(0)));
    }

    @Test
    void purchaseHistoryCursorPaginatesOrdersAndKeepsAllTicketsForReturnedOrder() throws Exception {
        String olderOrderId = createIssuedOrder(fanOne.token(), "page-old", List.of(seatOneId));
        String newestOrderId = createIssuedOrder(fanOne.token(), "page-new", List.of(seatTwoId, seatThreeId));

        MvcResult firstPage = mockMvc.perform(get("/api/v1/orders")
                        .header("Authorization", "Bearer " + fanOne.token())
                        .param("limit", "1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data", hasSize(1)))
                .andExpect(jsonPath("$.data[0].orderId").value(newestOrderId))
                .andExpect(jsonPath("$.data[0].tickets", hasSize(2)))
                .andReturn();

        String cursor = readJson(firstPage, "$.meta.nextCursor");
        assertThat(cursor).isNotBlank();

        mockMvc.perform(get("/api/v1/orders")
                        .header("Authorization", "Bearer " + fanOne.token())
                        .param("limit", "1")
                        .param("cursor", cursor))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data", hasSize(1)))
                .andExpect(jsonPath("$.data[0].orderId").value(olderOrderId))
                .andExpect(jsonPath("$.data[0].tickets", hasSize(1)));
    }

    @Test
    void ticketDetailRequiresOwnershipAndReturnsSignedQrWithoutPlaintextPii() throws Exception {
        String orderId = createIssuedOrder(fanOne.token(), "detail", List.of(seatOneId));
        String ticketId = ticketIdForOrder(orderId);

        MvcResult detail = mockMvc.perform(get("/api/v1/tickets/{ticketId}", ticketId)
                        .header("Authorization", "Bearer " + fanOne.token()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.ticketId").value(ticketId))
                .andExpect(jsonPath("$.data.match.name").value("TG 1.5 Match"))
                .andExpect(jsonPath("$.data.seatCode").value("A-T1-001"))
                .andExpect(jsonPath("$.data.status").value("ISSUED"))
                .andExpect(jsonPath("$.data.qrToken").value(not(containsString("fan1@example.test"))))
                .andReturn();

        String qrToken = readJson(detail, "$.data.qrToken");
        assertThat(qrToken).startsWith("tk_v1_");
        assertThat(qrToken).doesNotContain("84901234567", "Nguyen Van A", "fan1@example.test");

        mockMvc.perform(get("/api/v1/tickets/{ticketId}", ticketId)
                        .header("Authorization", "Bearer " + fanTwo.token()))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error.code").value("TICKET_FORBIDDEN"));
    }

    @Test
    void invalidTicketStatusesDoNotExposeEntryQr() throws Exception {
        String orderId = createIssuedOrder(fanOne.token(), "invalid-status", List.of(seatOneId));
        String ticketId = ticketIdForOrder(orderId);
        jdbcTemplate.update("UPDATE tickets SET status = 'CANCELLED' WHERE id = ?", UUID.fromString(ticketId));

        mockMvc.perform(get("/api/v1/tickets/{ticketId}", ticketId)
                        .header("Authorization", "Bearer " + fanOne.token()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.status").value("CANCELLED"))
                .andExpect(jsonPath("$.data.qrToken").isEmpty());
    }

    @Test
    void firstValidScanMarksTicketUsedAndRepeatedScanIsRejected() throws Exception {
        String orderId = createIssuedOrder(fanOne.token(), "scan", List.of(seatOneId));
        String ticketId = ticketIdForOrder(orderId);
        String qrToken = readJson(mockMvc.perform(get("/api/v1/tickets/{ticketId}", ticketId)
                        .header("Authorization", "Bearer " + fanOne.token()))
                .andExpect(status().isOk()).andReturn(), "$.data.qrToken");

        mockMvc.perform(post("/api/v1/tickets/scan")
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "scan-key-1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"qrToken\":\"%s\",\"scanSource\":\"gate-a\"}".formatted(qrToken)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.ticketId").value(ticketId))
                .andExpect(jsonPath("$.data.status").value("USED_SCANNED"));

        mockMvc.perform(post("/api/v1/tickets/scan")
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "scan-key-1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"qrToken\":\"%s\",\"scanSource\":\"gate-a\"}".formatted(qrToken)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.ticketId").value(ticketId));

        mockMvc.perform(post("/api/v1/tickets/scan")
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "scan-key-2")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"qrToken\":\"%s\",\"scanSource\":\"gate-a\"}".formatted(qrToken)))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.error.code").value("TICKET_ALREADY_SCANNED"));

        assertThat(jdbcTemplate.queryForObject("SELECT status FROM tickets WHERE id = ?", String.class,
                UUID.fromString(ticketId))).isEqualTo("USED_SCANNED");
        assertThat(jdbcTemplate.queryForObject("SELECT COUNT(*) FROM audit_logs WHERE resource_id = ? AND action = ?",
                Integer.class, UUID.fromString(ticketId), "TICKET_SCAN")).isEqualTo(1);
    }

    @Test
    void scanRequiresAdminRoleAndIdempotencyKey() throws Exception {
        String orderId = createIssuedOrder(fanOne.token(), "scan-guard", List.of(seatOneId));
        String ticketId = ticketIdForOrder(orderId);
        String qrToken = readJson(mockMvc.perform(get("/api/v1/tickets/{ticketId}", ticketId)
                        .header("Authorization", "Bearer " + fanOne.token()))
                .andExpect(status().isOk()).andReturn(), "$.data.qrToken");

        mockMvc.perform(post("/api/v1/tickets/scan")
                        .header("Authorization", "Bearer " + fanOne.token())
                        .header("Idempotency-Key", "scan-guard-1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"qrToken\":\"%s\"}".formatted(qrToken)))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error.code").value("SCAN_FORBIDDEN"));

        mockMvc.perform(post("/api/v1/tickets/scan")
                        .header("Authorization", "Bearer " + adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"qrToken\":\"%s\"}".formatted(qrToken)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("SCAN_TOKEN_INVALID"));

        String longScanSource = "x".repeat(121);
        mockMvc.perform(post("/api/v1/tickets/scan")
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "scan-guard-2")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"qrToken\":\"%s\",\"scanSource\":\"%s\"}".formatted(qrToken, longScanSource)))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_ERROR"));
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
                        .header("Authorization", "Bearer " + adminToken)
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

    private String ticketIdForOrder(String orderId) {
        return jdbcTemplate.queryForObject("SELECT id FROM tickets WHERE order_id = ?", UUID.class,
                UUID.fromString(orderId)).toString();
    }

    private void seedMatchInventory(UUID adminId) {
        Instant now = Instant.now();
        matchId = UUID.randomUUID();
        jdbcTemplate.update("""
                INSERT INTO matches(id, name, starts_at, status, created_at, updated_at)
                VALUES (?, 'TG 1.5 Match', ?, 'OPEN_FOR_SALE', ?, ?)
                """, matchId, Timestamp.from(now.plusSeconds(86_400)), Timestamp.from(now), Timestamp.from(now));
        seatOneId = insertSeat("A-T1-001");
        seatTwoId = insertSeat("A-T1-002");
        seatThreeId = insertSeat("A-T1-003");
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
