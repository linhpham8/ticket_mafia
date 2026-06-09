package com.ticketmafia;

import com.ticketmafia.config.SecurityProperties;
import com.ticketmafia.config.TicketQrProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableConfigurationProperties({SecurityProperties.class, TicketQrProperties.class})
@EnableScheduling
public class TicketMafiaApplication {
    public static void main(String[] args) {
        SpringApplication.run(TicketMafiaApplication.class, args);
    }
}
