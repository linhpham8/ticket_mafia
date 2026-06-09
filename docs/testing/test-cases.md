---
status: APPROVED
approved_by: user
version: v1
sprint: 1
phase: testing
sprint_id: sprint-v1
created: 2026-06-08
updated: 2026-06-08 22:21
---

# Test Cases — 

<!-- This file is the Living Truth root for the Test phase. It accumulates test cases
     across sprints. AI never writes this file directly — `apply_proposal.py` merges
     anchored TC items from each sprint's `testing/proposals/test-cases-v{X}.md` at sprint seal.

     Phase 9 changes vs 1.x:
     - ID format `TC-{AREA}-{NNN}` → flat `TC-{NNN}`. Feature area moves to `**Area**:` body field.
     - Stable ID anchor convention: every test case is preceded by `&lt;!-- ID: TC-NNN --&gt;` + optional `&lt;!-- VERIFIES: ID-NNN --&gt;` trace tag. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each TC block MUST start with:
         &lt;!-- ID: TC-NNN --&gt;
         &lt;!-- VERIFIES: ID-NNN --&gt;   (optional trace tag — preserves but does not route)
         ### TC-NNN: {Title} [planned-automated|planned-manual] P0|P1|P2
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type TC`
     Strict format: `TC-\d{3,}` (zero-padded ≥3 digits).
     (Guided seal only) The anchor also lets `apply_proposal.py` merge this block at sprint seal — Freedom has no seal but still issues the ID above and keeps the anchor. -->

## 1. Conventions

- **ID format**: `TC-NNN` flat (vd `TC-001`, `TC-042`). Feature area NOT in ID.
- **Title convention**: TC heading uses a trace prefix + technique prefix before the descriptive title.
  - Functional TCs: `[US-NNN][AC-NNN][Technique]` — example `### TC-007: [US-010][AC-001][BVA] Cache TTL 299s still serves (cacheHit=true) \`[planned-automated]\` \`P0\``.
  - Imported project/story aliases are accepted during normalization when the upstream product source owns that label, e.g. `[US-10.1][AC1][BVA]`; prefer canonical PRISM stable IDs for newly authored PRISM artifacts.
  - Non-functional TCs (Performance / Security / A11Y) without a single AC anchor: `[NFR-NNN][Technique]` — example `### TC-042: [NFR-V3-02][Security] SQL Injection prevention on /search`.
  - SIT TCs: `[US-NNN][AC-NNN][SIT]` (technique = SIT) when traceable to a US/AC; otherwise `[FLOW-NNN][SIT]`.
  - `Technique` ∈ `{Positive, Negative, BVA, EP, DT, ST, DD, Security, Regression, Impact, BasicFlow, CornerCase, Exploratory, SIT, Performance, Accessibility}`.
  - Multi-technique TCs combine with `+`, e.g. `[BVA+Negative]` or `[ST+Security]`.
  - Functional trace + Technique title prefixes must match Y cells in §3.5 Per-AC Technique Decision Matrix.
  - The exporter preserves the entire prefix in the `Summary` TSV column.
- **Feature area** *(field in body, not ID)*: write `**Area**: AUTH | ORDER | PAYMENT | PROFILE | CART | CHECKOUT | ADMIN | PERF | SEC | A11Y | ...` per test case. Use feature-based names that map to business risk; avoid component-based labels (API/UI).
- **Traceability**: every TC has `**Traceability**: US-NNN, FR-NNN, NFR-NNN` — no trace = no traceability. The optional `&lt;!-- VERIFIES: ID-NNN --&gt;` anchor tag carries the primary verified item for cross-doc tooling.
- **Coverage Traceability Index alignment**: TC IDs and FR/NFR refs here must match `test-plan-v{X}.md §2b Coverage Traceability Index`.
- **Format**: Given / When / Then (BDD-style).
- **Type tags** *(in heading)*: `[planned-automated]` = automation candidate; `[planned-manual]` = QA manual.
- **Test Level**: `component` | `integration` | `e2e`. Do NOT use `unit` (those are repo test delta owned by Implement).
- **Test Type**: `Functional` | `Regression` | `Non-Functional` | `Exploratory` | `Security` | `Performance` | `Accessibility` | or project-specific.
- **Export target**: `functional` | `sit` | `none`. Generated TSV companions derive from this field + section context.
- **Smoke**: `Y` only for independent, short, release-critical cases.
- **Automation intent**: `Auto=Y` = candidate for future repo test or external QC automation; does NOT generate runnable automation in Phase Test.
- **Generated TSV rule**: `generated/test-cases-functional-v{X}.tsv`, `generated/test-cases-sit-v{X}.tsv`, `generated/test-cases-export-manifest-v{X}.json` are generated from this Markdown. Do not edit generated TSV by hand.
- **Mandatory metadata for every TC**: Area, Traceability, Manual/Auto boundary, Test Level, Test Type, Export target, Smoke, Environment, Data needs, Teardown/reset (when state-changing), Depends on, Automation intent, Owner of execution context. Add Design states, API/NFR refs, System A/B expected, Screen under test, External QA handoff needs when applicable.
- **Metadata format**: keep metadata as `**Field**: value`. The TSV exporter reads that exact shape; grouping labels below are only for readability.
- **Pre-conditions phải cụ thể**: KHÔNG viết "User exists" — ghi user ID, role, status, và cách lấy auth token nếu cần test authenticated endpoint.

## 2. Priority Levels

| Priority | Meaning | Execution |
|----------|---------|-----------|
| P0 | Critical path — must be implemented and validated before release | Highest priority in planning |
| P1 | Important — should be implemented in the planned delivery window | Planned during implementation |
| P2 | Nice to have — can defer if time-constrained | Backlog / later cycle |

<!-- PRISM:INDEX:START (auto-generated by seal_sprint.py — do not edit by hand) -->

## Index

