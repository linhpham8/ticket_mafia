---
status: IMPLEMENTED
version: v1
sprint: 1
phase: implement
task_group: TG 1.4
updated: 2026-06-08 17:08
---

# TG 1.4 Admin Payment Confirmation and Audit Evidence

## 1. Scope

- **Task Group**: TG 1.4 Admin Payment Confirmation and Audit
- **Feature / Story refs**: FR-008, BR-005, BR-008, NFR-004; US-008; AC-015, AC-016
- **Architecture refs**: API-007, SEQ-004, ENT-004, ENT-005, ENT-008, ENT-010, PR-005
- **Changed surfaces**: backend admin decision endpoint, pending list endpoint, ticket issuance, audit write, pending-confirmation expiry, admin confirmation UI route.

## 2. Repo Test Delta

| test_file | test_case | AC / requirement | techniques | observable_assertion |
|---|---|---|---|---|
| `backend/src/test/java/com/ticketmafia/order_payment/OrderPaymentApiIntegrationTest.java` | `adminConfirmPendingOrderIssuesTicketsAndWritesAudit` | AC-015, FR-008, API-007, ENT-008, ENT-010 | BVA + DT + ST + integration contract | Response status is `ISSUED`, two ticket IDs are returned, tickets persist, seat becomes `ISSUED`, audit row exists. |
| `backend/src/test/java/com/ticketmafia/order_payment/OrderPaymentApiIntegrationTest.java` | `adminRejectAndConfirmationExpiryReleaseSeats` | AC-016, BR-005 | BVA + EP + DT + ST | Reject returns `REJECTED`; expiry job returns `CANCELLED`; seats return `AVAILABLE`; order items inactive. |
| `backend/src/test/java/com/ticketmafia/order_payment/OrderPaymentApiIntegrationTest.java` | `adminDecisionRequiresPendingStateAdminRoleAndStableIdempotencyPayload` | PR-005, API-007 security / state guard | Negative + DT + Security | Non-pending decision returns `ORDER_NOT_PENDING_CONFIRM`; invalid decision returns `ADMIN_DECISION_INVALID_REQUEST`; non-admin gets `ADMIN_FORBIDDEN`. |
| `admins/test/admin-ui-state.test.mjs` | SCREEN-008 state/control assertions | SCREEN-008, DS-COMP-004, DS-COMP-005 | UI state inventory | Empty/loading/table/error state IDs and confirm/reject/filter controls are present. |

## 3. Runtime Evidence

| Check | Command | Result |
|---|---|---|
| Backend full test suite | `rtk mvn test` from `backend/` | Passed: 28 tests, 0 failures. |
| Admin UI typecheck + state tests | `rtk npm test` from `admins/` | Passed. |
| Docker Compose startup | `rtk docker compose --profile local up -d postgres backend admins` | Started `postgres`, `backend`, `admins`; backend health returned `{"status":"UP"}`. |
| Smoke reset | `rtk docker compose exec -T postgres psql -U ticket_mafia -d ticket_mafia < backend/src/test/resources/smoke/tg-1-4-admin-confirmation-reset.sql` | Passed; fixture rows removed. |
| Smoke seed | `rtk docker compose exec -T postgres psql -U ticket_mafia -d ticket_mafia < backend/src/test/resources/smoke/tg-1-4-admin-confirmation-seed.sql` | Passed; admin/customer sessions, match, seats, pending order, order items created. |
| Changed endpoint error path | `curl -X POST /api/v1/admin/orders/00000000-0000-4000-8000-000000000041/decision` without auth | Returned HTTP 401 with `AUTH_UNAUTHORIZED` error envelope and request/trace IDs. |
| Changed endpoint happy path | `curl -X POST /api/v1/admin/orders/00000000-0000-4000-8000-000000000041/decision` with `Authorization: Bearer tg14-admin-token` and `Idempotency-Key: tg14-confirm-001` | Returned HTTP 200 with `status: ISSUED` and 2 `ticketIds`. |
| Post-confirm DB state | SQL aggregate over `orders`, `order_items`, `seats`, `tickets`, `audit_logs` for seeded order | `order_status=ISSUED`, `ticket_count=2`, `audit_count=1`, `seat_statuses=ISSUED`. |
| Admin web smoke | `curl http://localhost:3001/login` | Returned admin login smoke HTML. |

## 4. Self-Review

- **CODE-1**: Traceability markers added to TG 1.4 controller/service/ticket/audit/scheduler code.
- **CODE-3a**: Technique evidence table included above.
- **CODE-3c**: State transition invariants covered by explicit examples for confirm, reject, expiry, idempotent replay, and role guard. Property testing is N/A because TG 1.4 is transaction/I/O orchestration rather than parser/validator/reducer logic.
- **CODE-10**: Local Compose path exists, starts, has explicit reset/seed SQL, and verifies the API-007 happy path plus unauthenticated error path against the Compose PostgreSQL database.

## 5. User Self-Test Steps

Before `validate implementation --mode spec`, this full local smoke path should pass:

```bash
rtk docker compose --profile local up -d postgres backend admins
rtk curl -fsS http://localhost:8080/actuator/health
rtk docker compose exec -T postgres psql -U ticket_mafia -d ticket_mafia < backend/src/test/resources/smoke/tg-1-4-admin-confirmation-reset.sql
rtk docker compose exec -T postgres psql -U ticket_mafia -d ticket_mafia < backend/src/test/resources/smoke/tg-1-4-admin-confirmation-seed.sql
rtk curl -i -sS -X POST http://localhost:8080/api/v1/admin/orders/00000000-0000-4000-8000-000000000041/decision \
  -H 'Authorization: Bearer tg14-admin-token' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: tg14-confirm-001' \
  -d '{"decision":"CONFIRM","note":"Local smoke confirmed"}'
rtk docker compose exec -T postgres psql -U ticket_mafia -d ticket_mafia -c "SELECT o.status AS order_status, COUNT(DISTINCT t.id) AS ticket_count, COUNT(DISTINCT a.id) AS audit_count, string_agg(DISTINCT s.status, ',') AS seat_statuses FROM orders o JOIN order_items oi ON oi.order_id = o.id JOIN seats s ON s.id = oi.seat_id LEFT JOIN tickets t ON t.order_id = o.id LEFT JOIN audit_logs a ON a.resource_id = o.id WHERE o.id = '00000000-0000-4000-8000-000000000041' GROUP BY o.status;"
rtk docker compose exec -T postgres psql -U ticket_mafia -d ticket_mafia < backend/src/test/resources/smoke/tg-1-4-admin-confirmation-reset.sql
rtk docker compose --profile local down
```

Expected API result: HTTP 200 with `data.status = ISSUED` and two `ticketIds`.

Expected DB result: `order_status=ISSUED`, `ticket_count=2`, `audit_count=1`, `seat_statuses=ISSUED`.
