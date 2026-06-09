---
status: ACTIVE
phase: implement
mode: spec
sprint: 1
task_group: TG 1.3
cycle: tg-1-3
updated: 2026-06-08T16:35:30+07:00
conclusion: clean
---

# Validate Implementation Spec: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion

## 1. Target

| Field | Value |
|---|---|
| Command | `validate implementation --mode spec` |
| Scope | TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion |
| HEAD | `8225310` |
| Diff base | Current working tree |
| Worktree note | Dirty worktree; validation targets current working tree including untracked implementation files. |
| Plan target | `docs/sprint-v1/planning/implementation-plan-v1.md` TG 1.3 |
| Contract refs | FR-002, FR-003, FR-004, FR-005, BR-001..BR-004, NFR-001, NFR-002, US-002..US-005, AC-003..AC-010, API-003..API-006, ENT-002..ENT-005, ENT-009, SEQ-002, SEQ-003, PR-003, PR-005, SCREEN-002..SCREEN-005, DS-COMP-001, DS-COMP-002, TC-007..TC-012, TC-023 |
| Code surfaces inspected | `backend/src/main/java/com/ticketmafia/match_inventory/**`, `backend/src/main/java/com/ticketmafia/order_payment/**`, `backend/src/main/java/com/ticketmafia/shared/**`, `backend/src/test/java/com/ticketmafia/order_payment/**`, `website/src/features/matches/**`, `website/src/features/auth/components/LoginOtp.tsx`, `website/src/features/auth/services/authSession.ts`, `website/src/app/matches/page.tsx`, `apps/lib/features/matches/**`, `apps/test/**`, migrations, `docs/sprint-v1/implementation/tg-1-3-technique-evidence.md` |
| Target fingerprint | `MatchBrowseController.java` 6b84d8f9; `MatchBrowseService.java` a11e8781; `PaginatedApiResponse.java` 3f80177f; `CheckoutService.java` fbc14da8; `PaymentCompletionService.java` 991d0cf7; `OrderIdempotencyService.java` aeccadea; `OrderPaymentApiIntegrationTest.java` 9c099a3b; `OrderPaymentConcurrencyPostgresIntegrationTest.java` 6f7ee95c; `MatchCheckoutFlow.tsx` 782820f6; `useMatchCheckoutFlow.ts` 0cdebd3b; `MatchCheckoutFlowView.tsx` e3783547; `MatchCheckoutFlow.screenshot.spec.ts` 4f83530e; `MatchCheckoutFlow.screenshot-harness.tsx` ec155087; `authSession.ts` d68a95b9; `LoginOtp.tsx` 03dfde56; `tg-1-3-technique-evidence.md` 74693e34 / updated 2026-06-08T16:27:30+07:00 |

## 2. Structural Coverage (`DOC-3`)

| Artifact / area | Expected contract | Required sections / fields checked | Missing | N/A with reason |
|---|---|---|---|---|
| Product package | FR-002..FR-005, US-002..US-005, AC-003..AC-010 | Sellable match browse, concrete seat selection, max 5 seats, checkout hold, QR payment, payment-completed transition, expiry release | none for backend/web core scope | none |
| Architecture API | API-003..API-006 | Paths, auth, request parameters, response schema, error matrix, idempotency headers | none | none |
| ERD / migration | ENT-002..ENT-005, ENT-009 | Matches/seats/orders/order_items/idempotency tables, hold status columns, PostgreSQL active-order-item uniqueness | none | H2 remains a fast integration-test profile; PostgreSQL/Testcontainers now proves NFR-002. |
| Sequence | SEQ-002, SEQ-003 | Seat locks, transaction boundaries, price snapshot, idempotency records, hold expiry, payment completion, request-hash replay guard | none | none |
| Design | SCREEN-002..SCREEN-005, DS-COMP-001, DS-COMP-002 | State IDs, checkout flow, seat chips, countdown/QR/pending states, Empty/Loading/Populated/Error screenshots | none for web | Mobile screenshots remain under runtime evidence, not web design-state evidence. |
| Plan | TG 1.3 task fields | Modules, entrypoints, inherited obligations, allowed diff, affected surfaces, repo test delta, validation commands | none | External QA readiness is N/A for TG 1.3. User accepted excluding app/mobile runtime blockers on 2026-06-08. |
| Test package | TC-007..TC-012, TC-023 | Backend integration tests, PostgreSQL concurrent hold proof, web unit/screenshot smoke, mobile widget test source, technique evidence | none | Mobile runtime execution excluded by user instruction on 2026-06-08 because Flutter/Dart tooling is unavailable in this environment. |
| Runtime | Spec-mode runtime verification | Backend tests, web lint/tests/screenshots, Docker Compose API smoke, Flutter tooling check, auth token storage scan | none | Mobile launch on iOS and Android excluded by user instruction on 2026-06-08. |

