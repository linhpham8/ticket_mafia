package com.ticketmafia.match_inventory;

import com.ticketmafia.shared.ApiException;
import com.ticketmafia.shared.ApiResponse;
import com.ticketmafia.shared.ErrorCode;
import com.ticketmafia.shared.RequestTraceFilter;
import jakarta.servlet.http.HttpServletRequest;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/admin/payment-qr-configs")
public class AdminPaymentQrController {
    private final AdminActor adminActor;
    private final PaymentQrConfigService paymentQrConfigService;

    AdminPaymentQrController(AdminActor adminActor, PaymentQrConfigService paymentQrConfigService) {
        this.adminActor = adminActor;
        this.paymentQrConfigService = paymentQrConfigService;
    }

    // Sprint: v1 | Feature: FR-007,BR-004,NFR-004 | US: US-007 | Task Group: TG 1.2 Admin Match Inventory, Pricing, and QR
    // Contract: sequence-v1.md SEQ-002 default QR configuration; erd-v1.md ENT-007 one active default
    @PostMapping("/default")
    ApiResponse<PaymentQrConfigService.QrConfigResponse> setDefault(
            @RequestHeader("Authorization") String authorization,
            @RequestHeader(value = "Idempotency-Key", required = false) String idempotencyKey,
            @RequestBody SetDefaultQrRequest request,
            HttpServletRequest servletRequest) {
        if (idempotencyKey == null || idempotencyKey.isBlank() || idempotencyKey.length() > 120) {
            throw new ApiException(HttpStatus.BAD_REQUEST, ErrorCode.QR_CONFIG_INVALID_REQUEST,
                    "Idempotency-Key header is required for QR mutations.", "Idempotency-Key");
        }
        UUID actorUserId = adminActor.requireAdminUser(authorization);
        return new ApiResponse<>(paymentQrConfigService.setDefault(actorUserId, request.name(), request.qrAssetRef(),
                idempotencyKey, requestId(servletRequest), traceId(servletRequest)));
    }

    private String requestId(HttpServletRequest request) {
        return (String) request.getAttribute(RequestTraceFilter.REQUEST_ID_ATTRIBUTE);
    }

    private String traceId(HttpServletRequest request) {
        return (String) request.getAttribute(RequestTraceFilter.TRACE_ID_ATTRIBUTE);
    }

    record SetDefaultQrRequest(String name, String qrAssetRef) {
    }
}
