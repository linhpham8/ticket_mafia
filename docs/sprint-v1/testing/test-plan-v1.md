---
status: APPROVED
version: v1
sprint: 1
phase: test
created: 2026-06-08
updated: 2026-06-08 12:51
approved_by: user
---

# Test Plan — ticket_mafia (Sprint v1)

## 1. Test Strategy Overview

| Attribute | Value |
|-----------|-------|
| Testing approach | Risk-based, requirement-traceable |
| Planning target | Define execution-ready QA intent for the v1 demo before implementation closes |
| Execution ownership | Dev executes repo tests during Implement; QA/PO review manual demo evidence locally |
| Release criteria | TC-001 through TC-024 pass or have explicit accepted deferral; no Critical/High defect open |

> **Phase Test ownership**: phase này sở hữu `qa test intent` only — `test-plan` + `test-cases`. KHÔNG sở hữu repo test delta, generated runtime data packs, hoặc external QC automation code.

## 2. Scope

### In Scope

| Area | Test Types | Priority |
|------|-----------|----------|
| Mock OTP auth and protected purchase/exchange | Functional, integration, security | P0 |
| Admin match, seat, price, QR config | Functional, integration, UI manual | P0 |
| User match list, seat selection, checkout hold, manual payment completion | Functional, SIT, concurrency, UI manual, performance smoke | P0 |
| Admin confirm/reject and audit | Functional, SIT, state transition, UI manual | P0 |
| Purchase history, QR/e-ticket, one-time scan | Functional, security, SIT, UI manual | P0 |
| Seat exchange | Functional, SIT, state transition, UI manual | P0 |
| Local Docker Compose demo | Smoke, operational self-test | P1 |

### Out of Scope

| Area | Reason |
|------|--------|
| Payment gateway reconciliation | Product v1 uses manual transfer QR only. |
| SMS/email OTP provider verification | Architecture uses mock/internal OTP for demo. |
| Queue/waiting room load strategy | Product explicitly rejected for demo. |
| Scanner app UI and offline scan | Product scopes scan as API behavior only. |
| CI/CD, cloud, Sentry/Rollbar | Architecture ADR-003 marks them out of scope. |
| WCAG AA certification | User rejected WCAG AA as a v1 requirement; still keep basic visual/manual sanity checks. |

## 2a. Design State Coverage

| Screen / Component | State | Test Case ID | Mode (manual / auto) |
|--------------------|-------|--------------|----------------------|
| SCREEN-001 Login OTP | Empty/Input | TC-001 | manual + automated |
| SCREEN-001 Login OTP | Error/blocked protected action | TC-002 | manual + automated |
| SCREEN-002 Match List | Populated | TC-007 | manual + automated |
| SCREEN-002 Match List | Non-purchasable/empty filtered result | TC-008 | manual + automated |
| SCREEN-003 Match Seat Selection | Populated selectable seats | TC-009 | manual + automated |
| SCREEN-003 Match Seat Selection | Limit/error state | TC-010 | manual + automated |
| SCREEN-004 Checkout Transfer QR | Populated QR/amount/countdown | TC-011 | manual + automated |
| SCREEN-004 Checkout Transfer QR | Expired/error | TC-012 | manual + automated |
| SCREEN-005 Pending Confirmation | Waiting/countdown | TC-011, TC-013 | manual + automated |
| SCREEN-005 Pending Confirmation | Expired/rejected | TC-012, TC-014 | manual + automated |
| SCREEN-006 Admin Match Management | List/form/status populated | TC-003 | manual + automated |
| SCREEN-006 Admin Match Management | Cancelled/closed blocked purchase | TC-004 | manual + automated |
| SCREEN-007 Admin Seat Price QR Config | Price/QR configured | TC-005 | manual + automated |
| SCREEN-007 Admin Seat Price QR Config | Snapshot edge | TC-006 | automated |
| SCREEN-008 Admin Payment Confirmation | Pending list/filter/action | TC-013 | manual + automated |
| SCREEN-008 Admin Payment Confirmation | Reject/expired state | TC-014 | manual + automated |
| SCREEN-009 Purchase History | Populated | TC-015 | manual + automated |
| SCREEN-009 Purchase History | Empty/no cross-user data | TC-016 | manual + automated |
| SCREEN-010 Ticket Detail | Issued QR detail | TC-017 | manual + automated |
| SCREEN-010 Ticket Detail | Invalid/non-entry state | TC-018 | manual + automated |
| SCREEN-011 Scan Status Result | First scan success | TC-019 | automated |
| SCREEN-011 Scan Status Result | Repeated scan rejected | TC-020 | automated |
| SCREEN-012 Seat Exchange | Eligible exchange | TC-021, TC-022 | manual + automated |
| SCREEN-012 Seat Exchange | Cheaper/unavailable blocked | TC-024 | manual + automated |
| DS-COMP-001 Seat Chip | Available/held/selected/unavailable colors | TC-009, TC-010, TC-024 | manual |
| DS-COMP-002 Countdown Banner | Active/expired countdown | TC-011, TC-012, TC-014 | manual |
| DS-COMP-003 Ticket QR Card | Issued/invalid state | TC-017, TC-018 | manual |
| DS-COMP-004 Admin Data Table | Filtered pending/admin lists | TC-003, TC-013 | manual |
| DS-COMP-005 Status Chip | All core statuses | TC-004, TC-014, TC-018, TC-020 | manual |

