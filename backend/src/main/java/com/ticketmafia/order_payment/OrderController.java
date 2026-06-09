package com.ticketmafia.order_payment;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ApiResponse;
import com.ticketmafia.shared.AuthGuardFilter;
import com.ticketmafia.shared.ErrorCode;
import jakarta.servlet.http.HttpServletRequest;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {
    private final CheckoutService checkoutService;
    private final PaymentCompletionService paymentCompletionService;

    OrderController(CheckoutService checkoutService, PaymentCompletionService paymentCompletionService) {
        this.checkoutService = checkoutService;
        this.paymentCompletionService = paymentCompletionService;
    }

    // Sprint: v1 | Feature: FR-004,BR-002,BR-003,BR-004,NFR-002 | US: US-004 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
    // Contract: api-specs-v1.md API-005 POST /api/v1/orders/checkout; sequence-v1.md SEQ-003
    @PostMapping("/checkout")
    ApiResponse<CheckoutService.CheckoutResponse> checkout(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @RequestBody CheckoutRequest request,
            HttpServletRequest servletRequest) {
        return new ApiResponse<>(checkoutService.checkout(userId(servletRequest), request.matchId(),
                request.seatIds(), idempotencyKey));
    }

    // Sprint: v1 | Feature: FR-005,BR-005,NFR-002 | US: US-005 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
    // Contract: api-specs-v1.md API-006 POST /api/v1/orders/{orderId}/payment-completed; sequence-v1.md SEQ-003
    @PostMapping("/{orderId}/payment-completed")
    ApiResponse<PaymentCompletionService.PaymentCompletedResponse> paymentCompleted(
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @PathVariable UUID orderId,
            HttpServletRequest servletRequest) {
        return new ApiResponse<>(paymentCompletionService.complete(userId(servletRequest), orderId, idempotencyKey));
    }

    private UUID userId(HttpServletRequest request) {
        Object role = request.getAttribute(AuthGuardFilter.USER_ROLE_ATTRIBUTE);
        if (!"CUSTOMER".equals(role)) {
            throw new ApiException(HttpStatus.FORBIDDEN, ErrorCode.AUTH_FORBIDDEN,
                    "Customer role is required for checkout.", "role");
        }
        Object value = request.getAttribute(AuthGuardFilter.USER_ID_ATTRIBUTE);
        if (value instanceof UUID activeUserId) {
            return activeUserId;
        }
        throw new ApiException(HttpStatus.UNAUTHORIZED, ErrorCode.AUTH_UNAUTHORIZED,
                "Authentication is required before continuing.", null);
    }

    record CheckoutRequest(UUID matchId, List<UUID> seatIds) {
    }
}