| ID | Title |
|---|---|
| TC-001 | [US-001][AC-001][EP+DT+ST] Mock OTP login succeeds for email or phone `[planned-automated]` `P0` |
| TC-002 | [US-001][AC-002][EP+DT+ST+Security] Protected checkout and exchange require login `[planned-automated]` `P0` |
| TC-003 | [US-006][AC-011][EP+DT+ST] Admin opens a created match for sale `[planned-automated]` `P0` |
| TC-004 | [US-006][AC-012][EP+DT+ST] Cancelled or closed match blocks new purchase `[planned-automated]` `P0` |
| TC-005 | [US-007][AC-013][EP+DT+ST] New checkout uses latest active price after admin update `[planned-automated]` `P0` |
| TC-006 | [US-007][AC-014][EP+DT+ST] Existing checkout keeps original snapshot after price update `[planned-automated]` `P0` |
| TC-007 | [US-002][AC-003][EP+ST] User sees OPEN_FOR_SALE match and enters seat selection `[planned-automated]` `P0` |
| TC-008 | [US-002][AC-004][EP+DT+DD+ST] Non-purchasable match statuses do not start purchase `[planned-automated]` `P0` |
| TC-009 | [US-003][AC-005][BVA+EP+DT+ST+DD] Select 1 to 5 available seat codes with current prices `[planned-automated]` `P0` |
| TC-010 | [US-003][AC-006][BVA+DT+ST] Sixth selected seat is blocked `[planned-automated]` `P0` |
| TC-011 | [US-004][AC-007][BVA+EP+DT+ST+DD] Checkout holds selected seats, snapshots prices, and moves to pending payment completion `[planned-automated]` `P0` |
| TC-012 | [US-004][AC-008][BVA+DT+ST] Expired checkout hold releases seats and rejects payment completion `[planned-automated]` `P0` |
| TC-013 | [US-008][AC-015][BVA+DT+ST] Admin confirms pending order within 10 minutes and issues tickets `[planned-automated]` `P0` |
| TC-014 | [US-008][AC-016][BVA+EP+DT+ST] Admin rejection or confirmation expiry releases seats `[planned-automated]` `P0` |
| TC-015 | [US-009][AC-017][EP+DT+ST+DD] Purchase history shows only current user's records and statuses `[planned-automated]` `P0` |
| TC-016 | [US-009][AC-018][EP+DT+Security] Empty purchase history shows no other user's data `[planned-automated]` `P0` |
| TC-017 | [US-010][AC-019][EP+DT+ST+Security] Issued ticket detail shows signed QR without PII `[planned-automated]` `P0` |
| TC-018 | [US-010][AC-020][EP+DT+ST+DD] Invalid ticket statuses are not presented as valid entry tickets `[planned-automated]` `P0` |
| TC-019 | [US-011][AC-021][EP+DT+ST+Security] First valid ticket scan marks ticket USED/SCANNED `[planned-automated]` `P0` |
| TC-020 | [US-011][AC-022][EP+DT+ST+Security] Repeated scan is rejected and ticket remains scanned `[planned-automated]` `P0` |
| TC-021 | [US-012][AC-023][BVA+EP+DT+ST] Higher-priced exchange checkout holds new seat and charges difference `[planned-automated]` `P0` |
| TC-022 | [US-012][AC-023][BVA+DT+ST] Admin confirms exchange and retires old ticket `[planned-automated]` `P0` |
| TC-023 | [NFR-002][Performance+CornerCase] Concurrent checkout permits only one active hold per seat `[planned-automated]` `P0` |
| TC-024 | [US-012][AC-024][EP+DT] Cheaper or unavailable replacement seat blocks exchange and Docker smoke passes `[planned-automated]` `P1` |

<!-- PRISM:INDEX:END -->

<!-- ID: TEST-COVERAGE-001 -->
### Rule / Branch Inventory

| Rule / AC / BR / Branch ID | Source Ref | Description | Covered TC IDs | Status | Gap / N/A Reason |
|---|---|---|---|---|---|
| AC-001 | US-001 | Valid email/phone OTP logs user in | TC-001 | covered | |
| AC-002 | US-001 | Unauthenticated checkout/exchange requires login | TC-002 | covered | |
| AC-003 | US-002 | OPEN_FOR_SALE match appears and opens seat selection | TC-007 | covered | |
| AC-004 | US-002 | SOLD_OUT/CANCELLED/CLOSED not available for purchase | TC-008 | covered | |
| AC-005 | US-003 | Select up to 5 available seats and show current price | TC-009 | covered | |
| AC-006 | US-003 | Sixth selected seat is blocked | TC-010 | covered | |
| AC-007 | US-004 | Checkout creates order, holds seats 10 minutes, snapshots prices | TC-011, TC-023 | covered | |
| AC-008 | US-004 | Hold expiry expires order and releases seats | TC-012 | covered | |
| AC-009 | US-005 | Active hold can move to PENDING_ADMIN_CONFIRM | TC-011 | covered | |
| AC-010 | US-005 | Expired hold rejects payment completion | TC-012 | covered | |
| AC-011 | US-006 | Admin OPEN_FOR_SALE match is purchasable | TC-003 | covered | |
| AC-012 | US-006 | CANCELLED/CLOSED match blocks purchase | TC-004 | covered | |
| AC-013 | US-007 | New checkout after price update uses new price | TC-005 | covered | |
| AC-014 | US-007 | Existing checkout keeps original snapshot price | TC-006 | covered | |
| AC-015 | US-008 | Admin confirm within 10 minutes issues tickets | TC-013, TC-022 | covered | |
| AC-016 | US-008 | Admin reject/expiry cancels/rejects and releases seats | TC-014 | covered | |
| AC-017 | US-009 | User history shows own records/status | TC-015 | covered | |
| AC-018 | US-009 | Empty history shows empty state and no other user's data | TC-016 | covered | |
| AC-019 | US-010 | ISSUED ticket detail shows match, seat, status, QR | TC-017 | covered | |
| AC-020 | US-010 | CANCELLED/REJECTED/EXCHANGED not valid entry ticket | TC-018 | covered | |
| AC-021 | US-011 | First valid scan moves ISSUED to USED/SCANNED | TC-019 | covered | |
| AC-022 | US-011 | Repeated scan rejected and status remains scanned | TC-020 | covered | |
| AC-023 | US-012 | Higher-priced exchange confirmed issues new ticket and exchanges old | TC-021, TC-022 | covered | |
| AC-024 | US-012 | Cheaper/unavailable exchange target blocked | TC-024 | covered | |
| BR-001 | PRD | User must authenticate before purchase | TC-002 | covered | |
| BR-002 | PRD | Seat hold starts at payment step and lasts 10 minutes | TC-011, TC-012 | covered | |
| BR-003 | PRD | User can select at most 5 seats per purchase | TC-010 | covered | |
| BR-004 | PRD | Purchase price snapshotted at checkout start | TC-006, TC-011 | covered | |
| BR-005 | PRD | Admin confirmation window controls ticket issuance | TC-013, TC-014 | covered | |
| BR-006 | PRD | E-ticket QR can be scanned once | TC-019, TC-020 | covered | |
| BR-007 | PRD | Seat exchange only equal-or-higher available seats | TC-021, TC-024 | covered | |
| BR-008 | PRD | Match/seat lifecycle rules | TC-004, TC-012, TC-014, TC-018, TC-020, TC-022 | covered | |
| NFR-001 | NFR | Demo API p95 <= 800ms under 50 concurrent users | TC-023 | covered | |
| NFR-002 | NFR | Zero double-active holds | TC-023 | covered | |
| NFR-003 | NFR | Session timeout and no PII in QR | TC-002, TC-017 | covered | |
| NFR-004 | NFR | Structured logs/audit evidence | TC-014 | covered | |
| NFR-005 | NFR | Docker Compose self-test | TC-024 | covered | |

