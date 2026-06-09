---
status: clean
version: v1
sprint: 1
phase: implement
mode: spec
cycle: tg-1-6
command: validate implementation --mode spec
created: 2026-06-08
updated: 2026-06-08
target_task_group: TG 1.6
blockers: 0
warnings: 2
conclusion: clean
---

# Validate Implementation Spec — TG 1.6 Seat Exchange and Local Demo Runtime

## 1. Target Fingerprint

| Field | Value |
|---|---|
| Command | `validate implementation --mode spec` |
| Cycle | `tg-1-6` |
| Target scope | TG 1.6 Seat Exchange and Local Demo Runtime |
| Plan source | `docs/sprint-v1/planning/implementation-plan-v1.md` §Task Group TG 1.6 |
| Product refs | FR-011, FR-012; US-012; AC-023, AC-024; BR-007, BR-008; NFR-002, NFR-005 |
| Architecture refs | API-014, API-015; ENT-003, ENT-004, ENT-005, ENT-008; SEQ-003, SEQ-004; PR-001, PR-003, PR-005 |
| Test refs | TC-021, TC-022, TC-024 |
| Evidence file | `docs/sprint-v1/implementation/tg-1-6-technique-evidence.md` |

### 1.1 File Hashes

| SHA-256 | File |
|---|---|
| `48f2ab98ba5e4ca4367b1c64c2e6fe5e760aa3091a355407d1797223aea9272e` | `backend/src/main/java/com/ticketmafia/order_payment/ExchangeCheckoutService.java` |
| `d6d000187c16377318ea2d3ff3771ff1afe366fa75525fed3f78c02e7f7fc85b` | `backend/src/main/java/com/ticketmafia/order_payment/AdminExchangeDecisionService.java` |
| `8a4ffe281402b24c162b13583f5ae27a59bf0351bdc5ee6d137eab457b59cd04` | `backend/src/main/java/com/ticketmafia/order_payment/AdminExchangeController.java` |
| `ad2468bddf29c9d8c106e5d4f2cb8f6c9995d625cf25961e31b73bcd90039ecb` | `backend/src/main/java/com/ticketmafia/ticket_scan/TicketController.java` |
| `19c8de1794aa2b2e2741413e6bfc21b431d45b8bbe4a40e191ca08c31ea2a9a3` | `backend/src/main/java/com/ticketmafia/ticket_scan/TicketIssuanceService.java` |
| `c3f8fe2254dbc02479cf116c30be8f438cd6b4ebd19a2a386ef0f3ddc8fc78ad` | `backend/src/test/java/com/ticketmafia/exchange/ExchangeApiIntegrationTest.java` |
| `9030ad8977e000b6c0d841b9b0dd9a442e87dffa2980b97c24a4b03cffcae52f` | `website/src/features/exchange/components/SeatExchange.tsx` |
| `f52de26fc078c56d9d19b04781f73e40c3a4140ae90df9bb8a964cc19626aa5e` | `website/src/features/exchange/services/exchange.api.ts` |
| `d9c34c753f37b560f12b49b11c8d86ecbad18cf449d438a2e47a8f3c508b4bc8` | `apps/lib/features/exchange/seat_exchange_screen.dart` |
| `f5da116c19d18c0d32f2ab07c628d7625bd7ca0704aaa7e3c2a71deeabbef967` | `docker-compose.yml` |
| `e57b91ac5b2d460e764f06579e6ae8f064da0bdc2928952749561f38e4cb1fe3` | `website/smoke-server.mjs` |
| `92495fa9ba6cac29ef51d1892c627d7e9739f151d7eebdef3f43dc8bb4faca94` | `docs/sprint-v1/implementation/tg-1-6-technique-evidence.md` |

## 2. Structural Coverage (`DOC-3`)

| Required item | Source | Evidence checked | Status |
|---|---|---|---|
| Task group exists and is approved for implementation | Plan TG 1.6 | `implementation-plan-v1.md` has status APPROVED and TG 1.6 with target modules, entrypoints, DOD, refs | covered |
| `POST /api/v1/tickets/{ticketId}/exchange/checkout` endpoint | API-014 | `TicketController.exchangeCheckout`; `ExchangeCheckoutService.checkout`; `ExchangeApiIntegrationTest` checkout assertions | covered |
| API-014 request schema | API-014 | path `ticketId`, body `newSeatId`, customer auth and `Idempotency-Key` checked in controller/service/tests | covered |
| API-014 response schema | API-014 | response record includes `orderId`, `type`, `priceDifferenceVnd`, `holdExpiresAt`, `paymentQr.assetRef`; tests assert type, amount, QR, replay | covered |
| API-014 errors | API-014 | missing idempotency, non-owner, cheaper seat, unavailable seat, state conflict covered by service/test paths | covered |
| `POST /api/v1/admin/exchanges/{orderId}/decision` endpoint | API-015 | `AdminExchangeController.decide`; `AdminExchangeDecisionService.decide`; confirm/reject tests | covered |
| API-015 request schema | API-015 | path `orderId`, body `decision`/`note`, admin auth and `Idempotency-Key` checked in controller/service/tests | covered |
| API-015 response schema | API-015 | response record includes `orderId`, `orderStatus`, `oldTicketId`, `newTicketId`; tests assert confirm and reject shapes | covered |
| Exchange eligibility rule | FR-011, BR-007, AC-024 | service compares replacement price against original ticket price; web/mobile disable ineligible seats; backend negative tests | covered |
| Old ticket validity until admin confirm | FR-012, AC-023 | checkout test verifies old ticket remains `ISSUED`; confirm test verifies transition to `EXCHANGED` | covered |
| Old seat release and new seat issuance | FR-012, SEQ-004 | admin exchange confirm updates old seat `AVAILABLE`, new seat `ISSUED`, old order item inactive; integration test verifies DB state | covered |
| DB contract | ENT-003, ENT-004, ENT-005, ENT-008 | implementation uses existing `orders.type=EXCHANGE`, `original_ticket_id`, `order_items.active`, `tickets.exchanged_to_ticket_id` | covered |
| Transaction and state guard | SEQ-003, SEQ-004, PR-005 | `@Transactional`, row locks, state checks, idempotency records, audit insert | covered |
| UI state coverage | SCREEN-012, SCREEN-008 | website `SeatExchange`, Flutter `SeatExchangeScreen`, admin confirmation exchange label/tests | covered with warning |
| Repo test delta | Plan repo_test_delta_target | backend integration, web component, Flutter widget test file, admin static scan, technique evidence | covered with warning |
| Docker Compose local self-test | NFR-005, CODE-10 | compose config/startup/health/smoke/teardown evidence in TG 1.6 evidence file | covered |

