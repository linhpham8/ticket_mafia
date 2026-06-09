---
status: ACTIVE
phase: implement
mode: spec
sprint: 1
task_group: TG 1.2
cycle: tg-1-2
updated: 2026-06-08T15:16:15+07:00
conclusion: clean
---

# Validate Implementation Spec: TG 1.2 Admin Match Inventory, Pricing, and QR

## 1. Target

| Field | Value |
|---|---|
| Command | `validate implementation --mode spec` |
| Scope | TG 1.2 Admin Match Inventory, Pricing, and QR |
| HEAD | `8225310` |
| Diff base | Current working tree |
| Worktree note | Dirty worktree; validation targets current working tree including untracked implementation files. |
| Plan target | `docs/sprint-v1/planning/implementation-plan-v1.md` TG 1.2 |
| Contract refs | FR-006, FR-007, US-006, US-007, AC-011..AC-014, BR-004, BR-008, API-010..API-012, ENT-002, ENT-003, ENT-006, ENT-007, ENT-010, SEQ-002, PR-002, PR-003, PR-005, SCREEN-006, SCREEN-007, TC-003..TC-006 |
| Code surfaces inspected | `backend/src/main/java/com/ticketmafia/match_inventory/**`, `backend/src/main/java/com/ticketmafia/shared/**`, migrations, `backend/src/test/java/com/ticketmafia/match_inventory/**`, `admins/src/**`, `admins/test/**`, `docker-compose.yml`, `docs/sprint-v1/implementation/tg-1-2-technique-evidence.md` |

## 2. Structural Coverage (`DOC-3`)

| Artifact / area | Expected contract | Required sections / fields checked | Missing | N/A with reason |
|---|---|---|---|---|
| Product package | FR-006 / US-006 / AC-011..AC-012; FR-007 / US-007 / AC-013..AC-014 | Admin match creation/status, seat generation, active price update, one default transfer QR | none | User browse/checkout API proof for AC-011/012/013/014 is primarily TG 1.3; TG 1.2 now provides the inventory/pricing/QR source of truth. |
| Architecture API | API-010, API-011, API-012 | Paths, auth role, request fields, response fields, idempotency header, error matrix | none | QR default endpoint is not separately numbered in API-010..012, but is required by TG 1.2 deliverable and SEQ-002 and stays in admin inventory/QR scope. |
| ERD / migration | ENT-002, ENT-003, ENT-006, ENT-007, ENT-010 | Tables and core columns exist in PostgreSQL and H2 migrations | none | H2 omits PostgreSQL partial default-QR index; service test covers one-default invariant. |
| Sequence | SEQ-002 | TX service methods, audit log writes, idempotency record writes, QR config path | none | none |
| Design | SCREEN-006, SCREEN-007 | Required state identifiers, tabs, QR default command control | none | Visual screenshot evidence not captured in this pass. |
| Plan | TG 1.2 task fields | Modules, entrypoints, allowed diff, affected surfaces, repo test delta, DOD | none | none |
| Test package | TC-003, TC-004, TC-005, TC-006 | Backend integration/service tests, admin UI-state test, evidence table | none | Full checkout/browser end-to-end assertions for API-003/API-005 remain TG 1.3 scope. |
| Runtime | Spec-mode runtime verification | Backend tests, admin typecheck/UI-state test, Compose local profile config | none | Full Docker startup + live curl smoke not captured in this validate pass. |

## 3. Runtime / Static Evidence

| Check | Result | Evidence |
|---|---|---|
| Backend tests | pass | `mvn test` in `backend`: 19 tests, 0 failures, build success. |
| Admin static + UI-state check | pass | `npm test` in `admins`: `tsc --noEmit` plus `node test/admin-ui-state.test.mjs` completed with exit 0. |
| Docker Compose config | pass | `docker compose --profile local config` rendered Postgres, backend, website, and admins services. |
| Technique evidence | pass | `docs/sprint-v1/implementation/tg-1-2-technique-evidence.md` maps backend/admin tests to AC/API/requirements. |
| Full runtime smoke | warn | Not run in this validate pass: no Docker-backed live `POST /api/v1/admin/matches`, seat generation, price update, or QR default curl smoke captured. |