#### Per-AC Technique Decision Matrix

| AC ID | BVA Y/N + reason | EP Y/N + reason | DT Y/N + reason | ST Y/N + reason | DD Y/N + reason | TC IDs generated |
|---|---|---|---|---|---|---|
| AC-001 | N — no numeric boundary | Y — identifier has email/phone classes | Y — identifier valid and OTP valid are both required | Y — anonymous to authenticated session | N — two identifier variants only | TC-001 (EP+DT+ST) |
| AC-002 | N — no numeric boundary | Y — protected action classes are checkout and exchange | Y — not logged in plus protected action blocks | Y — unauthenticated remains blocked | N — two variants only | TC-002 (EP+DT+ST+Security) |
| AC-003 | N — no numeric boundary | Y — match status `OPEN_FOR_SALE` class | N — single allowed status condition | Y — purchasable list state | N — one positive status | TC-007 (EP+ST) |
| AC-004 | N — no numeric boundary | Y — three non-purchasable statuses | Y — status determines visibility/action | Y — sale status blocks purchase | Y — SOLD_OUT/CANCELLED/CLOSED share expected result | TC-008 (EP+DT+DD+ST) |
| AC-005 | Y — selection range 1 to 5 | Y — seat statuses include AVAILABLE vs unavailable | Y — logged-in and match open and seat available | Y — AVAILABLE to selected UI state | Y — sections/floors/VIP price groups share expected shape | TC-009 (BVA+EP+DT+ST+DD) |
| AC-006 | Y — boundary at 5 seats, sixth blocked | N — single boundary rule | Y — already selected 5 and select another blocks | Y — selection count remains 5 | N — one edge outcome | TC-010 (BVA+DT+ST) |
| AC-007 | Y — 1..5 seats and 10-minute hold | Y — selected seats by price groups | Y — available seats plus valid idempotency key create hold | Y — AVAILABLE to HELD and order created | Y — multiple selected seat counts share order creation | TC-011, TC-023 (BVA+EP+DT+ST+DD) |
| AC-008 | Y — 10-minute expiry boundary | N — single expiry rule | Y — timer ended causes expiry | Y — HELD to EXPIRED and seats AVAILABLE | N — one expiry path | TC-012 (BVA+DT+ST) |
| AC-009 | N — active hold is time-valid but TC uses ordinary valid state, not boundary | N — single transition | Y — active hold allows payment completed | Y — HELD to PENDING_ADMIN_CONFIRM | N — one transition | TC-011 (DT+ST) |
| AC-010 | Y — expired hold after 10 minutes | N — single expired class | Y — expired hold rejects completion | Y — EXPIRED remains not payable | N — one error path | TC-012 (BVA+DT+ST) |
| AC-011 | N — no numeric boundary | Y — OPEN_FOR_SALE status | Y — admin-created and open makes match purchasable | Y — match status controls user list state | N — one status | TC-003 (EP+DT+ST) |
| AC-012 | N — no numeric boundary | Y — CANCELLED and CLOSED status classes | Y — cancelled/closed blocks purchase | Y — match status moves to blocked sale state | N — two variants only | TC-004 (EP+DT+ST) |
| AC-013 | N — price value itself is not bounded | Y — old/new price version classes | Y — checkout after update reads active price | Y — active price version changes | N — one updated price path | TC-005 (EP+DT+ST) |
| AC-014 | N — price value itself is not bounded | Y — existing order vs future checkout classes | Y — checkout before update keeps snapshot | Y — order item snapshot remains unchanged | N — two paths only | TC-006 (EP+DT+ST) |
| AC-015 | Y — 10-minute admin confirmation window | N — single confirm decision | Y — pending order plus admin confirm issues ticket | Y — PENDING_ADMIN_CONFIRM to ISSUED | N — one decision | TC-013, TC-022 (BVA+DT+ST) |
| AC-016 | Y — 10-minute confirmation expiry | Y — reject and expiry classes | Y — reject or expiry releases seats | Y — PENDING_ADMIN_CONFIRM to REJECTED/CANCELLED | N — two variants only | TC-014 (BVA+EP+DT+ST) |
| AC-017 | N — no numeric boundary | Y — order/ticket status classes | Y — owner user sees own records only | Y — statuses rendered from current order/ticket state | Y — pending/issued/rejected/exchanged/scanned share history shape | TC-015 (EP+DT+ST+DD) |
| AC-018 | N — no numeric boundary | Y — no-purchase user vs other user's records | Y — no own records means empty and no cross-user leak | N — no lifecycle transition | N — two privacy paths only | TC-016 (EP+DT+Security) |
| AC-019 | N — no numeric boundary | Y — ISSUED ticket status | Y — issued and owner show QR | Y — ISSUED is valid entry state | N — one status | TC-017 (EP+DT+ST+Security) |
| AC-020 | N — no numeric boundary | Y — CANCELLED/REJECTED/EXCHANGED classes | Y — invalid status suppresses valid QR | Y — invalid ticket states are not entry-valid | Y — three invalid statuses share expected result | TC-018 (EP+DT+ST+DD) |
| AC-021 | N — one-time count is tested as state, not numeric range | Y — ISSUED not scanned class | Y — valid token and issued state allow scan | Y — ISSUED to USED/SCANNED | N — one success path | TC-019 (EP+DT+ST+Security) |
| AC-022 | N — repeated scan is state, not numeric range | Y — USED/SCANNED class | Y — already scanned rejects scan | Y — USED/SCANNED remains USED/SCANNED | N — one repeat path | TC-020 (EP+DT+ST+Security) |
| AC-023 | Y — 10-minute exchange/admin confirmation windows | Y — higher-priced target class | Y — issued ticket plus higher available seat plus admin confirm | Y — ISSUED old ticket to EXCHANGED, new ticket ISSUED | N — one higher-price path | TC-021, TC-022 (BVA+EP+DT+ST) |
| AC-024 | N — cheaper/unavailable are categorical guards | Y — cheaper and unavailable classes | Y — cheaper OR unavailable blocks exchange | N — blocked before checkout, no state transition | N — two variants only | TC-024 (EP+DT) |

