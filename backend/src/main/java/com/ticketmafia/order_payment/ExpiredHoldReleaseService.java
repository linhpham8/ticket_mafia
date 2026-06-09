package com.ticketmafia.order_payment;

import java.sql.Timestamp;
import java.time.Clock;
import java.time.Instant;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ExpiredHoldReleaseService {
    private final JdbcTemplate jdbcTemplate;
    private final AdminOrderDecisionService adminOrderDecisionService;
    private final Clock clock;

    @Autowired
    ExpiredHoldReleaseService(JdbcTemplate jdbcTemplate, AdminOrderDecisionService adminOrderDecisionService) {
        this(jdbcTemplate, adminOrderDecisionService, Clock.systemUTC());
    }

    ExpiredHoldReleaseService(JdbcTemplate jdbcTemplate, AdminOrderDecisionService adminOrderDecisionService,
                              Clock clock) {
        this.jdbcTemplate = jdbcTemplate;
        this.adminOrderDecisionService = adminOrderDecisionService;
        this.clock = clock;
    }

    // Sprint: v1 | Feature: FR-004,BR-002,NFR-002 | US: US-004 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
    // Contract: nfr-v1.md NFR-002 release expired holds every minute; product BR-002 returns seats to AVAILABLE
    @Scheduled(cron = "${ticketing.scheduler.release-expired-holds.cron:0 * * * * *}")
    @Transactional
    public int releaseExpiredHolds() {
        Instant now = clock.instant();
        var expiredOrderIds = jdbcTemplate.query("""
                SELECT id
                FROM orders
                WHERE status = 'HELD' AND hold_expires_at <= ?
                """, (rs, rowNum) -> rs.getObject("id", UUID.class), Timestamp.from(now));
        for (UUID orderId : expiredOrderIds) {
            jdbcTemplate.update("""
                    UPDATE seats
                    SET status = 'AVAILABLE', active_order_item_id = NULL, updated_at = ?
                    WHERE active_order_item_id IN (
                      SELECT id FROM order_items WHERE order_id = ? AND active = TRUE
                    )
                    """, Timestamp.from(now), orderId);
            jdbcTemplate.update("UPDATE order_items SET active = FALSE WHERE order_id = ? AND active = TRUE", orderId);
            jdbcTemplate.update("UPDATE orders SET status = 'EXPIRED', updated_at = ? WHERE id = ?",
                    Timestamp.from(now), orderId);
        }
        return expiredOrderIds.size();
    }

    // Sprint: v1 | Feature: FR-008,BR-005,NFR-004 | US: US-008 | Task Group: TG 1.4 Admin Payment Confirmation and Audit
    // Contract: product BR-005 cancels pending confirmations after 10 minutes and releases seats
    @Scheduled(cron = "${ticketing.scheduler.release-expired-admin-confirmations.cron:30 * * * * *}")
    @Transactional
    public int releaseExpiredAdminConfirmations() {
        Instant now = clock.instant();
        var expiredOrderIds = jdbcTemplate.query("""
                SELECT id
                FROM orders
                WHERE type = 'PURCHASE'
                  AND status = 'PENDING_ADMIN_CONFIRM'
                  AND admin_confirm_expires_at <= ?
                """, (rs, rowNum) -> rs.getObject("id", UUID.class), Timestamp.from(now));
        for (UUID orderId : expiredOrderIds) {
            adminOrderDecisionService.cancelExpiredPendingOrder(orderId, now);
        }
        return expiredOrderIds.size();
    }
}
