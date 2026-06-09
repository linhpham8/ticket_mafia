package com.ticketmafia.shared;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class RequestTraceFilter extends OncePerRequestFilter {
    public static final String REQUEST_ID_ATTRIBUTE = "requestId";
    public static final String TRACE_ID_ATTRIBUTE = "traceId";

    @Override
    // Sprint: v1 | Feature: FR-001,NFR-004 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
    // Contract: devsecops-standards.md correlation headers; project-reference-v1.md PR-003
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String requestId = Optional.ofNullable(request.getHeader("X-Request-ID")).filter(s -> !s.isBlank())
                .orElseGet(() -> UUID.randomUUID().toString());
        String traceId = Optional.ofNullable(request.getHeader("X-Trace-ID")).filter(s -> !s.isBlank())
                .orElseGet(() -> UUID.randomUUID().toString());
        request.setAttribute(REQUEST_ID_ATTRIBUTE, requestId);
        request.setAttribute(TRACE_ID_ATTRIBUTE, traceId);
        response.setHeader("X-Request-ID", requestId);
        response.setHeader("X-Trace-ID", traceId);
        filterChain.doFilter(request, response);
    }
}
