---
status: clean
version: v1
sprint: 1
phase: implement
mode: spec
cycle: tg-1-5
command: validate implementation --mode spec
created: 2026-06-08
updated: 2026-06-08
target_task_group: TG 1.5
blockers: 0
warnings: 2
conclusion: clean
---

# Validate Implementation Spec — TG 1.5 Purchase History, Ticket Detail, and One-Time Scan

## 1. Target Fingerprint

| Field | Value |
|---|---|
| Command | `validate implementation --mode spec` |
| Cycle | `tg-1-5` |
| Target scope | TG 1.5 Purchase History, Ticket Detail, and One-Time Scan |
| Plan source | `docs/sprint-v1/planning/implementation-plan-v1.md` §Task Group TG 1.5 |
| Product refs | FR-009, FR-010; US-009, US-010, US-011; AC-017..AC-022; BR-001, BR-006, BR-008; NFR-003 |
| Architecture refs | API-008, API-009, API-013; ENT-008, ENT-009; SEQ-005; PR-004, PR-005 |
| Test refs | TC-015, TC-016, TC-017, TC-018, TC-019, TC-020 |
| Evidence file | `docs/sprint-v1/implementation/tg-1-5-technique-evidence.md` |

### 1.1 File Hashes

| SHA-256 | File |
|---|---|
| `946add1bf6cccb50635a1d1def9f4e101ea9fc10a3ef301e11ea7ddec3cf63b2` | `backend/src/main/java/com/ticketmafia/ticket_scan/TicketController.java` |
| `cf9eb90315607165f3c895957ac518424b3a52bc38651d2036c01c0f865b6576` | `backend/src/main/java/com/ticketmafia/ticket_scan/OrderHistoryService.java` |
| `28212e09cdaef245c72de41651cee5425a8fbc2aeb7326ba1fbeb4307448fa9e` | `backend/src/main/java/com/ticketmafia/ticket_scan/TicketDetailService.java` |
| `46fb91d9c060cafdc9b0e7581df8d07cb9cb48514d162f3d8ea37bea23307d97` | `backend/src/main/java/com/ticketmafia/ticket_scan/TicketScanService.java` |
| `c79f4b92a0597383fb5da28972f4c1e62f5f044b575524d60de913c94d6cf4d7` | `backend/src/main/java/com/ticketmafia/ticket_scan/QrTokenService.java` |
| `2a99b284d4d2ffaf0e27c3e78ea8621476cf003f51d5b137bb03872fcc87f6d5` | `backend/src/main/java/com/ticketmafia/ticket_scan/TicketIdempotencyService.java` |
| `eb60e4b24bdf8c10288a69a2090e7e326c5feedfd63576d7941783f0b5a1d502` | `backend/src/main/java/com/ticketmafia/ticket_scan/TicketIssuanceService.java` |
| `f5110f24087ae2d27a746cb234a20ca61ff164e2569cd4f2c5a5bdf3784f6d21` | `backend/src/test/java/com/ticketmafia/ticket_scan/TicketScanApiIntegrationTest.java` |
| `3ec41849c173e8a4b1e2817788f965508258acbd44e0dde39f24ea31118b0324` | `website/src/features/tickets/components/TicketHistory.tsx` |
| `23e95477068a36516f72611fb5debf1d538364a228c0865996659d1df2d84a79` | `website/src/features/tickets/components/TicketHistory.test.tsx` |
| `cd767b7686a6bff76d0e236239b4017b727cbf3a12516d209973730d304c1552` | `website/src/features/tickets/components/TicketHistory.screenshot.spec.ts` |
| `b9fdd1aa89f6f54b486438965884009aff77d9f484cf7505526a0cbba08bfec3` | `website/src/features/tickets/services/tickets.api.ts` |
| `e58486b52420c1e6e4907c8eac8e2cb865df3b346a535bb287cb51c894bd9960` | `apps/lib/features/tickets/ticket_history_screen.dart` |
| `66c54eaf4df65e1eb7235f43eb96858b6e0a84e7e2b40bd1f619021bd126df7b` | `apps/test/ticket_history_screen_test.dart` |
| `314601927f7c3cec93a782e4c28de8810a901cc77613e9260753dba9bab51a74` | `docs/sprint-v1/implementation/tg-1-5-technique-evidence.md` |

## 2. Structural Coverage (`DOC-3`)