#### Coverage Category Checklist

| Feature / Flow | AC +/- | BR / Rule | Basic Flow | EP/BVA | Decision / Data-Driven | State Transition | Corner / Error Guessing | Impact / Regression | NFR | SIT | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Auth | covered | covered | covered | covered | covered | covered | covered | covered | covered | covered | TC-001, TC-002 |
| Admin inventory/pricing/QR | covered | covered | covered | covered | covered | covered | covered | covered | covered | covered | TC-003..TC-006 |
| User browse/checkout/payment | covered | covered | covered | covered | covered | covered | covered | covered | covered | covered | TC-007..TC-012, TC-023 |
| Admin confirmation | covered | covered | covered | covered | covered | covered | covered | covered | covered | covered | TC-013, TC-014, TC-022 |
| Ticket history/detail/scan | covered | covered | covered | covered | covered | covered | covered | covered | covered | covered | TC-015..TC-020 |
| Exchange + local runtime | covered | covered | covered | covered | covered | covered | covered | covered | covered | covered | TC-021, TC-022, TC-024 |

<!-- ID: TC-001 -->
<!-- VERIFIES: US-001 -->
### TC-001: [US-001][AC-001][EP+DT+ST] Mock OTP login succeeds for email or phone `[planned-automated]` `P0`

**Area**: AUTH
**Traceability**: FR-001, US-001, AC-001, NFR-003
**Design states referenced**: SCREEN-001 §Input/Success
**API / NFR refs**: API-001, API-002, NFR-003
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local Docker Compose or Testcontainers integration env
**Data needs**: synthetic identifier `fan1@example.test` and mock OTP `000000`; repeat with `84901234567`
**Teardown / reset**: delete session/OTP records for identifiers
**Depends on**: —
**Automation intent**: Auto=Y; backend integration + web login smoke; requires API-001/API-002 and login selectors
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- A synthetic user identifier is not currently authenticated and mock OTP provider returns `000000`.
**When**:
- POST `/api/v1/auth/otp/request` with the identifier, then POST `/api/v1/auth/otp/verify` with the same identifier and OTP `000000`.
**Then**:
- [ ] OTP request response is successful and does not expose secrets.
- [ ] Verify response returns an authenticated session token/cookie.
- [ ] Session owner matches the identifier.
- [ ] Protected purchase APIs can be called with the session and are not rejected for missing auth.

**Test Data**:
```json
{"identifiers":["fan1@example.test","84901234567"],"otp":"000000","expected_session":"authenticated"}
```

<!-- ID: TC-002 -->
<!-- VERIFIES: US-001 -->
### TC-002: [US-001][AC-002][EP+DT+ST+Security] Protected checkout and exchange require login `[planned-automated]` `P0`

**Area**: AUTH
**Traceability**: FR-001, US-001, AC-002, BR-001, NFR-003
**Design states referenced**: SCREEN-001 §Login required/Error
**API / NFR refs**: API-005, API-014, NFR-003
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Security
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env
**Data needs**: one open match, one issued ticket owned by `fan1`, unauthenticated request context
**Teardown / reset**: reset orders/tickets created by fixture
**Depends on**: TC-001
**Automation intent**: Auto=Y; security integration tests for protected mutation endpoints
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- No session token/cookie is present.
**When**:
- Call `POST /api/v1/orders/checkout` and `POST /api/v1/tickets/{ticketId}/exchange/checkout`.
**Then**:
- [ ] Both calls return 401/403 using the standard error envelope.
- [ ] No order, hold, exchange order, or ticket mutation is created.
- [ ] UI routes send the user to SCREEN-001 before continuing.

**Test Data**:
```json
{"auth":null,"expected_error":"AUTH_REQUIRED","protected_endpoints":["API-005","API-014"]}
```

<!-- ID: TC-003 -->
<!-- VERIFIES: US-006 -->
### TC-003: [US-006][AC-011][EP+DT+ST] Admin opens a created match for sale `[planned-automated]` `P0`

**Area**: ADMIN
**Traceability**: FR-006, US-006, AC-011, BR-008
**Design states referenced**: SCREEN-006 §Populated
**API / NFR refs**: API-010, API-003
**Manual / Auto boundary**: automated
**Test Level**: e2e
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local Docker Compose
**Data needs**: admin session, match payload with status `OPEN_FOR_SALE`
**Teardown / reset**: delete created match/seats
**Depends on**: TC-001
**Automation intent**: Auto=Y; admin API + user list e2e
**External QA handoff needs**: N/A
**Owner of execution context**: Dev + QA

**Given**:
- Admin is authenticated.
**When**:
- Admin creates a match with status `OPEN_FOR_SALE`, then user opens the match list.
**Then**:
- [ ] API-010 returns created match with `OPEN_FOR_SALE`.
- [ ] API-003 returns the match in the user list.
- [ ] User can open seat selection for that match.

**Test Data**:
```json
{"match":{"home":"CLB A","away":"CLB B","status":"OPEN_FOR_SALE"}}
```

<!-- ID: TC-004 -->
<!-- VERIFIES: US-006 -->
### TC-004: [US-006][AC-012][EP+DT+ST] Cancelled or closed match blocks new purchase `[planned-automated]` `P0`

**Area**: ADMIN
**Traceability**: FR-006, US-006, AC-012, BR-008
**Design states referenced**: SCREEN-006 §Status change, SCREEN-002 §Filtered/Blocked
**API / NFR refs**: API-010, API-003, API-005
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env
**Data needs**: matches with `CANCELLED` and `CLOSED`, available seats
**Teardown / reset**: reset match statuses
**Depends on**: TC-003
**Automation intent**: Auto=Y; data-driven integration test over statuses
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Existing matches have status `CANCELLED` and `CLOSED`.
**When**:
- User opens match list and attempts checkout for those matches by API.
**Then**:
- [ ] Non-selling matches are absent from purchasable list or visibly non-purchasable.
- [ ] Checkout returns `MATCH_NOT_OPEN_FOR_SALE`.
- [ ] No seat hold/order is created.