## 3. Runtime / Static Evidence

| Check | Result | Evidence |
|---|---|---|
| Backend full test suite | pass | `mvn -q test` in `backend` completed with exit 0 on 2026-06-08 16:31 +07. Includes H2 MockMvc/service tests and PostgreSQL/Testcontainers concurrency test. A scheduled-job log appeared during Testcontainers PostgreSQL teardown after the concurrency test, but Maven returned exit 0 and no test failed. |
| Website static/unit/screenshot checks | pass | `npm run lint`, `npm test`, and `npm run screenshots:matches` completed with exit 0 on 2026-06-08 16:31 +07. Vitest: 2 files, 6 tests passed; Playwright: 16 screenshots passed. |
| Docker Compose runtime smoke | pass | `docker compose --profile local up -d postgres backend` reached `{"status":"UP"}` on 2026-06-08 16:35 +07. Smoke observed: API-003 first page had 1 row and `meta.nextCursor`; second page had 1 row and `nextCursor: null`; checkout status `HELD`; default QR `asset://payment/default`; same-hash replay returned same order; mismatched request hash returned HTTP 409 `CHECKOUT_INVALID_REQUEST`; duplicate seat returned HTTP 409 `SEAT_UNAVAILABLE`; payment-completed returned `PENDING_ADMIN_CONFIRM`. Stack was torn down with `docker compose --profile local down`. |
| Browser design-state evidence | pass | 16 screenshots exist under `docs/sprint-v1/implementation/screenshots/tg-1-3/`: Empty, Loading, Populated, and Error states for SCREEN-002, SCREEN-003, SCREEN-004, and SCREEN-005. |
| Frontend auth/session storage scan | pass | `rg` over `website/src` found no `localStorage`, `sessionStorage`, or `ticketMafiaAccessToken` after the quality-blocker fix. `screenshotState` appears only in `MatchCheckoutFlow.screenshot-harness.tsx`, outside the production component. |
| Flutter/mobile runtime | accepted exclusion | `command -v flutter`, `command -v dart`, and common local install path checks found no Flutter/Dart SDK. User accepted excluding all app/mobile blockers on 2026-06-08. |
| Technique evidence | pass | `docs/sprint-v1/implementation/tg-1-3-technique-evidence.md` maps backend, PostgreSQL concurrency, web component, frontend session regression, and screenshot tests to AC/API/NFR/Design refs. Mobile widget test source exists but runtime execution is excluded by user instruction. |

## 4. Rule Coverage (`VAL-1`)

