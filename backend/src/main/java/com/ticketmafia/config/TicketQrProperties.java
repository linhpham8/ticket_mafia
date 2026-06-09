package com.ticketmafia.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "ticketing.qr")
public record TicketQrProperties(String signingSecret) {
    public TicketQrProperties {
        if (signingSecret == null || signingSecret.isBlank()) {
            throw new IllegalArgumentException("ticketing.qr.signing-secret must be provided by the runtime environment.");
        }
    }
}
