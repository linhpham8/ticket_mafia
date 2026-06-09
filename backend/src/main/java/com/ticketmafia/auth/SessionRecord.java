package com.ticketmafia.auth;

import java.time.Instant;
import java.util.UUID;

public record SessionRecord(String accessToken, UUID userId, String role, Instant expiresAt) {
}
