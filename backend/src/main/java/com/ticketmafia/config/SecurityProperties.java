package com.ticketmafia.config;

import java.time.Duration;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "security.session")
public record SecurityProperties(Duration inactiveTimeout) {
    public SecurityProperties {
        if (inactiveTimeout == null) {
            inactiveTimeout = Duration.ofMinutes(15);
        }
    }
}
