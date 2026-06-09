package com.ticketmafia.match_inventory;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class InventoryServicesTest {
    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private PriceVersionService priceVersionService;

    @Autowired
    private PaymentQrConfigService paymentQrConfigService;

    private UUID adminId;
    private UUID matchId;

    @BeforeEach
    void setUp() {
        jdbcTemplate.update("DELETE FROM payment_qr_configs");
        jdbcTemplate.update("DELETE FROM audit_logs");
        jdbcTemplate.update("DELETE FROM tickets");
        jdbcTemplate.update("DELETE FROM order_items");
        jdbcTemplate.update("DELETE FROM orders");
        jdbcTemplate.update("DELETE FROM price_versions");
        jdbcTemplate.update("DELETE FROM seats");
        jdbcTemplate.update("DELETE FROM matches");
        jdbcTemplate.update("DELETE FROM sessions");
        jdbcTemplate.update("DELETE FROM idempotency_records");
        jdbcTemplate.update("DELETE FROM users");
        adminId = UUID.randomUUID();
        matchId = UUID.randomUUID();
        Instant now = Instant.now();
        jdbcTemplate.update("""
                INSERT INTO users(id, identifier, identifier_type, role, status, created_at, updated_at)
                VALUES (?, 'admin-service@example.test', 'EMAIL', 'ADMIN', 'ACTIVE', ?, ?)
                """, adminId, Timestamp.from(now), Timestamp.from(now));
        jdbcTemplate.update("""
                INSERT INTO matches(id, name, status, created_at, updated_at)
                VALUES (?, 'Service Test Match', 'OPEN_FOR_SALE', ?, ?)
                """, matchId, Timestamp.from(now), Timestamp.from(now));
    }

    @Test
    void seatCodeGenerationIsStableAndVipScopedToSectionA() {
        assertThat(SeatGenerationService.seatCode(new InventorySlice("A", 1, true), 1)).isEqualTo("A-VIP-001");
        assertThat(SeatGenerationService.seatCode(new InventorySlice("D", 2, false), 42)).isEqualTo("D-T2-042");
    }

    @Test
    void latestPriceUsesNewestActiveVersionForFutureCheckoutSnapshots() {
        priceVersionService.setPrice(adminId, matchId, "A", 1, false, new BigDecimal("100000"),
                "price-key-1", "request-1", "trace-1");
        priceVersionService.setPrice(adminId, matchId, "A", 1, false, new BigDecimal("120000"),
                "price-key-2", "request-2", "trace-2");

        assertThat(priceVersionService.latestPrice(matchId, "A", 1, false)).contains(new BigDecimal("120000.00"));
    }

    @Test
    void paymentQrDefaultInvariantKeepsOneActiveRecord() {
        paymentQrConfigService.setDefault(adminId, "QR 1", "asset://qr-1", "qr-key-1", "request-1", "trace-1");
        paymentQrConfigService.setDefault(adminId, "QR 2", "asset://qr-2", "qr-key-2", "request-2", "trace-2");

        assertThat(paymentQrConfigService.defaultCount()).isEqualTo(1);
    }
}
