package com.ticketmafia.shared;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ticketmafia.auth.SessionRecord;
import com.ticketmafia.auth.SessionService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Optional;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 1)
public class AuthGuardFilter extends OncePerRequestFilter {
    public static final String USER_ID_ATTRIBUTE = "ticketMafia.userId";
    public static final String USER_ROLE_ATTRIBUTE = "ticketMafia.userRole";

    private final SessionService sessionService;
    private final ObjectMapper objectMapper;

    public AuthGuardFilter(SessionService sessionService, ObjectMapper objectMapper) {
        this.sessionService = sessionService;
        this.objectMapper = objectMapper;
    }

    @Override
    // Sprint: v1 | Feature: FR-001,FR-006,FR-007,FR-009,FR-010,NFR-003 | US: US-001,US-006,US-007,US-009..US-011 | Task Group: TG 1.1; TG 1.2; TG 1.5
    // Contract: api-specs-v1.md API-005/API-008/API-009/API-010/API-011/API-012/API-013/API-014/API-016; project-reference-v1.md PR-003/PR-005
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        Optional<SessionRecord> session = bearerToken(request).flatMap(sessionService::findActiveSession);
        if (requiresSession(request) && session.isEmpty()) {
            writeError(response, request, HttpServletResponse.SC_UNAUTHORIZED, ErrorCode.AUTH_UNAUTHORIZED,
                    "Authentication is required before continuing.", null);
            return;
        }
        if (requiresAdmin(request) && session.filter(active -> "ADMIN".equals(active.role())).isEmpty()) {
            ErrorCode code = session.isEmpty() ? ErrorCode.AUTH_UNAUTHORIZED : ErrorCode.ADMIN_FORBIDDEN;
            int status = session.isEmpty() ? HttpServletResponse.SC_UNAUTHORIZED : HttpServletResponse.SC_FORBIDDEN;
            writeError(response, request, status, code,
                    session.isEmpty() ? "Authentication is required before continuing." : "Admin role is required.",
                    session.isEmpty() ? null : "role");
            return;
        }
        session.ifPresent(active -> {
            request.setAttribute(USER_ID_ATTRIBUTE, active.userId());
            request.setAttribute(USER_ROLE_ATTRIBUTE, active.role());
        });
        filterChain.doFilter(request, response);
    }

    private boolean requiresSession(HttpServletRequest request) {
        String path = request.getRequestURI();
        return ("POST".equals(request.getMethod()) && "/api/v1/orders/checkout".equals(path))
                || ("GET".equals(request.getMethod()) && "/api/v1/orders".equals(path))
                || ("GET".equals(request.getMethod()) && path.matches("/api/v1/tickets/[^/]+"))
                || ("POST".equals(request.getMethod()) && "/api/v1/tickets/scan".equals(path))
                || ("POST".equals(request.getMethod()) && path.matches("/api/v1/orders/[^/]+/payment-completed"))
                || ("POST".equals(request.getMethod()) && path.matches("/api/v1/tickets/[^/]+/exchange/checkout"));
    }

    private boolean requiresAdmin(HttpServletRequest request) {
        return request.getRequestURI().startsWith("/api/v1/admin/");
    }

    private void writeError(HttpServletResponse response, HttpServletRequest request, int status, ErrorCode code,
                            String message, Object details) throws IOException {
        response.setStatus(status);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        var error = new ErrorEnvelope(new ApiError(
                code.code(),
                message,
                (String) request.getAttribute(RequestTraceFilter.REQUEST_ID_ATTRIBUTE),
                (String) request.getAttribute(RequestTraceFilter.TRACE_ID_ATTRIBUTE),
                details));
        objectMapper.writeValue(response.getOutputStream(), error);
    }

    private Optional<String> bearerToken(HttpServletRequest request) {
        return Optional.ofNullable(request.getHeader("Authorization"))
                .filter(value -> value.startsWith("Bearer "))
                .map(value -> value.substring("Bearer ".length()));
    }
}
