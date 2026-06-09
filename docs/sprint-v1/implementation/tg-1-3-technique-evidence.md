---
status: DRAFT
version: v1
sprint: 1
phase: implement
task_group: TG 1.3
created: 2026-06-08
updated: 2026-06-08T16:27:30+07:00
---

# TG 1.3 Repo Test Delta Technique Evidence

| test_file | test_case | AC / requirement | technique | observable_assertion |
|---|---|---|---|---|
| `backend/src/test/java/com/ticketmafia/order_payment/OrderPaymentApiIntegrationTest.java` | `matchListAndSeatMapExposeOnlySellableInventoryWithCurrentPrice` | AC-003, AC-004, AC-005 / API-003, API-004 | EP + contract | Response contains only `OPEN_FOR_SALE` match, always-present `meta.nextCursor`, and seat rows include current active price. |
| `backend/src/test/java/com/ticketmafia/order_payment/OrderPaymentApiIntegrationTest.java` | `checkoutHoldsSeatsSnapshotsPriceAndReplaysIdempotencyKey` | AC-007 / API-005 / BR-004 / PR-005 / SEQ-003 | State Transition + idempotency + contract | Checkout returns `HELD`, stores one order, same request hash replays the same order ID, and mismatched request hash conflicts. |
| `backend/src/test/java/com/ticketmafia/order_payment/OrderPaymentApiIntegrationTest.java` | `checkoutBlocksSixSeatsAndUnavailableSeats` | AC-006, AC-007 / BR-003 / NFR-002 | BVA + Negative | Six-seat request returns `CHECKOUT_LIMIT_EXCEEDED`; second checkout on held seat returns `SEAT_UNAVAILABLE`. |
| `backend/src/test/java/com/ticketmafia/order_payment/OrderPaymentApiIntegrationTest.java` | `paymentCompletionMovesHeldOrderToPendingAndRequiresOwnership` | AC-009, AC-010 / API-006 | State Transition + Negative | Other user receives `ORDER_FORBIDDEN`; owner moves order and seat to `PENDING_ADMIN_CONFIRM`. |
| `backend/src/test/java/com/ticketmafia/order_payment/OrderPaymentApiIntegrationTest.java` | `releaseExpiredHoldsReturnsSeatsToAvailable` | AC-008 / BR-002 / NFR-002 | State Transition + time-boundary | Expired order becomes `EXPIRED`, order item inactive, and seat returns to `AVAILABLE`. |
| `backend/src/test/java/com/ticketmafia/order_payment/OrderPaymentConcurrencyPostgresIntegrationTest.java` | `concurrentCheckoutPermitsOnlyOneActiveHoldPerSeat` | NFR-002 / TC-023 / API-005 | Concurrent integration + Corner | PostgreSQL/Testcontainers executes two concurrent checkout attempts for the same available seat; exactly one succeeds and exactly one active order item remains. |
| `website/src/features/matches/components/MatchCheckoutFlow.test.tsx` | `loads matches and blocks selecting a sixth seat` | AC-005, AC-006 / SCREEN-003 | BVA + component integration | UI blocks the sixth seat and keeps selected seat count at 5. |
| `website/src/features/matches/components/MatchCheckoutFlow.test.tsx` | `creates checkout and moves to pending confirmation` | AC-007, AC-009 / SCREEN-004, SCREEN-005 | State Transition + component integration | UI reaches QR state, submits payment-completed, and shows pending confirmation. |
| `website/src/features/auth/components/LoginOtp.test.tsx` | `requests challenge then verifies demo OTP` | NFR-003 / frontend security session handling | Security regression + component integration | OTP success stores the access token in in-memory `authSession` instead of browser storage. |
| `website/src/features/matches/components/MatchCheckoutFlow.screenshot.spec.ts` | `captures SCREEN-002..SCREEN-005 state screenshots` | SCREEN-002, SCREEN-003, SCREEN-004, SCREEN-005 | Visual state evidence | Playwright captures 16 screenshots covering Empty, Loading, Populated, and Error states for the TG 1.3 web flow. |

Integration surface: required and covered by MockMvc + H2-backed Spring integration tests for public APIs, DB state transitions, idempotency, and scheduler release behavior, plus PostgreSQL/Testcontainers for the concurrent hold invariant. Property-based testing: N/A — TG 1.3 has stateful DB transaction flows; boundary/invariant examples cover the 1-5 seat limit, price snapshot, idempotency request hash, and hold state invariants.

Runtime evidence:

- Backend full suite: `mvn -q test` passed on 2026-06-08T16:08:36+07:00.
- Website checks: `npm run lint`, `npm test`, and `npm run screenshots:matches` passed on 2026-06-08T16:27:30+07:00 with 16 Playwright screenshots under `docs/sprint-v1/implementation/screenshots/tg-1-3/`.
- Docker Compose smoke: local `postgres` + `backend` stack reached `{"status":"UP"}` and exercised API-003 metadata, checkout replay, idempotency mismatch, duplicate-seat conflict, and payment-completed.
- Flutter/mobile runtime: not executed in this environment because `flutter` and `dart` are not installed.