## 4. Rule Coverage (`VAL-1`)

| Rule ID / surface | Scope checked | Result | Notes |
|---|---|---|---|
| VAL-1 | Validate file evidence contract | pass | This report includes target fingerprint, structural coverage, rule coverage, findings, and conclusion. |
| DOC-3 | Expected implementation validation areas | pass | Product, API, ERD, sequence, design, plan, test, and runtime areas are listed with missing/N-A evidence. |
| LINK-1 / LINK-2 | Cross-artifact traceability | pass | QR requirement now links from plan/design/sequence to backend route/service and admin UI control. |
| ORB-1 | Sprint context | pass | Sprint v1 and TG 1.2 context recorded. |
| Product / US / AC | FR-006, FR-007, AC-011..AC-014 | pass | Admin match/seat/price/QR source-of-truth behavior is implemented and tested. |
| API contract | API-010..API-012 / PR-005 | pass | Main endpoint paths/fields exist; idempotency key replay is tested for admin match mutation; required auth/error paths are covered. |
| ERD / migration | ENT-002, ENT-003, ENT-006, ENT-007, ENT-010 | pass static | PostgreSQL migration includes required tables; H2 mirrors for tests except partial QR index. |
| Sequence | SEQ-002 | pass | Admin match/seat/price/QR services are transactional, audited, and idempotency-recorded. |
| Design contract | SCREEN-006, SCREEN-007 | pass | Required state IDs, tabs, and QR default command control are present and checked by admin UI-state test. |
| CODE-1 | Traceability markers | pass static | Business-facing backend services/controllers/migration and admin service carry TG 1.2 markers. |
| CODE-3 / CODE-3a | Repo test delta and technique evidence | pass | Backend service/integration tests and admin UI-state test exist with evidence. |
| CODE-3b | Coverage target | warn | Local commands did not generate line/branch coverage artifacts for new code. |
| CODE-3c | Property/example selection | pass | Seat-code and QR default invariants have explicit example/state tests. |
| CODE-10 | Local Docker Compose self-test path | warn | Compose local profile exists and renders; full live TG 1.2 endpoint smoke was not captured in this validation run. |
| External QA readiness | Plan/Test handoff | pass | TG 1.2 external QA readiness is N/A. |

## 5. Findings

| Severity | Rule ID | Location | Finding | Required fix |
|---|---|---|---|---|
| warn | CODE-3b | Repo test commands | Backend/admin checks passed, but no coverage report was generated, so the >=90% line/branch target on new code is not evidenced locally. | Add coverage commands or capture CI coverage for the TG 1.2 delta before final implement approval. |
| warn | CODE-10 | `docker-compose.yml`, implementation evidence | Compose local profile renders, but this validate pass did not capture full Docker startup and live TG 1.2 happy/error endpoint smoke. | Before final implement approval, run Docker-backed smoke for admin match create, seat generate, price set, QR default, and at least one auth/error case. |
| info | Scope boundary | TG 1.3 checkout/user browse refs | TC-003..TC-006 include API-003/API-005 checkout-facing assertions, but TG 1.2 plan excludes user checkout writes and TG 1.3 owns API-003..API-006. | Keep TG 1.2 focused on source-of-truth inventory/pricing/QR; complete user-facing proof in TG 1.3. |

## 6. Conclusion

- blocker: 0
- warn: 2
- info: 1
- latest conclusion: `clean`

Spec validation clears for TG 1.2. The previous blockers are resolved: default QR selection is exposed through an admin route and UI control, idempotency replay is covered, SCREEN-006/SCREEN-007 state coverage is present, and the admin UI-state test delta now runs. Remaining warnings are coverage artifact absence and lack of full Docker-backed live endpoint smoke in this pass.
