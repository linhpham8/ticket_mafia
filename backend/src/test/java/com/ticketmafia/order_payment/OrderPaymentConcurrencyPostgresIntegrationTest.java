package com.ticketmafia.order_payment;

import static org.assertj.core.api.Assertions.assertThat;

import com.ticketmafia.shared.ApiException;
import java.math.BigDecimal;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

@SpringBootTest
@ActiveProfiles("test")
@Testcontainers
class OrderPaymentConcurrencyPostgresIntegrationTest {
    @Container
    static final PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void postgresProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.datasource.driver-class-name", postgres::getDriverClassName);
        registry.add("spring.flyway.locations", () -> "classpath:db/migration");
    }

    @Autowired
    private CheckoutService checkoutService;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    private UUID matchId;
    private UUID seatId;
    private UUID firstUserId;
    private UUID secondUserId;
    private UUID adminId;

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

        adminId = insertUser("admin-concurrency@example.test", "ADMIN");
        firstUserId = insertUser("fan-one-concurrency@example.test", "CUSTOMER");
        secondUserId = insertUser("fan-two-concurrency@example.test", "CUSTOMER");
        seedOneAvailableSeat();
    }

    @Test
    void concurrentCheckoutPermitsOnlyOneActiveHoldPerSeat() throws Exception {
        CyclicBarrier barrier = new CyclicBarrier(2);
        Callable<String> first = () -> checkoutAfterBarrier(barrier, firstUserId, "concurrency-key-1");
        Callable<String> second = () -> checkoutAfterBarrier(barrier, secondUserId, "concurrency-key-2");

        try (var executor = Executors.newFixedThreadPool(2)) {
            List<String> results = executor.invokeAll(List.of(first, second)).stream()
                    .map(future -> {
                        try {
                            return future.get();
                        } catch (Exception exception) {
                            throw new IllegalStateException(exception);
                        }
                    })
                    .toList();

            assertThat(results).containsExactlyInAnyOrder("SUCCESS", "SEAT_UNAVAILABLE");
        }

        assertThat(jdbcTemplate.queryForObject("""
                SELECT COUNT(*)
                FROM order_items
                WHERE seat_id = ? AND active = TRUE
                """, Integer.class, seatId)).isEqualTo(1);
        assertThat(jdbcTemplate.queryForObject("SELECT status FROM seats WHERE id = ?", String.class, seatId))
                .isEqualTo("HELD");
    }

    private String checkoutAfterBarrier(CyclicBarrier barrier, UUID userId, String idempotencyKey) throws Exception {
        barrier.await();
        try {
            checkoutService.checkout(userId, matchId, List.of(seatId), idempotencyKey);
            return "SUCCESS";
        } catch (ApiException exception) {
            return exception.code();
        }
    }

    private UUID insertUser(String identifier, String role) {
        UUID userId = UUID.randomUUID();
        Instant now = Instant.now();
        jdbcTemplate.update("""
                INSERT INTO users(id, identifier, identifier_type, role, status, created_at, updated_at)
                VALUES (?, ?, 'EMAIL', ?, 'ACTIVE', ?, ?)
                """, userId, identifier, role, Timestamp.from(now), Timestamp.from(now));
        return userId;
    }

    private void seedOneAvailableSeat() {
        Instant now = Instant.now();
        matchId = UUID.randomUUID();
        seatId = UUID.randomUUID();
        jdbcTemplate.update("""
                INSERT INTO matches(id, name, starts_at, status, created_at, updated_at)
                VALUES (?, 'TG 1.3 Concurrency Match', ?, 'OPEN_FOR_SALE', ?, ?)
                """, matchId, Timestamp.from(now.plusSeconds(86_400)), Timestamp.from(now), Timestamp.from(now));
        jdbcTemplate.update("""
                INSERT INTO seats(id, match_id, section_code, floor_no, seat_code, is_vip, status)
                VALUES (?, ?, 'A', 1, 'A-T1-001', FALSE, 'AVAILABLE')
                """, seatId, matchId);
        jdbcTemplate.update("""
                INSERT INTO price_versions(id, match_id, section_code, floor_no, is_vip, price_vnd, active_from, created_by)
                VALUES (?, ?, 'A', 1, FALSE, ?, ?, ?)
                """, UUID.randomUUID(), matchId, BigDecimal.valueOf(120_000), Timestamp.from(now), adminId);
        jdbcTemplate.update("""
                INSERT INTO payment_qr_configs(id, name, qr_asset_ref, is_default, created_by)
                VALUES (?, 'Default QR', 'asset://payment/default', TRUE, ?)
                """, UUID.randomUUID(), adminId);
    }
}
