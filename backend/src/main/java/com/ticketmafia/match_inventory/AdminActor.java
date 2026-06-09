package com.ticketmafia.match_inventory;

import com.ticketmafia.auth.SessionRecord;
import com.ticketmafia.auth.SessionService;
import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ErrorCode;
import java.util.Optional;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

@Component
class AdminActor {
    private final SessionService sessionService;

    AdminActor(SessionService sessionService) {
        this.sessionService = sessionService;
    }

    UUID requireAdminUser(String authorizationHeader) {
        SessionRecord session = bearerToken(authorizationHeader)
                .flatMap(sessionService::findActiveSession)
                .orElseThrow(() -> new ApiException(HttpStatus.UNAUTHORIZED, ErrorCode.AUTH_UNAUTHORIZED,
                        "Authentication is required before continuing.", null));
        if (!"ADMIN".equals(session.role())) {
            throw new ApiException(HttpStatus.FORBIDDEN, ErrorCode.ADMIN_FORBIDDEN,
                    "Admin role is required.", "role");
        }
        return session.userId();
    }

    private Optional<String> bearerToken(String authorizationHeader) {
        return Optional.ofNullable(authorizationHeader)
                .filter(value -> value.startsWith("Bearer "))
                .map(value -> value.substring("Bearer ".length()));
    }
}
