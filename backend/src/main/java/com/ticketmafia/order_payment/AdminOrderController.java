package com.ticketmafia.order_payment;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ApiResponse;
import com.ticketmafia.shared.AuthGuardFilter;
import com.ticketmafia.shared.ErrorCode;
import com.ticketmafia.shared.RequestTraceFilter;
import jakarta.servlet.http.HttpServletRequest;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/admin/orders")
public class AdminOrderController {
    private final AdminOrderDecisionService decisionService;

    AdminOrderController(AdminOrderDecisionService decisionService) {
        this.decisionService = decisionService;
    }

    // Sprint: v1 | Feature: FR-008,BR-005,NFR-004 | US: US-008 | Task Group: TG 1.4 Admin Payment Confirmation and Audit
    // Contract: api-specs-v1.md API-007 POST /api/v1/admin/orders/{orderId}/decision; sequence-v1.md SEQ-004
    @PostMapping("/{orderId}/decision")
    ApiResponse<AdminOrderDecisionService.DecisionResponse> decide(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @PathVariable UUID orderId,
            @RequestBody DecisionRequest request,
            HttpServletRequest servletRequest) {
        var command = new AdminOrderDecisionService.DecisionCommand(adminUserId(servletRequest), orderId,
                request.decision(), request.note(), idempotencyKey, requestId(servletRequest),
                traceId(servletRequest));
        return new ApiResponse<>(decisionService.decide(command));
    }

    private UUID adminUserId(HttpServletRequest request) {
        Object role = request.getAttribute(AuthGuardFilter.USER_ROLE_ATTRIBUTE);
        if (!"ADMIN".equals(role)) {
            throw new ApiException(HttpStatus.FORBIDDEN, ErrorCode.ADMIN_FORBIDDEN,
                    "Admin role is required.", "role");
        }
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

    record DecisionRequest(String decision, String note) {
    }
}