## 2b. Coverage Traceability Index

| FR / NFR | US | Design / API Refs | Project / Boundary Refs | TC IDs | Manual / Auto Mix | Coverage Status / Gap |
|---|---|---|---|---|---|---|
| FR-001, NFR-003 | US-001 | SCREEN-001; API-001, API-002 | PR-001, PR-003 | TC-001, TC-002 | automated + manual | covered |
| FR-002 | US-002 | SCREEN-002; API-003 | PR-004 | TC-007, TC-008 | automated + manual | covered |
| FR-003, BR-003 | US-003 | SCREEN-003, DS-COMP-001; API-004 | PR-004 | TC-009, TC-010 | automated + manual | covered |
| FR-004, NFR-002 | US-004 | SCREEN-004, SCREEN-005; API-005 | PR-005 | TC-011, TC-012, TC-023 | automated + manual | covered |
| FR-005 | US-005 | SCREEN-004, SCREEN-005; API-006 | PR-005 | TC-011, TC-012 | automated + manual | covered |
| FR-006 | US-006 | SCREEN-006; API-010 | PR-002, PR-003 | TC-003, TC-004 | automated + manual | covered |
| FR-007, BR-004 | US-007 | SCREEN-007; API-011, API-012 | PR-002, PR-005 | TC-005, TC-006 | automated + manual | covered |
| FR-008, NFR-004 | US-008 | SCREEN-008; API-007 | PR-005 | TC-013, TC-014, TC-022 | automated + manual | covered |
| FR-009 | US-009, US-010 | SCREEN-009, SCREEN-010; API-008, API-009 | PR-004 | TC-015, TC-016, TC-017, TC-018 | automated + manual | covered |
| FR-010, NFR-003 | US-011 | SCREEN-011; API-013 | PR-005 | TC-019, TC-020 | automated | covered |
| FR-011, FR-012, NFR-002 | US-012 | SCREEN-012; API-014, API-015 | PR-005 | TC-021, TC-022, TC-024 | automated + manual | covered |
| NFR-001 | all API flows | API-003..API-015 | PR-003 | TC-023 | automated | covered as demo smoke/load intent |
| NFR-005 | full runtime | Docker Compose runtime | PR-001 | TC-024 | manual + automated smoke | covered |

## 2c. Branch Discovery Summary

| Feature / Flow | Branches Discovered | Unclear / Contradictory Inputs | Questions / Proposed Assumptions | Impacted TC Areas |
|---|---|---|---|---|
| Checkout hold | happy hold, 5-seat boundary, double booking, hold expiry, payment-completed after expiry, price snapshot | none | Use 10-minute hold, scheduler every minute, external `Idempotency-Key` | TC-009..TC-012, TC-023 |
| Admin confirmation | confirm within 10 minutes, reject, expiry, duplicate decision retry, audit | none | Admin validates transfer outside system | TC-013, TC-014, TC-022 |
| Ticket scan | first scan, repeated scan, invalid/non-issued token | none | Scanner UI out of scope; API behavior only | TC-019, TC-020 |
| Seat exchange | higher price, equal price, cheaper blocked, unavailable blocked, admin confirms, old ticket valid until confirm | none | Exchange reuses checkout/admin confirmation behavior | TC-021, TC-022, TC-024 |

## 3. Test Types & Tools

