package com.ticketmafia.auth;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.ticketmafia.config.SecurityProperties;
import com.ticketmafia.shared.ApiException;
import java.sql.Timestamp;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;

@SpringBootTest
@ActiveProfiles("test")
class OtpServiceTest {
    @Autowired
    private OtpService otpService;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    void normalizesEmailAndPhoneIdentifiers() {
        assertThat(otpService.normalizeIdentifier(" FAN1@EXAMPLE.TEST ").value()).isEqualTo("fan1@example.test");
        assertThat(otpService.normalizeIdentifier("84901234567").type()).isEqualTo("PHONE");
    }

    @Test
    void rejectsMalformedIdentifier() {
        assertThatThrownBy(() -> otpService.normalizeIdentifier("not-valid"))
                .isInstanceOf(ApiException.class)
                .extracting("code")
                .isEqualTo("AUTH_IDENTIFIER_INVALID");
    }

    @Test
    void rateLimitsOtpRequestsPerIdentifierWindow() {
        String identifier = "rate-request-%s@example.test".formatted(UUID.randomUUID());

        for (int i = 0; i < 5; i++) {
            assertThat(otpService.requestOtp(identifier).challengeId()).isNotNull();
        }

        assertThatThrownBy(() -> otpService.requestOtp(identifier))
                .isInstanceOf(ApiException.class)
                .satisfies(exception -> {
                    ApiException apiException = (ApiException) exception;
                    assertThat(apiException.status().value()).isEqualTo(429);
                    assertThat(apiException.code()).isEqualTo("RATE_LIMITED");
                });
    }

    @Test
    void rejectsMalformedOtpBeforeCredentialCheck() {
        OtpChallenge challenge = otpService.requestOtp("malformed-otp-%s@example.test".formatted(UUID.randomUUID()));

        assertThatThrownBy(() -> otpService.verifyOtp(challenge.challengeId().toString(), "ABCDEF"))
                .isInstanceOf(ApiException.class)
                .satisfies(exception -> {
                    ApiException apiException = (ApiException) exception;
                    assertThat(apiException.status().value()).isEqualTo(400);
                    assertThat(apiException.code()).isEqualTo("AUTH_CHALLENGE_INVALID");
                });
    }

    @Test
    void rateLimitsOtpVerificationAttemptsPerChallenge() {
        OtpChallenge challenge = otpService.requestOtp("rate-verify-%s@example.test".formatted(UUID.randomUUID()));

        for (int i = 0; i < 5; i++) {
            assertThatThrownBy(() -> otpService.verifyOtp(challenge.challengeId().toString(), "111111"))
                    .isInstanceOf(ApiException.class)
                    .extracting("code")
                    .isEqualTo("AUTH_OTP_INVALID");
        }

        assertThatThrownBy(() -> otpService.verifyOtp(challenge.challengeId().toString(), "111111"))
                .isInstanceOf(ApiException.class)
                .satisfies(exception -> {
                    ApiException apiException = (ApiException) exception;
                    assertThat(apiException.status().value()).isEqualTo(429);
                    assertThat(apiException.code()).isEqualTo("RATE_LIMITED");
                });
    }

    @Test
    void rejectsDisabledUserAfterValidOtp() {
        String identifier = "disabled-%s@example.test".formatted(UUID.randomUUID());
        jdbcTemplate.update("""
                INSERT INTO users(identifier, identifier_type, role, status)
                VALUES (?, 'EMAIL', 'CUSTOMER', 'DISABLED')
                """, identifier);
        OtpChallenge challenge = otpService.requestOtp(identifier);

        assertThatThrownBy(() -> otpService.verifyOtp(challenge.challengeId().toString(), OtpService.DEMO_OTP))
                .isInstanceOf(ApiException.class)
                .satisfies(exception -> {
                    ApiException apiException = (ApiException) exception;
                    assertThat(apiException.status().value()).isEqualTo(403);
                    assertThat(apiException.code()).isEqualTo("AUTH_FORBIDDEN");
                });
    }

    @Test
    void refreshesActiveSessionAndRejectsExpiredInactiveSession() {
        MutableClock clock = new MutableClock(Instant.parse("2026-06-08T00:00:00Z"));
        SessionService sessionService = new SessionService(jdbcTemplate, new SecurityProperties(Duration.ofMinutes(15)), clock);
        UUID userId = UUID.randomUUID();
        jdbcTemplate.update("""
                INSERT INTO users(id, identifier, identifier_type, role, status)
                VALUES (?, ?, 'EMAIL', 'CUSTOMER', 'ACTIVE')
                """, userId, "session-%s@example.test".formatted(userId));
        SessionRecord created = sessionService.createSession(userId, "CUSTOMER");

        clock.set(Instant.parse("2026-06-08T00:10:00Z"));
        SessionRecord active = sessionService.findActiveSession(created.accessToken()).orElseThrow();

        assertThat(active.expiresAt()).isEqualTo(Instant.parse("2026-06-08T00:25:00Z"));
        Instant dbLastSeen = jdbcTemplate.queryForObject("""
                SELECT last_seen_at
                FROM sessions
                WHERE access_token = ?
                """, Timestamp.class, created.accessToken()).toInstant();
        assertThat(dbLastSeen).isEqualTo(Instant.parse("2026-06-08T00:10:00Z"));

        clock.set(Instant.parse("2026-06-08T00:41:00Z"));
        assertThat(sessionService.findActiveSession(created.accessToken())).isEmpty();
    }

    private static final class MutableClock extends Clock {
        private Instant instant;

        private MutableClock(Instant instant) {
            this.instant = instant;
        }

        private void set(Instant instant) {
            this.instant = instant;
        }

        @Override
        public ZoneId getZone() {
            return ZoneId.of("UTC");
        }

        @Override
        public Clock withZone(ZoneId zone) {
            return this;
        }

        @Override
        public Instant instant() {
            return instant;
        }
    }
}