| Required item | Source | Evidence checked | Status |
|---|---|---|---|
| Task group exists and is approved for implementation | Plan TG 1.5 | `implementation-plan-v1.md` has status APPROVED and TG 1.5 with target modules, entrypoints, DOD, refs | covered |
| `GET /api/v1/orders` endpoint | API-008 | `TicketController.orders`; `OrderHistoryService.list`; `TicketScanApiIntegrationTest.purchaseHistoryCursorPaginatesOrdersAndKeepsAllTicketsForReturnedOrder` | covered |
| API-008 cursor pagination | API-008 | Controller accepts `cursor`; service decodes opaque cursor, fetches `limit + 1` orders, returns `meta.nextCursor`; integration test covers next-page cursor behavior | covered |
| API-008 related ticket summaries | API-008 | Orders are paged first, then all ticket summaries for returned orders are fetched by order IDs; integration test covers multi-ticket order with `limit=1` | covered |
| `GET /api/v1/tickets/{ticketId}` endpoint | API-009 | `TicketController.ticket`; `TicketDetailService.detail`; ownership and QR tests | covered |
| `POST /api/v1/tickets/scan` endpoint | API-013 | `TicketController.scan`; `TicketScanService.scan`; scan tests | covered |
| API-013 `scanSource` schema | API-013 | `TicketScanService.normalizeScanSource`; integration test covers overlong `scanSource` returning `VALIDATION_ERROR` | covered |
| DB contract for tickets and idempotency | ENT-008, ENT-009 | `tickets.qr_token_hash`, `tickets.status`, `scanned_at`, `idempotency_records` references in services/tests | covered |
| Transaction and state guard | SEQ-005 | `@Transactional`, `FOR UPDATE`, `status = 'ISSUED'`, audit insert | covered |
| Security and ownership | BR-001, NFR-003 | customer ownership checks, admin scan guard, signed opaque token tests | covered |
| Repo test delta | Plan repo_test_delta_target | backend integration, web component, Flutter widget tests, technique evidence | covered with warning |
| Runtime local self-test path | CODE-10 | Docker Compose local profile backend health + API unauthenticated error check | covered |

## 3. Rule Coverage

| Rule ID | Result | Evidence |
|---|---|---|
| `VAL-1` | covered | This file includes target fingerprint, structural coverage, rule coverage, findings, and conclusion. |
| `DOC-2` | covered | TG, FR, US, AC, API, TC IDs are stable and traceable. |
| `DOC-3` | covered | Required implementation surfaces checked in §2. |
| `LINK-1` | covered | Coverage and findings point to concrete files, commands, and contract IDs. |
| `LINK-2` | covered | Remaining warnings include source, impact, and validation path. |
| `ORB-1` | covered | Sprint v1 context and TG 1.5 cycle recorded. |
| `CODE-1` | covered | Business-facing new services/controllers carry TG 1.5 traceability markers. |
| `CODE-3` | covered | Repo test delta exists for backend/web/mobile surfaces. |
| `CODE-3a` | covered | Technique evidence table exists with observable assertions. |
| `CODE-3c` | covered | QR token and scan state invariants documented. |
| `CODE-10` | covered | Compose startup and backend endpoint evidence recorded. |

## 4. Findings

| ID | Severity | Rule ID | Location | Finding | Impact | Required fix / validation path |
|---|---|---|---|---|---|---|
| SPEC-TG15-004 | warn | `DOC-3`, `LINK-2` | `backend/src/main/java/com/ticketmafia/ticket_scan/TicketController.java` | API-013 says roles `ADMIN / SCANNER` and auth can be a trusted demo scanner token, but the implementation accepts only role `ADMIN`. | The current v1 schema appears to support only `CUSTOMER` and `ADMIN`, so this is likely an upstream contract inconsistency rather than an implementation blocker for TG 1.5. | Either amend Architecture/API to say admin-only scanner for v1, or add a scanner role/token path and tests in a later scoped change. |
| SPEC-TG15-005 | warn | `CODE-3`, `CODE-10` | local environment | Flutter widget test could not be run because `flutter` is not on PATH in this shell. | Mobile shell spec is covered by code/test files but lacks local execution evidence in this validate run. | Run `cd apps && flutter test test/ticket_history_screen_test.dart` in a Flutter-enabled environment before relying on mobile execution evidence. |

## 5. Resolved Blocker Recheck

| Prior ID | Recheck result | Evidence |
|---|---|---|
| SPEC-TG15-001 | resolved | API-008 now accepts `cursor`, returns real `meta.nextCursor`, and focused backend integration tests pass. |
| SPEC-TG15-002 | resolved | API-008 now pages orders before ticket-summary fetch; `purchaseHistoryCursorPaginatesOrdersAndKeepsAllTicketsForReturnedOrder` verifies `limit=1` keeps all tickets for the returned order. |
| SPEC-TG15-003 | resolved | API-013 now normalizes and validates `scanSource`; overlong value returns `VALIDATION_ERROR` in integration coverage. |

## 6. Command Evidence

| Command | Result | Notes |
|---|---|---|
| `mvn test -Dtest=TicketScanApiIntegrationTest` | pass | 6 tests, 0 failures, 0 errors. |
| `npm test -- TicketHistory.test.tsx` | pass | 2 tests, 0 failures. |
| `npm run screenshots:tickets` | pass | 4 Playwright screenshot tests passed; screenshots in `docs/sprint-v1/implementation/screenshots/tg-1-5/`. |
| `docker compose --profile local up -d postgres backend` | pass | PostgreSQL became healthy and backend started. |
| `curl http://localhost:8080/actuator/health` | pass | returned `{"status":"UP"}`. |
| `curl http://localhost:8080/api/v1/orders` without auth | pass | returned HTTP 401 with `AUTH_UNAUTHORIZED` envelope. |
| `docker compose --profile local down` | pass | local profile containers and network removed. |
| `command -v flutter` | not runnable | no Flutter binary found in shell PATH. |

## 7. Conclusion

Latest conclusion: `clean`.

Blockers: 0  
Warnings: 2

TG 1.5 clears `validate implementation --mode spec`. The three previous blocker findings are resolved and covered by current integration/runtime evidence. The remaining warnings do not block spec validation: API-013 scanner-role wording should be reconciled with the v1 auth model, and Flutter widget execution still requires a Flutter-enabled local environment.
