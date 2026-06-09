package com.ticketmafia.auth;

import com.ticketmafia.config.SecurityProperties;
import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.regex.Pattern;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OtpService {
    static final String DEMO_OTP = "000000";
    private static final int REQUEST_LIMIT = 5;
    private static final int VERIFY_ATTEMPT_LIMIT = 5;
    private static final Pattern EMAIL = Pattern.compile("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$");
    private static final Pattern VN_PHONE = Pattern.compile("^(0|84)\\d{8,10}$");
    private static final Pattern OTP = Pattern.compile("^\\d{6}$");

    private final JdbcTemplate jdbcTemplate;
    private final SessionService sessionService;
    private final Clock clock;

    @Autowired
    public OtpService(JdbcTemplate jdbcTemplate, SessionService sessionService) {
        this(jdbcTemplate, sessionService, Clock.systemUTC());
    }

    OtpService(JdbcTemplate jdbcTemplate, SessionService sessionService, Clock clock) {
        this.jdbcTemplate = jdbcTemplate;
        this.sessionService = sessionService;
        this.clock = clock;
    }

    // Sprint: v1 | Feature: FR-001,NFR-003 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
    // Contract: api-specs-v1.md API-001; sequence-v1.md SEQ-001 mock OTP challenge storage
    public OtpChallenge requestOtp(String rawIdentifier) {
        Identifier identifier = normalizeIdentifier(rawIdentifier);
        UUID challengeId = UUID.randomUUID();
        Instant now = clock.instant();
        if (recentChallengeCount(identifier.value(), now.minus(Duration.ofMinutes(10))) >= REQUEST_LIMIT) {
            throw new ApiException(HttpStatus.TOO_MANY_REQUESTS, ErrorCode.RATE_LIMITED,
                    "Too many OTP requests for this identifier.", "identifier");
        }
        Instant expiresAt = now.plus(Duration.ofMinutes(5));
        jdbcTemplate.update("""
                INSERT INTO otp_challenges(id, identifier, identifier_type, otp_code, expires_at, consumed_at, attempt_count, created_at)
                VALUES (?, ?, ?, ?, ?, NULL, 0, ?)
                """, challengeId, identifier.value(), identifier.type(), DEMO_OTP, Timestamp.from(expiresAt),
                Timestamp.from(now));
        return new OtpChallenge(challengeId, expiresAt);
    }

    // Sprint: v1 | Feature: FR-001,NFR-003 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
    // Contract: api-specs-v1.md API-002; sequence-v1.md SEQ-001 user/session creation
    @Transactional(noRollbackFor = ApiException.class)
    public OtpVerifyResponse verifyOtp(String challengeIdValue, String otp) {
        UUID challengeId = parseChallengeId(challengeIdValue);
        validateOtpFormat(otp);
        OtpChallengeRecord challenge = findChallenge(challengeId)
                .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, ErrorCode.AUTH_CHALLENGE_NOT_FOUND,
                        "OTP challenge was not found.", null));
        if (challenge.consumedAt() != null) {
            throw new ApiException(HttpStatus.CONFLICT, ErrorCode.AUTH_CHALLENGE_USED,
                    "OTP challenge was already consumed.", null);
        }
        if (challenge.attemptCount() >= VERIFY_ATTEMPT_LIMIT) {
            throw new ApiException(HttpStatus.TOO_MANY_REQUESTS, ErrorCode.RATE_LIMITED,
                    "Too many OTP verification attempts for this challenge.", "otp");
        }
        if (challenge.expiresAt().isBefore(clock.instant()) || !DEMO_OTP.equals(otp)) {
            jdbcTemplate.update("UPDATE otp_challenges SET attempt_count = attempt_count + 1 WHERE id = ?", challenge.id());
            throw new ApiException(HttpStatus.UNAUTHORIZED, ErrorCode.AUTH_OTP_INVALID,
                    "OTP is wrong or expired.", null);
        }
        UserRecord user = upsertAndFindUser(challenge.identifier(), challenge.identifierType());
        if ("DISABLED".equals(user.status())) {
            throw new ApiException(HttpStatus.FORBIDDEN, ErrorCode.AUTH_FORBIDDEN,
                    "User account is disabled.", null);
        }
        jdbcTemplate.update("UPDATE otp_challenges SET consumed_at = ? WHERE id = ?",
                Timestamp.from(clock.instant()), challenge.id());
        SessionRecord session = sessionService.createSession(user.id(), user.role());
        return new OtpVerifyResponse(session.accessToken(), new OtpVerifyResponse.UserSummary(user.id(), user.role()),
                session.expiresAt());
    }

    Identifier normalizeIdentifier(String rawIdentifier) {
        String value = Optional.ofNullable(rawIdentifier).map(String::trim).orElse("");
        if (value.isEmpty() || value.length() > 255) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.AUTH_IDENTIFIER_INVALID,
                    "Identifier must be an email or Vietnam-like phone number.", "identifier");
        }
        String normalized = value.toLowerCase(Locale.ROOT);
        if (EMAIL.matcher(normalized).matches()) {
            return new Identifier(normalized, "EMAIL");
        }
        if (VN_PHONE.matcher(value).matches()) {
            return new Identifier(value, "PHONE");
        }
        throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.AUTH_IDENTIFIER_INVALID,
                "Identifier must be an email or Vietnam-like phone number.", "identifier");
    }

    private UUID parseChallengeId(String challengeIdValue) {
        try {
            return UUID.fromString(challengeIdValue);
        } catch (IllegalArgumentException | NullPointerException exception) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.AUTH_CHALLENGE_INVALID,
                    "Challenge ID is malformed.", "challengeId");
        }
    }

    private void validateOtpFormat(String otp) {
        if (otp == null || !OTP.matcher(otp).matches()) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.AUTH_CHALLENGE_INVALID,
                    "OTP must be a six digit code.", "otp");
        }
    }

    private int recentChallengeCount(String identifier, Instant createdAfter) {
        Integer count = jdbcTemplate.queryForObject("""
                SELECT COUNT(*)
                FROM otp_challenges
                WHERE identifier = ? AND created_at >= ?
                """, Integer.class, identifier, Timestamp.from(createdAfter));
        return count == null ? 0 : count;
    }

    private Optional<OtpChallengeRecord> findChallenge(UUID challengeId) {
        return jdbcTemplate.query("""
                SELECT id, identifier, identifier_type, expires_at, consumed_at, attempt_count
                FROM otp_challenges
                WHERE id = ?
                """, this::mapChallenge, challengeId).stream().findFirst();
    }

    private UserRecord upsertAndFindUser(String identifier, String identifierType) {
        try {
            jdbcTemplate.update("""
                    INSERT INTO users(identifier, identifier_type, role, status)
                    VALUES (?, ?, 'CUSTOMER', 'ACTIVE')
                    """, identifier, identifierType);
        } catch (DuplicateKeyException ignored) {
            // Existing demo user is acceptable; the identifier remains the stable login owner.
        }
        return jdbcTemplate.queryForObject("""
                SELECT id, role, status
                FROM users
                WHERE identifier = ?
                """, (rs, rowNum) -> new UserRecord(
                rs.getObject("id", UUID.class),
                rs.getString("role"),
                rs.getString("status")), identifier);
    }

    private OtpChallengeRecord mapChallenge(ResultSet rs, int rowNum) throws SQLException {
        var consumed = rs.getTimestamp("consumed_at");
        return new OtpChallengeRecord(
                rs.getObject("id", UUID.class),
                rs.getString("identifier"),
                rs.getString("identifier_type"),
                rs.getTimestamp("expires_at").toInstant(),
                consumed == null ? null : consumed.toInstant(),
                rs.getInt("attempt_count"));
    }

    record Identifier(String value, String type) {
    }

    private record OtpChallengeRecord(UUID id, String identifier, String identifierType, Instant expiresAt,
                                      Instant consumedAt, int attemptCount) {
    }

    private record UserRecord(UUID id, String role, String status) {
    }
}