**Test Data**:
```json
{"statuses":["CANCELLED","CLOSED"],"expected_error":"MATCH_NOT_OPEN_FOR_SALE"}
```

<!-- ID: TC-005 -->
<!-- VERIFIES: US-007 -->
### TC-005: [US-007][AC-013][EP+DT+ST] New checkout uses latest active price after admin update `[planned-automated]` `P0`

**Area**: ADMIN
**Traceability**: FR-007, US-007, AC-013, BR-004
**Design states referenced**: SCREEN-007 §Price configured
**API / NFR refs**: API-012, API-005
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env
**Data needs**: seat `A-T1-001`, old price 100000, new price 120000
**Teardown / reset**: reset price_versions and orders
**Depends on**: TC-003
**Automation intent**: Auto=Y; price service integration test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Admin has generated a seat and set old price `100000`.
**When**:
- Admin updates the seat price to `120000`, then user starts a new checkout for that seat.
**Then**:
- [ ] Checkout order item has price snapshot `120000`.
- [ ] Total amount equals the sum of new snapshots.
- [ ] Older inactive price version is not used for this new order.

**Test Data**:
```json
{"seatCode":"A-T1-001","oldPrice":100000,"newPrice":120000,"expectedSnapshot":120000}
```

<!-- ID: TC-006 -->
<!-- VERIFIES: US-007 -->
### TC-006: [US-007][AC-014][EP+DT+ST] Existing checkout keeps original snapshot after price update `[planned-automated]` `P0`

**Area**: CHECKOUT
**Traceability**: FR-007, US-007, AC-014, BR-004
**Design states referenced**: SCREEN-007 §Snapshot edge, SCREEN-004 §Amount restated
**API / NFR refs**: API-012, API-005
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Regression
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env
**Data needs**: checkout order created before price update
**Teardown / reset**: cancel order and reset price_versions
**Depends on**: TC-005
**Automation intent**: Auto=Y; regression test for price snapshot
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- User has an active checkout order with snapshot price `100000`.
**When**:
- Admin updates active price to `120000`.
**Then**:
- [ ] Existing order item remains `100000`.
- [ ] Existing checkout total remains unchanged.
- [ ] A later new checkout uses `120000`.

**Test Data**:
```json
{"originalSnapshot":100000,"updatedActivePrice":120000}
```

<!-- ID: TC-007 -->
<!-- VERIFIES: US-002 -->
### TC-007: [US-002][AC-003][EP+ST] User sees OPEN_FOR_SALE match and enters seat selection `[planned-automated]` `P0`

**Area**: CHECKOUT
**Traceability**: FR-002, US-002, AC-003
**Design states referenced**: SCREEN-002 §Populated
**API / NFR refs**: API-003, API-004
**Manual / Auto boundary**: automated
**Test Level**: e2e
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local Docker Compose
**Data needs**: one open match with generated seats
**Teardown / reset**: reset match/seat fixture
**Depends on**: TC-003
**Automation intent**: Auto=Y; Playwright/web and Flutter happy path
**External QA handoff needs**: N/A
**Owner of execution context**: Dev + QA

**Given**:
- Match `M-OPEN` is `OPEN_FOR_SALE`.
**When**:
- User opens match list and selects `M-OPEN`.
**Then**:
- [ ] Match appears with sale information.
- [ ] Seat selection opens and calls API-004.
- [ ] Sections/floors/prices are visible.

**Test Data**:
```json
{"matchStatus":"OPEN_FOR_SALE","expectedScreen":"SCREEN-003"}
```

<!-- ID: TC-008 -->
<!-- VERIFIES: US-002 -->
### TC-008: [US-002][AC-004][EP+DT+DD+ST] Non-purchasable match statuses do not start purchase `[planned-automated]` `P0`

**Area**: CHECKOUT
**Traceability**: FR-002, US-002, AC-004, BR-008
**Design states referenced**: SCREEN-002 §Filtered/Blocked
**API / NFR refs**: API-003, API-005
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env
**Data needs**: matches in `SOLD_OUT`, `CANCELLED`, `CLOSED`
**Teardown / reset**: reset matches
**Depends on**: TC-003
**Automation intent**: Auto=Y; data-driven status test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Matches exist in non-selling statuses.
**When**:
- User lists matches and attempts checkout for each non-selling match.
**Then**:
- [ ] Match is not available for new purchase.
- [ ] Checkout is rejected.
- [ ] No order/hold is created.

**Test Data**:
```json
{"statuses":["SOLD_OUT","CANCELLED","CLOSED"],"expected":"not_purchasable"}
```

<!-- ID: TC-009 -->
<!-- VERIFIES: US-003 -->
### TC-009: [US-003][AC-005][BVA+EP+DT+ST+DD] Select 1 to 5 available seat codes with current prices `[planned-automated]` `P0`

**Area**: CHECKOUT
**Traceability**: FR-003, US-003, AC-005, BR-003
**Design states referenced**: SCREEN-003 §Seat map populated, DS-COMP-001
**API / NFR refs**: API-004
**Manual / Auto boundary**: automated
**Test Level**: e2e
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local Docker Compose
**Data needs**: available seats across A/B/C/D, floors 1/2, A VIP with distinct prices
**Teardown / reset**: clear selected state and reset seats
**Depends on**: TC-007
**Automation intent**: Auto=Y; component + e2e selection test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev + QA

**Given**:
- User is logged in and the seat map has available seat codes.
**When**:
- User selects 1 seat, then expands selection up to 5 seats.
**Then**:
- [ ] Each selected seat is marked selected and remains counted once.
- [ ] Seat code, section, floor/VIP, price, and status color are visible.
- [ ] The selected total equals the sum of current visible prices.

**Test Data**:
```json
{"seatCounts":[1,5],"seatCodes":["A-VIP-001","A-T1-001","B-T2-001","C-T1-001","D-T2-001"]}
```

<!-- ID: TC-010 -->
<!-- VERIFIES: US-003 -->
### TC-010: [US-003][AC-006][BVA+DT+ST] Sixth selected seat is blocked `[planned-automated]` `P0`

