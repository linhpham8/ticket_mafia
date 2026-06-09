package com.ticketmafia.auth;

import com.ticketmafia.config.SecurityProperties;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Clock;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class SessionService {
    private final JdbcTemplate jdbcTemplate;
    private final SecurityProperties securityProperties;
    private final Clock clock;

    @Autowired
    public SessionService(JdbcTemplate jdbcTemplate, SecurityProperties securityProperties) {
        this(jdbcTemplate, securityProperties, Clock.systemUTC());
    }

    SessionService(JdbcTemplate jdbcTemplate, SecurityProperties securityProperties, Clock clock) {
        this.jdbcTemplate = jdbcTemplate;
        this.securityProperties = securityProperties;
        this.clock = clock;
    }

    // Sprint: v1 | Feature: FR-001,NFR-003 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
    // Contract: sequence-v1.md SEQ-001 session creation; nfr-v1.md NFR-003 PT15M inactive timeout
    public SessionRecord createSession(UUID userId, String role) {
        UUID sessionId = UUID.randomUUID();
        String accessToken = UUID.randomUUID().toString();
        Instant now = clock.instant();
        Instant expiresAt = now.plus(securityProperties.inactiveTimeout());
        jdbcTemplate.update("""
                INSERT INTO sessions(id, user_id, access_token, expires_at, last_seen_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, sessionId, userId, accessToken, Timestamp.from(expiresAt), Timestamp.from(now),
                Timestamp.from(now));
        return new SessionRecord(accessToken, userId, role, expiresAt);
    }

    public Optional<SessionRecord> findActiveSession(String accessToken) {
        Instant now = clock.instant();
        return jdbcTemplate.query("""
                SELECT s.id, s.user_id, u.role
                FROM sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.access_token = ? AND s.expires_at > ? AND u.status = 'ACTIVE'
                """, this::mapSession, accessToken, Timestamp.from(now)).stream().findFirst()
                .map(session -> refreshInactiveTimeout(accessToken, session, now));
    }

    private SessionRecord refreshInactiveTimeout(String accessToken, SessionRecord session, Instant now) {
        Instant refreshedExpiry = now.plus(securityProperties.inactiveTimeout());
        jdbcTemplate.update("""
                UPDATE sessions
                SET last_seen_at = ?, expires_at = ?
                WHERE access_token = ?
                """, Timestamp.from(now), Timestamp.from(refreshedExpiry), accessToken);
        return new SessionRecord(null, session.userId(), session.role(), refreshedExpiry);
    }

    private SessionRecord mapSession(ResultSet rs, int rowNum) throws SQLException {
        return new SessionRecord(
                null,
                rs.getObject("user_id", UUID.class),
                rs.getString("role"),
                null);
    }
}
