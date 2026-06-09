package com.ticketmafia.auth;

import java.time.Instant;
import java.util.UUID;

public record OtpVerifyResponse(String accessToken, UserSummary user, Instant expiresAt) {
    public record UserSummary(UUID id, String role) {
    }
}
