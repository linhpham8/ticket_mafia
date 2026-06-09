package com.ticketmafia.shared;

public record ApiError(String code, String message, String requestId, String traceId, Object details) {
}
