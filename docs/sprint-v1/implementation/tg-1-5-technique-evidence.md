---
status: DRAFT
version: v1
sprint: 1
phase: implement
task_group: TG 1.5
created: 2026-06-08
updated: 2026-06-08
---

# TG 1.5 Technique Evidence — Purchase History, Ticket Detail, and One-Time Scan

## 1. Scope

| Field | Value |
|---|---|
| Task Group | TG 1.5 Purchase History, Ticket Detail, and One-Time Scan |
| Feature refs | FR-009, FR-010, BR-001, BR-006, BR-008, NFR-003 |
| User stories | US-009, US-010, US-011 |
| QA refs | TC-015, TC-016, TC-017, TC-018, TC-019, TC-020 |
| Repo test delta | Backend MockMvc integration tests; web component tests; Flutter widget tests |

## 2. Technique Evidence

| test_file | test_case | AC / requirement | techniques | observable_assertion |
|---|---|---|---|---|
| `backend/src/test/java/com/ticketmafia/ticket_scan/TicketScanApiIntegrationTest.java` | `purchaseHistoryShowsOnlyCurrentUserRecordsAndEmptyStateDoesNotLeakOtherUserData` | AC-017, AC-018 | EP + DT + ST + Security | Fan1 response contains only fan1 issued order/ticket; fan2 history response is empty. |
| `backend/src/test/java/com/ticketmafia/ticket_scan/TicketScanApiIntegrationTest.java` | `purchaseHistoryCursorPaginatesOrdersAndKeepsAllTicketsForReturnedOrder` | API-008, AC-017 | BVA + EP + DT | `limit=1` returns one order with all related ticket summaries and provides an opaque cursor for the next page. |
| `backend/src/test/java/com/ticketmafia/ticket_scan/TicketScanApiIntegrationTest.java` | `ticketDetailRequiresOwnershipAndReturnsSignedQrWithoutPlaintextPii` | AC-019, NFR-003 | EP + DT + ST + Security | Owner receives `tk_v1_` token without plaintext email/phone/name; other customer receives `TICKET_FORBIDDEN`. |
| `backend/src/test/java/com/ticketmafia/ticket_scan/TicketScanApiIntegrationTest.java` | `invalidTicketStatusesDoNotExposeEntryQr` | AC-020, BR-006 | EP + DT + ST | Cancelled ticket detail has null/empty QR and is not presented as valid entry ticket. |
| `backend/src/test/java/com/ticketmafia/ticket_scan/TicketScanApiIntegrationTest.java` | `firstValidScanMarksTicketUsedAndRepeatedScanIsRejected` | AC-021, AC-022, BR-006 | EP + DT + ST + Security | First admin scan returns `USED_SCANNED`, same idempotency key replays, new key repeat returns `TICKET_ALREADY_SCANNED`, and only one audit row exists. |
| `backend/src/test/java/com/ticketmafia/ticket_scan/TicketScanApiIntegrationTest.java` | `scanRequiresAdminRoleAndIdempotencyKey` | API-013, PR-005 | BVA + Negative + Security | Customer scan receives `SCAN_FORBIDDEN`; missing `Idempotency-Key` receives `SCAN_TOKEN_INVALID`; `scanSource` length > 120 receives `VALIDATION_ERROR`. |
| `website/src/features/tickets/components/TicketHistory.test.tsx` | `renders only returned order history rows and opens an issued QR detail` | AC-017, AC-019 | EP + DT | History renders returned owned order and opens issued QR card with API token. |
| `website/src/features/tickets/components/TicketHistory.test.tsx` | `shows empty state and suppresses QR for invalid ticket status` | AC-020 | EP + DT | Cancelled ticket detail shows invalid-entry message and no QR card. |
| `apps/test/ticket_history_screen_test.dart` | `ticket history opens issued QR detail and suppresses invalid QR` | SCREEN-009, SCREEN-010, AC-019, AC-020 | EP + DT | Flutter shell opens issued QR card, then hides QR for cancelled ticket and shows invalid-entry copy. |

## 3. Integration Surface Decision

| Surface | Integration test required? | Reason |
|---|---:|---|
| `GET /api/v1/orders` | Yes | Public authenticated API with ownership/security behavior. |
| `GET /api/v1/tickets/{ticketId}` | Yes | Public authenticated API exposing signed QR token and ownership guard. |
| `POST /api/v1/tickets/scan` | Yes | Public mutation API with transaction, idempotency, state guard, and audit persistence. |
| Web ticket UI | Component-level | UI consumes typed API service; no backend runtime in component test. |
| Flutter ticket UI | Widget-level | Mobile shell is static/demo-only in this repo state; API wiring is future service integration. |

## 4. Property / Invariant Coverage

| Surface | Classification | Evidence |
|---|---|---|
| QR token | property_or_examples | Example invariant: issued token starts with `tk_v1_`, is signed/opaque, and does not contain known user PII plaintext. |
| Scan state transition | property_or_examples | Example invariant: `ISSUED` can transition once to `USED_SCANNED`; repeated scan cannot produce a second success/audit event. |

## 5. Determinism

All tests use synthetic users, in-memory H2 profile or component/widget fixtures, deterministic session rows, no real network, no real external clock sleeps, and no production data.