**Area**: CHECKOUT
**Traceability**: FR-003, US-003, AC-006, BR-003
**Design states referenced**: SCREEN-003 §Limit error
**API / NFR refs**: API-004
**Manual / Auto boundary**: automated
**Test Level**: component
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local
**Data needs**: six available seats
**Teardown / reset**: clear selected state
**Depends on**: TC-009
**Automation intent**: Auto=Y; UI component plus backend validation for max 5
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- User already selected 5 seats.
**When**:
- User selects a sixth available seat.
**Then**:
- [ ] UI blocks the action with max-5 message.
- [ ] Selected seat count remains 5.
- [ ] Backend checkout with 6 seat IDs returns validation error and creates no order.

**Test Data**:
```json
{"selectedBefore":5,"attemptedAfter":6,"expected_error":"MAX_SEATS_EXCEEDED"}
```

<!-- ID: TC-011 -->
<!-- VERIFIES: US-004 -->
### TC-011: [US-004][AC-007][BVA+EP+DT+ST+DD] Checkout holds selected seats, snapshots prices, and moves to pending payment completion `[planned-automated]` `P0`

**Area**: CHECKOUT
**Traceability**: FR-004, FR-005, US-004, US-005, AC-007, AC-009, BR-002, BR-004, BR-005, NFR-002
**Design states referenced**: SCREEN-004 §QR/amount/countdown, SCREEN-005 §Waiting
**API / NFR refs**: API-005, API-006, NFR-002
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: SIT
**Export target**: sit
**Smoke**: Y
**Environment**: local integration env
**Data needs**: logged-in user, 1 and 5 available seat variants, default QR config, idempotency key
**Teardown / reset**: cancel order and release seats
**Depends on**: TC-009
**Automation intent**: Auto=Y; checkout API + idempotency + UI e2e smoke
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- User selected available seats and sends a unique `Idempotency-Key`.
**When**:
- User calls checkout, views QR page, then taps payment completed before expiry.
**Then**:
- [ ] Order is created with status HELD/checkout-active.
- [ ] Each order item stores checkout-time price snapshot.
- [ ] Seats are unavailable to other users while held.
- [ ] Payment-completed moves order to `PENDING_ADMIN_CONFIRM`.
- [ ] QR config shown is the active default QR and total amount matches snapshots.

**Test Data**:
```json
{"seatCounts":[1,5],"holdDuration":"PT10M","idempotencyKey":"tc-011-checkout-001","expectedStatus":"PENDING_ADMIN_CONFIRM"}
```

<!-- ID: TC-012 -->
<!-- VERIFIES: US-004 -->
### TC-012: [US-004][AC-008][BVA+DT+ST] Expired checkout hold releases seats and rejects payment completion `[planned-automated]` `P0`

**Area**: CHECKOUT
**Traceability**: FR-004, FR-005, US-004, US-005, AC-008, AC-010, BR-002
**Design states referenced**: SCREEN-004 §Expired, SCREEN-005 §Expired
**API / NFR refs**: API-005, API-006, NFR-002
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env with controllable clock
**Data needs**: held order with `holdExpiresAt = now - 1s`
**Teardown / reset**: reset seats/orders
**Depends on**: TC-011
**Automation intent**: Auto=Y; scheduler/time-travel integration test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- A checkout hold has exceeded 10 minutes.
**When**:
- Expiry job runs and user attempts payment completion.
**Then**:
- [ ] Order status is `EXPIRED`.
- [ ] Held seats return to `AVAILABLE`.
- [ ] Payment completion returns `ORDER_EXPIRED`.
- [ ] User must create a new order.

**Test Data**:
```json
{"holdAge":"PT10M+1S","expectedSeatStatus":"AVAILABLE","expected_error":"ORDER_EXPIRED"}
```

<!-- ID: TC-013 -->
<!-- VERIFIES: US-008 -->
### TC-013: [US-008][AC-015][BVA+DT+ST] Admin confirms pending order within 10 minutes and issues tickets `[planned-automated]` `P0`

**Area**: ADMIN
**Traceability**: FR-008, US-008, AC-015, BR-005
**Design states referenced**: SCREEN-008 §Pending list/Confirm
**API / NFR refs**: API-007, EVT-002
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: SIT
**Export target**: sit
**Smoke**: Y
**Environment**: local integration env
**Data needs**: `PENDING_ADMIN_CONFIRM` order within confirmation window, admin session, idempotency key
**Teardown / reset**: cancel created ticket/seat state or reset DB
**Depends on**: TC-011
**Automation intent**: Auto=Y; admin decision integration test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Order is `PENDING_ADMIN_CONFIRM` and not expired.
**When**:
- Admin confirms payment with `Idempotency-Key`.
**Then**:
- [ ] Order becomes confirmed/issued.
- [ ] Ticket records are created with status `ISSUED`.
- [ ] Selected seats are no longer available for purchase.
- [ ] Audit log records admin decision without sensitive transfer data.

**Test Data**:
```json
{"orderStatus":"PENDING_ADMIN_CONFIRM","decision":"CONFIRM","idempotencyKey":"tc-013-confirm-001"}
```

<!-- ID: TC-014 -->
<!-- VERIFIES: US-008 -->
### TC-014: [US-008][AC-016][BVA+EP+DT+ST] Admin rejection or confirmation expiry releases seats `[planned-automated]` `P0`

**Area**: ADMIN
**Traceability**: FR-008, US-008, AC-016, BR-005, NFR-004
**Design states referenced**: SCREEN-008 §Rejected/Expired, DS-COMP-005
**API / NFR refs**: API-007, NFR-004
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env with controllable clock
**Data needs**: one pending order for reject path, one expired pending order
**Teardown / reset**: reset orders/seats/audit logs
**Depends on**: TC-011
**Automation intent**: Auto=Y; data-driven reject/expiry integration test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Orders are `PENDING_ADMIN_CONFIRM`.
**When**:
- Admin rejects one order, and expiry job processes another order older than 10 minutes.
**Then**:
- [ ] Rejected order status is `REJECTED` or `CANCELLED` per implementation enum.
- [ ] Expired pending order is cancelled/expired.
- [ ] Seats from both orders return to `AVAILABLE`.
- [ ] Audit/log evidence contains operation, order ID, actor where applicable, status, duration/error code without PII.

**Test Data**:
```json
{"branches":["admin_reject","confirmation_expiry"],"expectedSeatStatus":"AVAILABLE"}
```

<!-- ID: TC-015 -->
<!-- VERIFIES: US-009 -->
### TC-015: [US-009][AC-017][EP+DT+ST+DD] Purchase history shows only current user's records and statuses `[planned-automated]` `P0`

