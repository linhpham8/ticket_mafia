package com.ticketmafia.shared;

import jakarta.servlet.http.HttpServletRequest;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger LOGGER = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(ApiException.class)
    // Sprint: v1 | Feature: FR-001,NFR-003 | US: US-001 | Task Group: TG 1.1 Foundation and Auth
    // Contract: project-reference-v1.md PR-003 REST error envelope; api-specs-v1.md API-001/API-002/API-016
    ResponseEntity<ErrorEnvelope> handleApiException(ApiException exception, HttpServletRequest request) {
        return ResponseEntity.status(exception.status()).body(envelope(
                exception.code(), exception.getMessage(), exception.details(), request));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<ErrorEnvelope> handleValidation(MethodArgumentNotValidException exception, HttpServletRequest request) {
        List<FieldViolation> details = exception.getBindingResult().getFieldErrors().stream()
                .map(this::toFieldViolation)
                .toList();
        return ResponseEntity.unprocessableEntity().body(envelope(
                ErrorCode.VALIDATION_ERROR.code(), "Request validation failed", details, request));
    }

    @ExceptionHandler(Exception.class)
    ResponseEntity<ErrorEnvelope> handleUnexpected(Exception exception, HttpServletRequest request) {
        LOGGER.error("Unhandled API exception requestId={} traceId={}",
                request.getAttribute(RequestTraceFilter.REQUEST_ID_ATTRIBUTE),
                request.getAttribute(RequestTraceFilter.TRACE_ID_ATTRIBUTE),
                exception);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(envelope(
                ErrorCode.INTERNAL_ERROR.code(), "Unexpected server error", null, request));
    }

    private FieldViolation toFieldViolation(FieldError error) {
        return new FieldViolation(error.getField(), error.getDefaultMessage());
    }

    private ErrorEnvelope envelope(String code, String message, Object details, HttpServletRequest request) {
        return new ErrorEnvelope(new ApiError(
                code,
                message,
                (String) request.getAttribute(RequestTraceFilter.REQUEST_ID_ATTRIBUTE),
                (String) request.getAttribute(RequestTraceFilter.TRACE_ID_ATTRIBUTE),
                details));
    }

    private record FieldViolation(String field, String message) {
    }
}