## 3. Rule Coverage

| Rule ID | Result | Evidence |
|---|---|---|
| `VAL-1` | covered | This file includes target fingerprint, structural coverage, rule coverage, findings, and conclusion. |
| `DOC-2` | covered | TG, FR, US, AC, API, TC IDs are stable and traceable. |
| `DOC-3` | covered | Required implementation surfaces checked in §2. |
| `LINK-1` | covered | Coverage and findings point to concrete files, commands, and contract IDs. |
| `LINK-2` | covered | Warnings include source, impact, and validation path. |
| `ORB-1` | covered | Sprint v1 context and TG 1.6 cycle recorded. |
| `CODE-1` | covered | Business-facing new services/controllers carry TG 1.6 traceability markers. |
| `CODE-3` | covered | Repo test delta exists for backend/web/mobile/admin surfaces. |
| `CODE-3a` | covered | Technique evidence table exists with observable assertions. |
| `CODE-3c` | covered | Exchange eligibility and state invariants are covered by explicit examples. |
| `CODE-10` | covered | Compose config, startup, health, smoke routes, and teardown recorded. |

## 4. Findings

| ID | Severity | Rule ID | Location | Finding | Impact | Required fix / validation path |
|---|---|---|---|---|---|---|
| SPEC-TG16-001 | warn | `LINK-2`, `DOC-3` | `ExchangeCheckoutService.checkout`; API-014/API-015 contract | API-014 creates an exchange order directly in `PENDING_ADMIN_CONFIRM` because API-015 requires a pending exchange order and no separate exchange payment-completed endpoint exists in approved API-014/API-015. | Behavior is internally consistent with the approved two-endpoint exchange surface and is documented in TG 1.6 evidence, but Product/Architecture may want an explicit exchange payment-completed step if the transfer confirmation must mirror purchase exactly. | If business requires a distinct user "payment completed" step for exchange, open an Architecture/Product change pack to add that API; current TG 1.6 spec validation does not block on this because API-014/API-015 remain satisfied. |
| SPEC-TG16-002 | warn | `CODE-3`, `DOC-3` | local environment | Flutter widget test could not be run because `flutter` is not on PATH in this shell. | Mobile shell spec is covered by source and test file, but this validate run lacks local execution evidence for Flutter. | Run `cd apps && flutter test test/seat_exchange_screen_test.dart` in a Flutter-enabled environment before relying on mobile execution evidence. |

## 5. Command Evidence

| Command | Result | Notes |
|---|---|---|
| `mvn test -Dtest=ExchangeApiIntegrationTest` | pass | 3 tests, 0 failures, 0 errors. |
| `npm test -- --run src/features/exchange/components/SeatExchange.test.tsx` | pass | 2 tests, 0 failures. |
| `npm test` in `admins/` | pass | Typecheck plus admin UI state scan passed. |
| `TICKETING_QR_SIGNING_SECRET=local-demo-signing-secret docker compose --profile local config --quiet` | pass | Compose syntax/profile is valid without reading protected secret files. |
| Prior TG 1.6 evidence: `mvn test` | pass | 37 backend tests, 0 failures, 0 errors. |
| Prior TG 1.6 evidence: `npm test` in `website/` | pass | 10 web tests, 0 failures. |
| Prior TG 1.6 evidence: Docker Compose startup/health/smoke/down | pass | postgres, backend, website, admins healthy; backend `/actuator/health`, website `/login` + `/tickets/exchange`, admin `/login` smoke routes passed; stack torn down. |
| `flutter test test/seat_exchange_screen_test.dart` | not runnable | `flutter` binary unavailable in this environment. |

## 6. Conclusion

Latest conclusion: `clean`.

Blockers: 0  
Warnings: 2

TG 1.6 clears `validate implementation --mode spec`. The implemented exchange checkout, admin exchange decision, state transitions, idempotency, ownership guards, UI state shells, repo test delta, and local Docker Compose smoke path match the approved Sprint v1 TG 1.6 scope. The remaining warnings do not block spec validation: exchange payment-completed semantics are an explicit API-surface ambiguity documented in the evidence, and Flutter execution needs a Flutter-enabled local environment.