| Test Type | Purpose | Tool (from Architecture/context) | Run Frequency | Owner |
|-----------|---------|-------------------------|--------------|-------|
| Unit | Dev-owned repo test delta context | JUnit 5 + Mockito; Flutter test; Vitest | During implementation | Dev |
| Component | Component-level behavior intent | Vitest/Testing Library; Flutter widget test | During implementation | Dev |
| Integration | Component interaction intent | Spring Boot integration + Testcontainers | During implementation | Dev |
| E2E | Full user-flow validation intent | Playwright for web/admin; Flutter integration as available | Post-implementation | QA + Dev |
| API Contract | Request/response schema intent | Spring/JSON schema assertions or generated contract tests from approved API specs | During implementation | Dev |
| Performance | Load & stress validation intent | TBD by Implement; must report p50/p95/p99 and error rate | Pre-demo smoke | Dev + QA |
| Security | Vulnerability and abuse-case intent | Safe local checks, unit/integration assertions, dependency/config review | During implementation / review | Security + Dev |
| Accessibility | Basic UI sanity only | Manual keyboard/visual scan; no WCAG AA gate | QA review | Dev + QA |
| Manual / Exploratory | UX, QR display, admin table/filter, mobile responsive/native behavior | Manual | QA/PO review stage | QA + PO |

## 4. Test Environment

| Environment | Purpose | Data | Access |
|------------|---------|------|--------|
| Local Docker Compose | Primary demo and integration/e2e validation | Synthetic seed matches, users, seats, QR configs | Dev |
| Future CI | Intent only; no CI/CD required in v1 | Ephemeral PostgreSQL/Testcontainers fixtures | Dev |
| Staging | N/A for v1 demo | N/A | N/A |

### Test Data Strategy

- **Golden dataset**: One `OPEN_FOR_SALE` match with sections A/B/C/D, two floors each, A VIP, seats `A-T1-001` style, prices per section/floor/VIP, and one default QR config.
- **Mutation strategy**: Change match statuses, seat statuses, selected seat count, hold timestamps, price versions, order statuses, ticket statuses, and exchange target price class.
- **PII / sensitive data rule**: synthetic users only, e.g. `fan1@example.test`, `fan2@example.test`, `admin@example.test`; no production data.
- **Isolation model**: local DB reset/seed before e2e and Testcontainers per integration suite.
- **Teardown/reset expectation**: reset DB or fixture cleanup for orders, order_items, seats, tickets, idempotency_records, and audit_logs.
- **Repo unit-test data requirement**: builders/factories for user, match, seat, price_version, order, order_item, ticket, idempotency_record.
- **Integration-test data requirement**: PostgreSQL Testcontainers with migrations and deterministic clock for hold/confirmation expiry.
- **E2E data requirement**: seeded admin/user accounts, one default QR, deterministic match inventory.
- **Performance data requirement**: minimum 1 open match, 9+ section/floor/VIP price groups, and enough seats to support 50 concurrent browse/seat requests; exact volume can be created by seed script during Implement.

## 4a. External QA Handoff Summary

| Handoff Need | Detail | Source / Owner | Status |
|---|---|---|---|
| Target environment | N/A — no external QA handoff; local Docker Compose only | PO default | ready |
| Stable UI selectors | Dev should still add `data-testid` for P0 web/admin controls to support future automation | Dev | planned |
| API contracts | API-001 through API-016 used by repo/e2e tests | Architecture | ready |
| Seed/reset hooks | Local seed/reset expected during Implement | Dev | planned |
| Test accounts | Roles only: fan buyer, admin, scan consumer; secrets outside PRISM if ever needed | Dev | planned |
| Feature flags/config | N/A for v1 | Dev | ready |
| Evidence expectation | Screenshots for designed UI states, API responses for scan/exchange, test output summaries | Dev + QA | planned |

## 5. Entry Criteria

Planning is complete when:

- [x] Every in-scope feature has defined test intent.
- [x] Planned automated vs manual boundaries are clear.
- [x] Required test data is identified.
- [x] Future execution environments are identified.
- [x] Release-critical risks have explicit validation coverage.
- [x] Branch Discovery Summary exists for checkout, confirmation, scan, and exchange.
- [x] External QA Handoff Summary records N/A for external QA and required local evidence.

## 6. Exit Criteria

Execution success is measured later when:

- [ ] All P0 TC cases TC-001 through TC-024 are implemented/executed and pass.
- [ ] Unit test line coverage >= 90% and branch coverage >= 90% on new code.
- [ ] Integration tests cover every in-scope public API with at least one happy path and one error/guard path where applicable.
- [ ] 0 Critical defect open.
- [ ] 0 High defect open unless PO + Tech Lead explicitly accept workaround.
- [ ] NFR-001 performance smoke records p50/p95/p99 under 50 concurrent demo users and p95 <= 800ms excluding cold start.
- [ ] Security tests pass for auth/session, role guard, ownership/IDOR, QR token PII, CSRF/basic header posture where applicable, and OTP/checkout abuse guards.
- [ ] Basic UI sanity checks show no blocking layout overlap or broken P0 visual state.
- [ ] QA/PO sign-off on exploratory execution for P0 user and admin flows.
- [ ] Regression strategy in §7 is executed for the final demo build.

