package com.ticketmafia.auth;

import com.ticketmafia.shared.ApiResponse;
import java.time.Instant;
import java.util.UUID;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/auth/otp")
public class AuthController {
    private final OtpService otpService;

    public AuthController(OtpService otpService) {
        this.otpService = otpService;
    }

    // Sprint: v1 | Feature: FR-001,NFR-003 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
    // Contract: api-specs-v1.md API-001 POST /api/v1/auth/otp/request | Project: project-reference-v1.md PR-003
    @PostMapping("/request")
    ApiResponse<OtpRequestResponse> requestOtp(@RequestBody OtpRequest request) {
        OtpChallenge challenge = otpService.requestOtp(request.identifier());
        return new ApiResponse<>(new OtpRequestResponse(challenge.challengeId(), challenge.expiresAt()));
    }

    // Sprint: v1 | Feature: FR-001,NFR-003 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
    // Contract: api-specs-v1.md API-002 POST /api/v1/auth/otp/verify | Project: project-reference-v1.md PR-003
    @PostMapping("/verify")
    ApiResponse<OtpVerifyResponse> verifyOtp(@RequestBody OtpVerifyRequest request) {
        return new ApiResponse<>(otpService.verifyOtp(request.challengeId(), request.otp()));
    }

    record OtpRequest(String identifier) {
    }

    record OtpRequestResponse(UUID challengeId, Instant expiresAt) {
    }

    record OtpVerifyRequest(String challengeId, String otp) {
    }
}
