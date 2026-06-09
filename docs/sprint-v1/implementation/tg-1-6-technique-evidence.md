---
status: DRAFT
version: v1
sprint: 1
phase: implement
task_group: TG 1.6
created: 2026-06-08
updated: 2026-06-08 22:01
---

# TG 1.6 Technique Evidence — Seat Exchange and Local Demo Runtime

## 1. Scope

| Field | Value |
|---|---|
| Task Group | TG 1.6 Seat Exchange and Local Demo Runtime |
| Feature refs | FR-011, FR-012, BR-007, BR-008, NFR-002, NFR-005 |
| User stories | US-012 |
| API refs | API-014, API-015 |
| Architecture refs | ENT-003, ENT-004, ENT-005, ENT-008, SEQ-003, SEQ-004, PR-001, PR-003, PR-005 |
| Code surfaces | `backend` exchange checkout/admin decision, `website` exchange shell, `admins` exchange confirmation state, `apps` exchange shell, `docker-compose.yml` |

## 2. Repo Test Delta

| test_file | test_case | AC / requirement | techniques | observable_assertion |
|---|---|---|---|---|
| `backend/src/test/java/com/ticketmafia/exchange/ExchangeApiIntegrationTest.java` | `higherPricedExchangeCheckoutHoldsReplacementSeatAndAdminConfirmRetiresOldTicket` | AC-023, API-014, API-015, BR-007 | BVA + EP + DT + ST + SIT | higher-price difference is 50,000 VND, old ticket remains `ISSUED` until confirm, old ticket becomes `EXCHANGED`, old seat returns `AVAILABLE`, new seat becomes `ISSUED`, audit row exists |
| `backend/src/test/java/com/ticketmafia/exchange/ExchangeApiIntegrationTest.java` | `equalPricedExchangeRequiresNoPaymentQrAndRejectKeepsOldTicketIssued` | AC-023, API-014, API-015 | BVA + DT + ST + Negative | equal-price exchange returns 0 VND and no QR; reject releases replacement seat and keeps old ticket `ISSUED` |
| `backend/src/test/java/com/ticketmafia/exchange/ExchangeApiIntegrationTest.java` | `cheaperUnavailableAndUnauthorizedExchangeTargetsAreBlockedBeforeCheckout` | AC-024, BR-007, API-014 | EP + DT + Negative + Security | cheaper seat returns `EXCHANGE_CHEAPER_SEAT_NOT_ALLOWED`, unavailable target returns conflict, non-owner returns `TICKET_FORBIDDEN`, no exchange order is created |
| `website/src/features/exchange/components/SeatExchange.test.tsx` | `allows only equal-or-higher available seats and submits exchange checkout` | SCREEN-012, AC-023, API-014 | EP + DT + Component | cheaper/unavailable seats are disabled; eligible seat calls typed exchange API with `Idempotency-Key` |
| `website/src/features/exchange/components/SeatExchange.test.tsx` | `renders empty and blocked states from SCREEN-012` | SCREEN-012, AC-024 | EP + Negative | empty state copy and blocked exchange error copy render with stable test IDs |
| `apps/test/seat_exchange_screen_test.dart` | `seat exchange blocks cheaper and unavailable seats then continues eligible seat` | SCREEN-012, AC-023, AC-024 | EP + DT + Widget | cheaper and held buttons are disabled; eligible seat advances to created exchange state |
| `admins/test/admin-ui-state.test.mjs` | admin confirmation static state check | SCREEN-008 exchange confirm | N/A — static UI contract scan | admin page includes `Xác nhận đổi ghế` exchange confirmation control |

## 3. Property / Invariant Selection

| Surface | Decision | Reason |
|---|---|---|
| Exchange eligibility | Example-set instead of property test | Small business rule with concrete invariant examples: higher allowed, equal allowed, cheaper blocked, unavailable blocked |
| Exchange state transition | Example-set instead of property test | State machine is integration-backed; observable states are asserted across DB rows and API responses |
| Docker Compose smoke | N/A | Runtime health/self-test path, not pure algorithmic logic |

## 4. Runtime Smoke Evidence

| Check | Command | Result |
|---|---|---|
| Compose config | `TICKETING_QR_SIGNING_SECRET=local-demo-signing-secret docker compose --profile local config --quiet` | pass |
| Compose startup | `TICKETING_QR_SIGNING_SECRET=local-demo-signing-secret docker compose --profile local up -d` | pass |
| Backend health | `curl -fsS http://localhost:8080/actuator/health` | `{"status":"UP"}` |
| Website smoke | `curl -fsS http://localhost:3000/login`; `curl -fsS http://localhost:3000/tickets/exchange` | pass |
| Admin smoke | `curl -fsS http://localhost:3001/login` | pass |
| Compose health | `docker compose --profile local ps` | postgres, backend, website, admins healthy after Node healthcheck fix |
| Teardown | `TICKETING_QR_SIGNING_SECRET=local-demo-signing-secret docker compose --profile local down` | pass |

## 5. Auto-Test Summary

| Step | Command | Result |
|---|---|---|
| backend integration | `mvn test -Dtest=ExchangeApiIntegrationTest` | pass — 3 tests, 0 failures |
| backend regression | `mvn test` | pass — 37 tests, 0 failures |
| website component | `npm test -- --run src/features/exchange/components/SeatExchange.test.tsx` | pass — 2 tests, 0 failures |
| website regression | `npm test` | pass — 10 tests, 0 failures |
| website typecheck | `npm run lint` | pass |
| admin typecheck/state scan | `npm test` in `admins/` | pass |
| Docker Compose smoke | commands in §4 | pass |
| Flutter widget | `flutter test test/seat_exchange_screen_test.dart` | not run locally — `flutter` command unavailable in environment |

## 6. Notes

- API-014 creates a `PENDING_ADMIN_CONFIRM` exchange order with a 10-minute confirmation window because the approved API surface has no separate exchange payment-completed endpoint, while API-015 requires a pending exchange order.
- Website Compose uses a deterministic smoke server for local profile health, matching the existing admin smoke-server pattern. The real Next exchange component is covered by TypeScript and Vitest.
- Mutation testing suggestion: optional PIT for backend exchange services plus StrykerJS for the web exchange component, estimated 20-30 minutes for the focused slice.