**Area**: TICKET
**Traceability**: FR-009, US-009, AC-017, BR-001
**Design states referenced**: SCREEN-009 §Populated
**API / NFR refs**: API-008
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env
**Data needs**: fan1 records in pending/issued/rejected/exchanged/scanned states; fan2 records
**Teardown / reset**: reset orders/tickets
**Depends on**: TC-013
**Automation intent**: Auto=Y; ownership and status rendering tests
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Fan1 and fan2 both have orders/tickets.
**When**:
- Fan1 calls `GET /api/v1/orders`.
**Then**:
- [ ] Response includes only fan1 records.
- [ ] Current statuses match database state.
- [ ] Fan2 order/ticket IDs are absent.

**Test Data**:
```json
{"viewer":"fan1@example.test","forbiddenOwner":"fan2@example.test","statuses":["PENDING_ADMIN_CONFIRM","ISSUED","REJECTED","EXCHANGED","USED_SCANNED"]}
```

<!-- ID: TC-016 -->
<!-- VERIFIES: US-009 -->
### TC-016: [US-009][AC-018][EP+DT+Security] Empty purchase history shows no other user's data `[planned-automated]` `P0`

**Area**: TICKET
**Traceability**: FR-009, US-009, AC-018, BR-001
**Design states referenced**: SCREEN-009 §Empty
**API / NFR refs**: API-008
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Security
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env
**Data needs**: fan_empty has no purchases; fan2 has purchases
**Teardown / reset**: reset users/orders/tickets
**Depends on**: TC-015
**Automation intent**: Auto=Y; IDOR/ownership test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Logged-in user has no purchases and another user has purchases.
**When**:
- User opens purchase history.
**Then**:
- [ ] API returns empty list for the logged-in user.
- [ ] UI shows empty state.
- [ ] No other user's order, ticket, seat, or QR details are visible.

**Test Data**:
```json
{"viewer":"fan_empty@example.test","otherUser":"fan2@example.test","expected":[]}
```

<!-- ID: TC-017 -->
<!-- VERIFIES: US-010 -->
### TC-017: [US-010][AC-019][EP+DT+ST+Security] Issued ticket detail shows signed QR without PII `[planned-automated]` `P0`

**Area**: TICKET
**Traceability**: FR-009, US-010, AC-019, BR-006, NFR-003
**Design states referenced**: SCREEN-010 §Issued QR, DS-COMP-003
**API / NFR refs**: API-009, NFR-003
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Security
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env
**Data needs**: fan-owned `ISSUED` ticket
**Teardown / reset**: reset ticket
**Depends on**: TC-013
**Automation intent**: Auto=Y; QR token unit/integration tests and UI smoke
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Fan owns a ticket with status `ISSUED`.
**When**:
- Fan opens `GET /api/v1/tickets/{ticketId}`.
**Then**:
- [ ] Response includes match, seat code, ticket status, and QR/e-ticket token.
- [ ] QR token is signed/opaque and does not contain email, phone, or full name in decodable plaintext.
- [ ] UI shows a large QR card and valid status.

**Test Data**:
```json
{"ticketStatus":"ISSUED","forbiddenPlaintext":["fan1@example.test","84901234567","Nguyen Van A"]}
```

<!-- ID: TC-018 -->
<!-- VERIFIES: US-010 -->
### TC-018: [US-010][AC-020][EP+DT+ST+DD] Invalid ticket statuses are not presented as valid entry tickets `[planned-automated]` `P0`

**Area**: TICKET
**Traceability**: FR-009, US-010, AC-020, BR-006
**Design states referenced**: SCREEN-010 §Invalid/Status
**API / NFR refs**: API-009
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env
**Data needs**: fan-owned tickets in `CANCELLED`, `REJECTED`, `EXCHANGED`
**Teardown / reset**: reset tickets
**Depends on**: TC-017
**Automation intent**: Auto=Y; data-driven invalid ticket status test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Fan owns non-entry-valid tickets.
**When**:
- Fan opens ticket detail for each status.
**Then**:
- [ ] UI/API does not present the ticket as valid for entry.
- [ ] QR is absent, disabled, or clearly invalid according to design.
- [ ] Status chip matches the ticket status.

**Test Data**:
```json
{"invalidStatuses":["CANCELLED","REJECTED","EXCHANGED"],"expectedEntryValid":false}
```

<!-- ID: TC-019 -->
<!-- VERIFIES: US-011 -->
### TC-019: [US-011][AC-021][EP+DT+ST+Security] First valid ticket scan marks ticket USED/SCANNED `[planned-automated]` `P0`

**Area**: SCAN
**Traceability**: FR-010, US-011, AC-021, BR-006
**Design states referenced**: SCREEN-011 §Scan success
**API / NFR refs**: API-013, EVT-003
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: SIT
**Export target**: sit
**Smoke**: Y
**Environment**: local integration env
**Data needs**: valid signed QR token for `ISSUED` ticket, idempotency key
**Teardown / reset**: reset ticket status
**Depends on**: TC-017
**Automation intent**: Auto=Y; atomic update integration test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Ticket is `ISSUED` and has not been scanned.
**When**:
- Scan consumer calls `POST /api/v1/tickets/scan` with valid token and `Idempotency-Key`.
**Then**:
- [ ] Response is successful and reports scanned/used.
- [ ] Ticket status changes to `USED/SCANNED`.
- [ ] Scan event/audit evidence is created without PII.

**Test Data**:
```json
{"initialStatus":"ISSUED","expectedStatus":"USED_SCANNED","idempotencyKey":"tc-019-scan-001"}
```

<!-- ID: TC-020 -->
<!-- VERIFIES: US-011 -->
### TC-020: [US-011][AC-022][EP+DT+ST+Security] Repeated scan is rejected and ticket remains scanned `[planned-automated]` `P0`

**Area**: SCAN
**Traceability**: FR-010, US-011, AC-022, BR-006
**Design states referenced**: SCREEN-011 §Already scanned error
**API / NFR refs**: API-013
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Security
**Export target**: functional
**Smoke**: Y
**Environment**: local integration env
**Data needs**: ticket already `USED/SCANNED`
**Teardown / reset**: reset ticket
**Depends on**: TC-019
**Automation intent**: Auto=Y; repeated scan state guard test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Ticket is already `USED/SCANNED`.
**When**:
- Scan consumer submits the same QR token again.
**Then**:
- [ ] API returns `TICKET_ALREADY_SCANNED` or equivalent conflict error.
- [ ] Ticket remains `USED/SCANNED`.
- [ ] No second successful scan event is created.

