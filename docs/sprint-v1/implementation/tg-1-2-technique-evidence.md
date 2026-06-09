---
status: DRAFT
version: v1
sprint: 1
phase: implement
task_group: TG 1.2
updated: 2026-06-08T15:15:05+07:00
---

# TG 1.2 Repo Test Delta Technique Evidence

| test_file | test_case | AC/requirement | technique | observable_assertion |
|---|---|---|---|---|
| `backend/src/test/java/com/ticketmafia/match_inventory/AdminInventoryApiIntegrationTest.java` | `adminCreatesOpenMatchGeneratesSeatsAndSetsPrice` | AC-011 / AC-013 / API-010..API-012 / PR-005 / QR default | Integration + Contract + State Transition | Admin creates `OPEN_FOR_SALE` match, generates `A-VIP-001..003`, sets active price, sets default QR, writes 4 audit logs and 4 idempotency records. |
| `backend/src/test/java/com/ticketmafia/match_inventory/AdminInventoryApiIntegrationTest.java` | `adminMutationReplaysSameIdempotencyKey` | API-010 / PR-005 | Contract + State Transition | Reusing the same `Idempotency-Key` returns the original match ID and creates only one match row. |
| `backend/src/test/java/com/ticketmafia/match_inventory/AdminInventoryApiIntegrationTest.java` | `customerCannotCallAdminMutation` | API-010 roles ADMIN / admin-only authorization | Security + Negative | Authenticated `CUSTOMER` session receives HTTP 403 `ADMIN_FORBIDDEN`. |
| `backend/src/test/java/com/ticketmafia/match_inventory/AdminInventoryApiIntegrationTest.java` | `adminMutationRequiresIdempotencyKey` | API-010 idempotency header required | Negative + Contract | Missing `Idempotency-Key` returns HTTP 400 `ADMIN_MATCH_INVALID_REQUEST`. |
| `backend/src/test/java/com/ticketmafia/match_inventory/AdminInventoryApiIntegrationTest.java` | `duplicateSeatGenerationIsBlockedForSameSlice` | API-011 / seat generation invariant | State Transition + Negative | Re-generating the same match/section/floor/VIP slice returns HTTP 409 `SEATS_ALREADY_EXIST`. |
| `backend/src/test/java/com/ticketmafia/match_inventory/AdminInventoryApiIntegrationTest.java` | `cancelledMatchBlocksPriceUpdates` | API-012 / BR-008 | Decision Table + Negative | `CANCELLED` match rejects price mutation with HTTP 409 `MATCH_PRICE_LOCKED`. |
| `backend/src/test/java/com/ticketmafia/match_inventory/InventoryServicesTest.java` | `seatCodeGenerationIsStableAndVipScopedToSectionA` | US-007 / seat code invariant | Example + Boundary | VIP and non-VIP generated codes use stable section/floor/index format. |
| `backend/src/test/java/com/ticketmafia/match_inventory/InventoryServicesTest.java` | `latestPriceUsesNewestActiveVersionForFutureCheckoutSnapshots` | AC-013 / AC-014 / BR-004 | State Transition + Regression | Latest price lookup returns `120000.00` after appending old then new price versions. |
| `backend/src/test/java/com/ticketmafia/match_inventory/InventoryServicesTest.java` | `paymentQrDefaultInvariantKeepsOneActiveRecord` | FR-007 / QR default invariant | State Transition | Setting two QR configs leaves exactly one default. |
| `admins/test/admin-ui-state.test.mjs` | executable UI state scan | SCREEN-006 / SCREEN-007 | Component surface smoke + State Inventory | Test asserts Empty, Loading, Populated, Error state IDs plus SCREEN-007 tabs and `Chọn QR mặc định` control are present. |
| `admins` | `npm test` | SCREEN-006 / SCREEN-007 compile contract | Static verification | Admin match and inventory pages typecheck through `tsc --noEmit` before the UI-state scan. |

## Runtime Smoke Evidence

| command | result | observable_assertion |
|---|---|---|
| `mvn test` in `backend` | Pass | 19 tests passed, including TG 1.2 admin inventory/QR integration/service tests, idempotency replay, and TG 1.1 auth regression tests. |
| `npm test` in `admins` | Pass | Admin Next app typechecks, then `admin-ui-state.test.mjs` verifies SCREEN-006 and SCREEN-007 state/control coverage. |
| `docker compose --profile local config` | Pass | Local compose configuration renders successfully with Postgres, backend, website, and admins services. |

## Implementation Notes

- Backend scope stayed inside `com.ticketmafia.match_inventory` plus the shared admin authorization/error-code extension required by API-010..API-012.
- Migrations added `matches`, `seats`, `price_versions`, and `payment_qr_configs`; H2 mirrors the schema for tests except PostgreSQL's partial QR default index, which is covered by service-level invariant test.
- `Idempotency-Key` is required and persisted in `idempotency_records` for admin match, seat generation, price, and QR mutations. Admin match/seat/price replay returns the previous successful resource instead of creating duplicates.
- Admin UI has operational routes for `/admin/matches` and `/admin/matches/{matchId}/inventory`; the inventory page includes tabs for `Ghế`, `Giá`, and `QR thanh toán` plus the default QR command control. Read data is currently local typed service data because TG 1.2 defines admin mutation APIs but no admin list/read API.
- Full Docker runtime startup and coverage threshold artifacts were not generated in this pass; use the validation commands below to audit remaining quality/spec evidence.