## 7. Regression Strategy

| Trigger | Regression Scope | Duration Estimate | Owner |
|---|---|---|---|
| Feature branch merge into delivery branch | Targeted TC set for affected task group + direct downstream flow | 30–60 minutes | Dev |
| Backend schema/state-machine change | Auth, checkout, admin confirmation, ticket scan, exchange integration tests | 1–2 hours | Dev |
| UI screen change | Screenshot/manual observation for affected SCREEN IDs plus one happy e2e path | 30–60 minutes | Dev + QA |
| End of sprint / demo candidate | Full TC-001 through TC-024 plus local Docker Compose smoke | 4–6 hours | QA + Dev |
| Hotfix before demo | P0 smoke: auth → admin seed → checkout → confirm → ticket QR → scan → exchange | ~30 minutes | Dev + QA |

**Automated regression gate** *(future intent, no CI/CD required in v1)*:
- Local pre-merge: backend unit/integration tests + web component tests for touched area.
- Local demo candidate: Playwright smoke for web/admin and Docker Compose health checks.

## 8. Risk-Based Test Priority

| Risk Area | Likelihood | Impact | Test Priority | Test Depth |
|-----------|-----------|--------|--------------|-----------|
| Seat hold consistency and double booking | Medium | Critical | P0 | Deep: transaction, concurrent hold, expiry, idempotency |
| Manual payment/admin confirmation state transitions | Medium | Critical | P0 | Deep: confirm, reject, expiry, duplicate action, audit |
| QR/e-ticket scan once | Medium | High | P0 | Deep: signed token, no PII, atomic scan, repeated scan rejection |
| Price snapshot after admin price update | Medium | High | P0 | Deep: before/after price version scenarios |
| Seat exchange eligibility and old-ticket retirement | Medium | High | P0 | Deep: equal/higher allowed, cheaper/unavailable blocked, old ticket valid until confirm |
| Auth/session/ownership | Medium | High | P0 | Deep: protected actions, IDOR, timeout |
| UI layout across web/mobile/admin | Medium | Medium | P1 | Manual + e2e on P0 screens |
| Local Docker runtime | Low | High | P1 | Health and full smoke |

## 9. Defect Management

| Severity | Definition | Response Time | Resolution SLA |
|----------|-----------|--------------|----------------|
| Critical | Core purchase/admin/ticket/scan/exchange blocked, data loss, or serious security issue | Immediate | Same day |
| High | Main feature broken with no acceptable workaround | < 4 hours | Current delivery window |
| Medium | Feature impaired but workaround exists | < 1 day | Within 2 delivery windows |
| Low | Cosmetic/minor issue with limited functional impact | Best effort | Backlog |

## 10. Test Reporting

| Report | Frequency | Audience | Contents |
|--------|----------|---------|----------|
| Planning review | During Plan/Test approval | PO, Tech Lead, QA | Coverage map, risks, execution intent |
| Implementation checkpoint | Per task group | Dev team | Implemented repo tests, mapped TC evidence, open defects |
| Demo candidate report | Before approval of implementation | PO, Tech Lead, QA | TC status, screenshots, API evidence, known limitations |
| Generated TSV companions | During `start test` / `validate test` | QA / future QC import | Functional/SIT import views generated from `test-cases-v1.md` |

---

## Self-Review Checklist

- [x] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `TEST-1`, `TEST-2`, `TEST-3`, `TEST-3b`, `TEST-4`, `TEST-5`, `TEST-6`, `TEST-7`, `TEST-8`
- [x] All Must Have FRs have test coverage plan.
- [x] Coverage Traceability Index maps FR/NFR/US to design/API/project refs and concrete TC IDs.
- [x] Test types match Architecture-approved frameworks and do not choose new frameworks.
- [x] Exit criteria include coverage, defect, performance, security, and manual evidence targets.
- [x] Regression strategy has trigger, scope, estimate, and owner.
- [x] Risk matrix uses actual ticketing risks.
- [x] Test data strategy covers synthetic data, isolation, and teardown/reset.
- [x] Branch Discovery Summary exists for complex flows.
- [x] External QA Handoff Summary records local-only default.
- [x] Phase Test does not create runnable automation code or runtime data packs.