**Test Data**:
```json
{"initialStatus":"USED_SCANNED","expected_error":"TICKET_ALREADY_SCANNED"}
```

<!-- ID: TC-021 -->
<!-- VERIFIES: US-012 -->
### TC-021: [US-012][AC-023][BVA+EP+DT+ST] Higher-priced exchange checkout holds new seat and charges difference `[planned-automated]` `P0`

**Area**: EXCHANGE
**Traceability**: FR-011, US-012, AC-023, BR-007, NFR-002
**Design states referenced**: SCREEN-012 §Eligible exchange, SCREEN-004 §Difference QR
**API / NFR refs**: API-014, NFR-002
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: SIT
**Export target**: sit
**Smoke**: Y
**Environment**: local integration env
**Data needs**: issued ticket price 100000, replacement available seat price 150000, default QR
**Teardown / reset**: cancel exchange order and reset seats/tickets
**Depends on**: TC-017
**Automation intent**: Auto=Y; exchange checkout integration test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- User owns an `ISSUED` ticket and selects an available higher-priced replacement seat.
**When**:
- User starts exchange checkout with `Idempotency-Key`.
**Then**:
- [ ] Replacement seat is held for 10 minutes.
- [ ] Amount due equals replacement price minus original ticket price.
- [ ] Old ticket remains `ISSUED` until admin confirms exchange.
- [ ] Default QR is shown for the difference amount.

**Test Data**:
```json
{"oldPrice":100000,"newPrice":150000,"expectedDifference":50000,"idempotencyKey":"tc-021-exchange-001"}
```

<!-- ID: TC-022 -->
<!-- VERIFIES: US-012 -->
### TC-022: [US-012][AC-023][BVA+DT+ST] Admin confirms exchange and retires old ticket `[planned-automated]` `P0`

**Area**: EXCHANGE
**Traceability**: FR-012, US-012, AC-023, BR-007, BR-008
**Design states referenced**: SCREEN-008 §Exchange confirm, SCREEN-012 §Confirmed
**API / NFR refs**: API-015, EVT-004
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: SIT
**Export target**: sit
**Smoke**: Y
**Environment**: local integration env
**Data needs**: pending exchange order within confirmation window, admin session, idempotency key
**Teardown / reset**: reset old/new tickets and seats
**Depends on**: TC-021
**Automation intent**: Auto=Y; exchange confirmation integration test
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- Exchange order is pending admin confirmation.
**When**:
- Admin confirms exchange payment.
**Then**:
- [ ] New ticket is issued for replacement seat.
- [ ] Old ticket becomes `EXCHANGED`.
- [ ] Old seat returns to `AVAILABLE`.
- [ ] Replacement seat is no longer available.
- [ ] Audit/event evidence records exchange confirmation.

**Test Data**:
```json
{"decision":"CONFIRM","oldTicketExpected":"EXCHANGED","newTicketExpected":"ISSUED"}
```

<!-- ID: TC-023 -->
<!-- VERIFIES: NFR-002 -->
### TC-023: [NFR-002][Performance+CornerCase] Concurrent checkout permits only one active hold per seat `[planned-automated]` `P0`

**Area**: PERF
**Traceability**: FR-004, US-004, NFR-001, NFR-002
**Design states referenced**: SCREEN-003 §Seat unavailable after hold
**API / NFR refs**: API-005, NFR-001, NFR-002
**Manual / Auto boundary**: automated
**Test Level**: integration
**Test Type**: Performance
**Export target**: sit
**Smoke**: Y
**Environment**: local integration env with PostgreSQL/Testcontainers
**Data needs**: one open match, one available target seat, two authenticated users, two idempotency keys
**Teardown / reset**: reset orders/order_items/seats/idempotency_records
**Depends on**: TC-011
**Automation intent**: Auto=Y; concurrency integration test and demo load smoke
**External QA handoff needs**: N/A
**Owner of execution context**: Dev

**Given**:
- The same seat is `AVAILABLE` and two users attempt checkout concurrently.
**When**:
- Both users submit `POST /api/v1/orders/checkout` for the same seat at the same time.
**Then**:
- [ ] Exactly one checkout succeeds.
- [ ] Exactly one active order_item/hold exists for the seat.
- [ ] Losing request receives conflict error.
- [ ] Under 50 concurrent demo browse/seat/checkout-smoke requests, API p95 is recorded and target is <= 800ms excluding cold start.

**Test Data**:
```json
{"concurrentUsers":2,"demoLoadUsers":50,"targetP95Ms":800,"expectedActiveHolds":1}
```

<!-- ID: TC-024 -->
<!-- VERIFIES: US-012 -->
### TC-024: [US-012][AC-024][EP+DT] Cheaper or unavailable replacement seat blocks exchange and Docker smoke passes `[planned-automated]` `P1`

**Area**: EXCHANGE
**Traceability**: FR-011, US-012, AC-024, BR-007, NFR-005
**Design states referenced**: SCREEN-012 §Blocked exchange, DS-COMP-001
**API / NFR refs**: API-014, NFR-005
**Manual / Auto boundary**: automated
**Test Level**: e2e
**Test Type**: Functional
**Export target**: functional
**Smoke**: Y
**Environment**: local Docker Compose
**Data needs**: issued ticket, cheaper available seat, equal/higher unavailable seat, local runtime seed
**Teardown / reset**: reset exchange attempts and Docker DB seed as needed
**Depends on**: TC-021
**Automation intent**: Auto=Y; e2e negative exchange plus Docker Compose smoke
**External QA handoff needs**: N/A
**Owner of execution context**: Dev + QA

**Given**:
- User owns an `ISSUED` ticket and local Docker Compose services are running.
**When**:
- User attempts exchange to a cheaper seat and then to an unavailable seat.
**Then**:
- [ ] Both attempts are blocked before checkout.
- [ ] No exchange order or new hold is created.
- [ ] Old ticket remains `ISSUED`.
- [ ] Docker Compose health/smoke path can still complete auth → browse → checkout → admin confirm → ticket detail.

**Test Data**:
```json
{"branches":["cheaper_available","higher_unavailable"],"expected_error":"EXCHANGE_TARGET_NOT_ELIGIBLE","dockerSmoke":true}
```
