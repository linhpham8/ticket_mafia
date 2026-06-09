package com.ticketmafia.ticket_scan;

import com.ticketmafia.config.TicketQrProperties;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;
import java.util.HexFormat;
import java.util.UUID;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.springframework.stereotype.Service;

@Service
public class QrTokenService {
    private static final String TOKEN_PREFIX = "tk_v1_";
    private final byte[] signingSecret;

    QrTokenService(TicketQrProperties properties) {
        this.signingSecret = properties.signingSecret().getBytes(StandardCharsets.UTF_8);
    }

    // Sprint: v1 | Feature: FR-009,FR-010,NFR-003 | US: US-010,US-011 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
    // Contract: api-specs-v1.md API-009/API-013; nfr-v1.md NFR-003 requires signed QR token with no PII
    public String issueToken(UUID ticketId) {
        byte[] signature = hmac("ticket-mafia:v1:ticket:%s".formatted(ticketId));
        return TOKEN_PREFIX + Base64.getUrlEncoder().withoutPadding().encodeToString(signature);
    }

    public boolean isWellFormed(String token) {
        if (token == null || !token.startsWith(TOKEN_PREFIX)) {
            return false;
        }
        try {
            Base64.getUrlDecoder().decode(token.substring(TOKEN_PREFIX.length()));
            return true;
        } catch (IllegalArgumentException exception) {
            return false;
        }
    }

    public String hashToken(String token) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(token.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256 is required for ticket token hashes.", exception);
        }
    }

    private byte[] hmac(String canonical) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(signingSecret, "HmacSHA256"));
            return mac.doFinal(canonical.getBytes(StandardCharsets.UTF_8));
        } catch (Exception exception) {
            throw new IllegalStateException("HMAC-SHA256 is required for ticket QR signing.", exception);
        }
    }
}
