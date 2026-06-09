package com.ticketmafia.ticket_scan;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ApiResponse;
import com.ticketmafia.shared.AuthGuardFilter;
import com.ticketmafia.shared.ErrorCode;
import com.ticketmafia.shared.RequestTraceFilter;
import com.ticketmafia.order_payment.ExchangeCheckoutService;
import jakarta.servlet.http.HttpServletRequest;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class TicketController {
    private final OrderHistoryService orderHistoryService;
    private final TicketDetailService ticketDetailService;
    private final TicketScanService ticketScanService;
    private final ExchangeCheckoutService exchangeCheckoutService;

    TicketController(OrderHistoryService orderHistoryService, TicketDetailService ticketDetailService,
                     TicketScanService ticketScanService, ExchangeCheckoutService exchangeCheckoutService) {
        this.orderHistoryService = orderHistoryService;
        this.ticketDetailService = ticketDetailService;
        this.ticketScanService = ticketScanService;
        this.exchangeCheckoutService = exchangeCheckoutService;
    }

    // Sprint: v1 | Feature: FR-009,BR-001 | US: US-009 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
    // Contract: api-specs-v1.md API-008 GET /api/v1/orders; project-reference-v1.md PR-004 ownership boundary
    @GetMapping("/orders")
    OrderHistoryService.HistoryPage orders(@RequestParam(required = false) String status,
                                           @RequestParam(required = false) String cursor,
                                           @RequestParam(required = false) Integer limit,
                                           HttpServletRequest request) {
        return orderHistoryService.list(customerUserId(request), status, cursor, limit);
    }

    // Sprint: v1 | Feature: FR-009,BR-006,NFR-003 | US: US-010 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
    // Contract: api-specs-v1.md API-009 GET /api/v1/tickets/{ticketId}; nfr-v1.md NFR-003 QR token no-PII rule
    @GetMapping("/tickets/{ticketId}")
    ApiResponse<TicketDetailService.TicketDetail> ticket(@PathVariable UUID ticketId, HttpServletRequest request) {
        return new ApiResponse<>(ticketDetailService.detail(customerUserId(request), ticketId));
    }

    // Sprint: v1 | Feature: FR-010,BR-006 | US: US-011 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
    // Contract: api-specs-v1.md API-013 POST /api/v1/tickets/scan; sequence-v1.md SEQ-005 atomic one-time scan
    @PostMapping("/tickets/scan")
    ApiResponse<TicketScanService.ScanResponse> scan(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @RequestBody ScanRequest body,
            HttpServletRequest request) {
        var command = new TicketScanService.ScanCommand(scannerUserId(request), body.qrToken(), body.scanSource(),
                idempotencyKey, requestId(request), traceId(request));
        return new ApiResponse<>(ticketScanService.scan(command));
    }

    // Sprint: v1 | Feature: FR-011,FR-012,BR-007,NFR-002 | US: US-012 | Task Group: TG 1.6 Seat Exchange and Local Demo Runtime
    // Contract: api-specs-v1.md API-014 POST /api/v1/tickets/{ticketId}/exchange/checkout; project-reference-v1.md PR-005 idempotency
    @PostMapping("/tickets/{ticketId}/exchange/checkout")
    ApiResponse<ExchangeCheckoutService.ExchangeCheckoutResponse> exchangeCheckout(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @PathVariable UUID ticketId,
            @RequestBody ExchangeCheckoutRequest body,
            HttpServletRequest request) {
        return new ApiResponse<>(exchangeCheckoutService.checkout(customerUserId(request), ticketId, body.newSeatId(),
                idempotencyKey));
    }

    private UUID customerUserId(HttpServletRequest request) {
        Object role = request.getAttribute(AuthGuardFilter.USER_ROLE_ATTRIBUTE);
        if (!"CUSTOMER".equals(role)) {
            throw new ApiException(HttpStatus.FORBIDDEN, ErrorCode.ORDER_FORBIDDEN,
                    "Customer role is required.", "role");
        }
        return requiredUserId(request);
    }

    private UUID scannerUserId(HttpServletRequest request) {
        Object role = request.getAttribute(AuthGuardFilter.USER_ROLE_ATTRIBUTE);
        if (!"ADMIN".equals(role)) {
            throw new ApiException(HttpStatus.FORBIDDEN, ErrorCode.SCAN_FORBIDDEN,
                    "Scanner or admin role is required.", "role");
        }
        return requiredUserId(request);
    }

    private UUID requiredUserId(HttpServletRequest request) {
        Object value = request.getAttribute(AuthGuardFilter.USER_ID_ATTRIBUTE);
        if (value instanceof UUID activeUserId) {
            return activeUserId;
        }
        throw new ApiException(HttpStatus.UNAUTHORIZED, ErrorCode.AUTH_UNAUTHORIZED,
                "Authentication is required before continuing.", null);
    }

    private String requestId(HttpServletRequest request) {
        return (String) request.getAttribute(RequestTraceFilter.REQUEST_ID_ATTRIBUTE);
    }

    private String traceId(HttpServletRequest request) {
        return (String) request.getAttribute(RequestTraceFilter.TRACE_ID_ATTRIBUTE);
    }

    record ScanRequest(String qrToken, String scanSource) {
    }

    record ExchangeCheckoutRequest(UUID newSeatId) {
    }
}
