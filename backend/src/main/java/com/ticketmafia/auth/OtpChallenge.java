package com.ticketmafia.auth;

import java.time.Instant;
import java.util.UUID;

public record OtpChallenge(UUID challengeId, Instant expiresAt) {
}