| Rule ID / surface | Scope checked | Result | Notes |
|---|---|---|---|
| VAL-1 | Validate file evidence contract | pass | This report records target fingerprint, structural coverage, runtime/static evidence, rule coverage, findings, and conclusion. |
| DOC-3 | Expected implementation validation areas | pass | Product, API, ERD, sequence, design, plan, test, and runtime areas are listed with missing/N-A evidence. |
| LINK-1 / LINK-2 | Cross-artifact traceability | pass | TG 1.3 refs were traced from plan to product, architecture, design, test package, code, and implementation evidence. |
| ORB-1 | Sprint context | pass | Sprint v1 and TG 1.3 context recorded. |
| Product / US / AC | FR-002..FR-005, US-002..US-005, AC-003..AC-010 | pass | Core browse, seat map, checkout, payment-completed, ownership, max-seat, price snapshot, expiry, idempotency replay/mismatch, and web state behavior are implemented/tested; app/mobile runtime is excluded by user instruction. |
| API contract | API-003..API-006 | pass | API-003 now includes `cursor` handling and always-present `meta.nextCursor`; API-005/API-006 schemas and errors are covered. |
| ERD / NFR | ENT-002..ENT-005, ENT-009, NFR-002 | pass | PostgreSQL migration includes active hold uniqueness and Testcontainers proves exactly one active hold/order item under concurrent checkout. |
| Sequence | SEQ-002, SEQ-003 | pass | Checkout/payment state transitions are implemented; duplicate idempotency now replays only for the same request hash and conflicts on mismatch. |
| Design contract | SCREEN-002..SCREEN-005, DS-COMP-001, DS-COMP-002 | pass | State IDs and Playwright screenshots cover Empty, Loading, Populated, and Error states for all TG 1.3 web screens; app/mobile runtime is excluded by user instruction. |
| Frontend session behavior | NFR-003 / AC-002 inherited auth guard | pass | Web login now stores the access token in in-memory `authSession`; checkout uses `authSession.getAccessToken` by default and still blocks checkout when no token is available. |
| CODE-1 | Traceability markers | pass static | Business/API code surfaces inspected carry TG 1.3 markers or are directly supporting marked entrypoints. |
| CODE-3 / CODE-3a | Repo test delta and technique evidence | pass | Backend, PostgreSQL concurrency, and web repo deltas are present and mapped in technique evidence; mobile runtime is excluded by user instruction. |
| CODE-3b | Coverage target | warn | Local commands did not generate line/branch coverage artifacts for new code. |
| CODE-3c | Property/example selection | pass | Selection limit, price snapshot, idempotency request hash, state transition, expiry, and concurrent hold invariants have explicit example/integration coverage. |
| CODE-10 | Local Docker Compose runtime self-test | pass | Local compose path exists and changed backend endpoints were exercised with happy and error paths. |
| External QA readiness | Plan/Test handoff | pass | TG 1.3 external QA readiness is N/A. |

## 5. Findings

| Severity | Rule ID | Location | Finding | Required fix |
|---|---|---|---|---|
| warn | CODE-3b | Repo test commands | Backend/web checks passed, but no coverage report was generated, so the >=90% line/branch target on new code is not evidenced locally. | Add coverage commands or capture CI coverage for the TG 1.3 delta before final implement approval. |
| info | Test runtime noise | `mvn -q test` / Testcontainers teardown | Backend suite returned exit 0, but a scheduled hold-release task logged a PostgreSQL connection error while the Testcontainers database was shutting down after the concurrency test. This did not fail the suite or contradict the TG 1.3 contract evidence. | Consider disabling scheduled jobs in the test profile or explicitly shutting down scheduling before Testcontainers teardown to reduce noise. |
| info | User exclusion | App/mobile runtime | User explicitly instructed to ignore all app-related blockers on 2026-06-08. Flutter/Dart are unavailable in this environment, and mobile runtime evidence is excluded from this TG 1.3 spec verdict. | Re-open validation if app/mobile runtime evidence becomes required again. |
| info | Fixed | API contract / API-003 | Previous blocker resolved: `GET /api/v1/matches` now supports `cursor` and returns always-present `meta.nextCursor`; tests and Docker smoke confirm the field. | none |
| info | Fixed | Sequence / PR-005 | Previous blocker resolved: order idempotency now stores and compares request hashes before replay; mismatch returns HTTP 409. | none |
| info | Fixed | NFR-002 / CODE-3 | Previous blocker resolved: PostgreSQL/Testcontainers concurrent checkout test proves exactly one active hold/order item for one seat. | none |
| info | Fixed | Design runtime / SCREEN-002..SCREEN-005 | Previous blocker resolved: Playwright now captures 16 web screenshots covering all declared states. | none |

## 6. Conclusion

- blocker: 0
- warn: 1
- info: 6
- latest conclusion: `clean`

Spec validation clears for TG 1.3 after user-accepted exclusion of app/mobile runtime blockers. The quality-blocker refactor did not break TG 1.3 spec behavior: frontend tests and screenshots still pass, checkout still blocks unauthenticated users through the token provider path, and live Docker smoke verifies API-003/API-005/API-006 behavior. All auto-runnable TG 1.3 blockers found in the prior spec validation remain fixed and verified: API-003 pagination metadata, idempotency request-hash behavior, PostgreSQL concurrent hold proof, and complete web design-state screenshots.
