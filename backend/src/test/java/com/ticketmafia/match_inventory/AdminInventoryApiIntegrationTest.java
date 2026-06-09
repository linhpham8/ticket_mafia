package com.ticketmafia.match_inventory;

import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.blankOrNullString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.jayway.jsonpath.JsonPath;
import java.sql.Timestamp;
import java.time.Instant;
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
class AdminInventoryApiIntegrationTest {
    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private String adminToken;
    private String customerToken;

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
        adminToken = session("admin@example.test", "ADMIN");
        customerToken = session("fan@example.test", "CUSTOMER");
    }

    @Test
    void adminCreatesOpenMatchGeneratesSeatsAndSetsPrice() throws Exception {
        MvcResult matchResult = mockMvc.perform(post("/api/v1/admin/matches")
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "match-open-1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"name":"Hanoi FC vs Saigon FC","startsAt":"2026-07-01T12:00:00Z","status":"OPEN_FOR_SALE"}
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.id", not(blankOrNullString())))
                .andExpect(jsonPath("$.data.status").value("OPEN_FOR_SALE"))
                .andReturn();
        String matchId = readJson(matchResult, "$.data.id");

        mockMvc.perform(post("/api/v1/admin/matches/{matchId}/seats/generate", matchId)
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "seats-a-1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"sectionCode":"A","floorNo":1,"isVip":true,"seatCount":3}
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.generatedCount").value(3))
                .andExpect(jsonPath("$.data.seatCodes", hasSize(3)))
                .andExpect(jsonPath("$.data.seatCodes[0]").value("A-VIP-001"));

        mockMvc.perform(post("/api/v1/admin/matches/{matchId}/prices", matchId)
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "price-a-1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"sectionCode":"A","floorNo":1,"isVip":true,"priceVnd":250000}
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.priceVersionId", not(blankOrNullString())))
                .andExpect(jsonPath("$.data.activeFrom", not(blankOrNullString())));

        mockMvc.perform(post("/api/v1/admin/payment-qr-configs/default")
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "qr-default-1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"name":"QR MB Bank","qrAssetRef":"asset://payment/default-mb"}
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.name").value("QR MB Bank"))
                .andExpect(jsonPath("$.data.isDefault").value(true));

        Integer auditCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM audit_logs", Integer.class);
        org.assertj.core.api.Assertions.assertThat(auditCount).isEqualTo(4);
        Integer idempotencyCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM idempotency_records", Integer.class);
        org.assertj.core.api.Assertions.assertThat(idempotencyCount).isEqualTo(4);
    }

    @Test
    void adminMutationReplaysSameIdempotencyKey() throws Exception {
        MvcResult first = mockMvc.perform(post("/api/v1/admin/matches")
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "match-replay-1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Replay Match\",\"status\":\"OPEN_FOR_SALE\"}"))
                .andExpect(status().isOk())
                .andReturn();

        String firstId = readJson(first, "$.data.id");
        mockMvc.perform(post("/api/v1/admin/matches")
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "match-replay-1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Replay Match\",\"status\":\"OPEN_FOR_SALE\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.id").value(firstId));

        Integer matchCount = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM matches WHERE name = 'Replay Match'",
                Integer.class);
        org.assertj.core.api.Assertions.assertThat(matchCount).isEqualTo(1);
    }

    @Test
    void customerCannotCallAdminMutation() throws Exception {
        mockMvc.perform(post("/api/v1/admin/matches")
                        .header("Authorization", "Bearer " + customerToken)
                        .header("Idempotency-Key", "forbidden-1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"CLB A vs CLB B\",\"status\":\"OPEN_FOR_SALE\"}"))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.error.code").value("ADMIN_FORBIDDEN"));
    }

    @Test
    void adminMutationRequiresIdempotencyKey() throws Exception {
        mockMvc.perform(post("/api/v1/admin/matches")
                        .header("Authorization", "Bearer " + adminToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"CLB A vs CLB B\",\"status\":\"OPEN_FOR_SALE\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("ADMIN_MATCH_INVALID_REQUEST"));
    }

    @Test
    void duplicateSeatGenerationIsBlockedForSameSlice() throws Exception {
        String matchId = createMatch("dup-slice-match");
        String payload = "{\"sectionCode\":\"B\",\"floorNo\":2,\"seatCount\":1}";
        mockMvc.perform(post("/api/v1/admin/matches/{matchId}/seats/generate", matchId)
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "seats-first")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isOk());

        mockMvc.perform(post("/api/v1/admin/matches/{matchId}/seats/generate", matchId)
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "seats-second")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.error.code").value("SEATS_ALREADY_EXIST"));
    }

    @Test
    void cancelledMatchBlocksPriceUpdates() throws Exception {
        String matchId = createMatchWithStatus("cancelled-price-match", "CANCELLED");
        mockMvc.perform(post("/api/v1/admin/matches/{matchId}/prices", matchId)
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", "cancelled-price")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"sectionCode\":\"A\",\"floorNo\":1,\"priceVnd\":100000}"))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.error.code").value("MATCH_PRICE_LOCKED"));
    }

    private String createMatch(String idempotencyKey) throws Exception {
        return createMatchWithStatus(idempotencyKey, "OPEN_FOR_SALE");
    }

    private String createMatchWithStatus(String idempotencyKey, String status) throws Exception {
        MvcResult result = mockMvc.perform(post("/api/v1/admin/matches")
                        .header("Authorization", "Bearer " + adminToken)
                        .header("Idempotency-Key", idempotencyKey)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"%s\",\"status\":\"%s\"}".formatted(idempotencyKey, status)))
                .andExpect(status().isOk())
                .andReturn();
        return readJson(result, "$.data.id");
    }

    private String session(String identifier, String role) {
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
        return token;
    }

    private String readJson(MvcResult result, String path) throws Exception {
        return JsonPath.read(result.getResponse().getContentAsString(), path);
    }
}
