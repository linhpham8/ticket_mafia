---
status: DRAFT
version: v1
sprint: 1
phase: implement
task_group: TG 1.1
updated: 2026-06-08T14:10:00+07:00
---

# TG 1.1 Repo Test Delta Technique Evidence

| test_file | test_case | AC/requirement | technique | observable_assertion |
|---|---|---|---|---|
| `backend/src/test/java/com/ticketmafia/auth/OtpServiceTest.java` | `normalizesEmailAndPhoneIdentifiers` | AC-001 / API-001 identifier validation | EP | Email is normalized to lowercase; VN-like phone is classified as `PHONE`. |
| `backend/src/test/java/com/ticketmafia/auth/OtpServiceTest.java` | `rejectsMalformedIdentifier` | API-001 error path | Negative | Malformed identifier throws `AUTH_IDENTIFIER_INVALID`. |
| `backend/src/test/java/com/ticketmafia/auth/OtpServiceTest.java` | `rateLimitsOtpRequestsPerIdentifierWindow` | API-001 rate limit | BVA+State Transition | The sixth request in a 10-minute identifier window throws HTTP 429 `RATE_LIMITED`. |
| `backend/src/test/java/com/ticketmafia/auth/OtpServiceTest.java` | `rejectsMalformedOtpBeforeCredentialCheck` | API-002 malformed OTP | Negative+EP | Non-numeric OTP returns HTTP 400 `AUTH_CHALLENGE_INVALID` before credential comparison. |
| `backend/src/test/java/com/ticketmafia/auth/OtpServiceTest.java` | `rateLimitsOtpVerificationAttemptsPerChallenge` | API-002 attempt limit | BVA+State Transition | Five wrong OTP attempts return `AUTH_OTP_INVALID`; the next attempt returns HTTP 429 `RATE_LIMITED`. |
| `backend/src/test/java/com/ticketmafia/auth/OtpServiceTest.java` | `rejectsDisabledUserAfterValidOtp` | API-002 disabled user | Decision Table+Negative | Valid OTP for a disabled account returns HTTP 403 `AUTH_FORBIDDEN` and no session token. |
| `backend/src/test/java/com/ticketmafia/auth/OtpServiceTest.java` | `refreshesActiveSessionAndRejectsExpiredInactiveSession` | NFR-003 inactive timeout | State Transition+BVA | Active lookup refreshes `last_seen_at` and expiry; a session past refreshed expiry is rejected. |
| `backend/src/test/java/com/ticketmafia/auth/AuthControllerIntegrationTest.java` | `mockOtpLoginSucceedsForEmail` | AC-001 / TC-001 | EP+DT+ST | OTP request returns a challenge; verify returns token, `CUSTOMER` role, and session expiry. |
| `backend/src/test/java/com/ticketmafia/auth/AuthControllerIntegrationTest.java` | `protectedCheckoutRequiresAuthentication` | AC-002 / API-005 / API-014 / API-016 | EP+DT+ST+Security | Unauthenticated protected checkout returns 401 with `AUTH_UNAUTHORIZED` envelope and no handler execution. |
| `backend/src/test/java/com/ticketmafia/auth/AuthControllerIntegrationTest.java` | `blankIdentifierReturnsContractError` | API-001 blank identifier | Negative+Contract | Blank identifier returns HTTP 400 `AUTH_IDENTIFIER_INVALID`, not framework validation 422. |
| `website/src/features/auth/components/LoginOtp.test.tsx` | `keeps CTA disabled until identifier is present` | SCREEN-001 Empty | State Transition | Empty state renders `login-empty` and disabled CTA. |
| `website/src/features/auth/components/LoginOtp.test.tsx` | `requests challenge then verifies demo OTP` | SCREEN-001 Populated / AC-001 | State Transition | Form moves through challenge request to successful verified state using two API calls. |
| `website/src/features/auth/components/LoginOtp.test.tsx` | `shows loading while requesting a challenge` | SCREEN-001 Loading | State Transition | Loading state renders `login-loading` with disabled `Đang gửi...` CTA. |
| `website/src/features/auth/components/LoginOtp.test.tsx` | `shows the contract error copy when OTP verification fails` | SCREEN-001 Error | Negative+State Transition | Failed OTP verification renders `login-error` and exact design error copy. |
| `apps/test/login_otp_screen_test.dart` | `login shell enables challenge request after identifier entry` | SCREEN-001 Mobile smoke | State Transition | Flutter login shell starts disabled, enables after identifier entry, and shows OTP field after challenge request. |

## Integration Test Applicability

Backend auth has public API and DB integration surfaces, so MockMvc + Flyway/H2 integration tests are included. Flutter widget test coverage is now present under `apps/test/`, but local execution still requires a Flutter SDK on the machine.

## Runtime Smoke Evidence

| command | result | observable_assertion |
|---|---|---|
| `docker compose --profile local config` | Pass | Local profile renders with Postgres, backend, website, and admin services. |
| `docker compose --profile local up -d postgres backend website admins` | Pass | Postgres/backend become healthy; website Vite login harness and admin smoke shell respond within bounded validation. |
| `curl -fsSI http://localhost:3000/screenshot-harness.html` | Pass | User login shell harness returns HTTP 200. |
| `curl -fsSI http://localhost:3001/login` | Pass | Admin login shell returns HTTP 200. |
| `POST /api/v1/auth/otp/request` then `POST /api/v1/auth/otp/verify` with `000000` | Pass | Challenge is issued; verify returns access token, `CUSTOMER` role, and session expiry. |
| `POST /api/v1/orders/checkout` without auth | Pass | Protected checkout returns HTTP 401 with `AUTH_UNAUTHORIZED`, requestId, and traceId. |
| `mvn spring-boot:run -Dspring-boot.run.profiles=test` | Pass | Backend starts with main-resource H2 smoke profile; `/actuator/health` returns `UP`. |
| `npm run screenshots:login` | Pass | SCREEN-001 Empty, Loading, Populated, and Error screenshots saved under `docs/sprint-v1/implementation/screenshots/tg-1-1/`. |
| `flutter test` in `apps` | Waived for TG 1.1 spec validation | User explicitly accepted skipping app tests for this slice and requiring web/backend validation only. Flutter widget test file remains present for later execution when SDK is available. |

## Property / Example Selection

Identifier validation is a small business validator, so explicit EP/negative examples are used instead of property-based tests. No parser, serializer, reducer, or non-trivial algorithm in TG 1.1 requires a property test.
