---
status: DRAFT
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# Test Cases — {{PROJECT_NAME}}

<!-- This file is the Living Truth root for the Test phase. It accumulates test cases
     across sprints. AI never writes this file directly — `apply_proposal.py` merges
     anchored TC items from each sprint's `testing/proposals/test-cases-v{X}.md` at sprint seal.

     Phase 9 changes vs 1.x:
     - ID format `TC-{AREA}-{NNN}` → flat `TC-{NNN}`. Feature area moves to `**Area**:` body field.
     - Stable ID anchor convention: every test case is preceded by `<!-- ID: TC-NNN -->` + optional `<!-- VERIFIES: ID-NNN -->` trace tag. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each TC block MUST start with:
         <!-- ID: TC-NNN -->
         <!-- VERIFIES: ID-NNN -->   (optional trace tag — preserves but does not route)
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
- **Traceability**: every TC has `**Traceability**: US-NNN, FR-NNN, NFR-NNN` — no trace = no traceability. The optional `<!-- VERIFIES: ID-NNN -->` anchor tag carries the primary verified item for cross-doc tooling.
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

<!-- PRISM:LT-SKELETON-END -->

## 3. Rule / Branch Inventory

<!-- PROMOTED TO LIVING TRUTH. Author this section in the proposal as a SINGLETON anchored block:
     the anchor id is ALWAYS TEST-COVERAGE-001 (never increment) on its own line, immediately above
     an `### Rule / Branch Inventory` H3 + the table — exactly the raw block shown below. It then
     merges into `/docs/testing/test-cases.md` at sprint seal via apply_proposal.py.
     `## New` in sprint 1, `## Updated` (replace-in-place, ID fixed) in later sprints: re-author the
     FULL CUMULATIVE table each sprint — carry every prior row forward, add this sprint's new
     AC/BR/branch rows, and refresh Covered TC IDs for any rule newly covered. Same singleton
     regeneration pattern as PRD-OVERVIEW-001 / ARCH-OVERVIEW-001. -->
<!-- Required when upstream artifacts contain AC IDs, BR IDs, Rule IDs, decision-table rows, named flow branches, or state transitions. -->
<!-- Every in-scope item must map to TC IDs or have N/A + reason. -->

<!-- ID: TEST-COVERAGE-001 -->
### Rule / Branch Inventory

| Rule / AC / BR / Branch ID | Source Ref | Description | Covered TC IDs | Status | Gap / N/A Reason |
|---|---|---|---|---|---|
| AC-NNN | `epics/EP-NNN-{slug}.md §User Stories § US-NNN` | | TC-NNN | covered / partial / gap / N/A | |
| BR-NNN | `/docs/product/prd.md §6.3` | | TC-NNN | covered / partial / gap / N/A | |

## 3.5 Per-AC Technique Decision Matrix

<!-- Mandatory before authoring TC blocks (see `core/phase-test.md` step 6.5).
     This matrix forces a Y/N decision per AC × ISTQB-technique. Y must cite the AC clause;
     N must give a one-line concrete reason. Every Y must produce ≥1 TC with the technique
     tag in its title prefix. Rules in `core/standards/testing-standards.md §1.5`. -->
<!-- PROPOSAL-ONLY working artifact: gates `approve test`, lives in the sprint proposal, and is
     NOT promoted to Living Truth (unlike §3 Rule / Branch Inventory). The matrix is per-sprint
     authoring RATIONALE (why each technique was chosen for this sprint's ACs); the durable
     coverage record in LT is §3 + the TC blocks' own trace + Technique title prefixes. Do NOT
     anchor this section. -->

| AC ID | BVA Y/N + reason | EP Y/N + reason | DT Y/N + reason | ST Y/N + reason | DD Y/N + reason | TC IDs generated |
|---|---|---|---|---|---|---|
| US-NNN AC-NNN | Y — "cache TTL = 300s" defines a 300s boundary | N — single input class (no enum/role partitions) | N — single condition with linear outcome | Y — cache lifecycle: cold → warm → invalidate → warm | N — only one variant per state | TC-001 (BVA), TC-002 (ST) |
| US-NNN AC-NNN | *fill all 5 cells (Y with clause / N with reason) before writing TC blocks for this AC* | | | | | |

<!-- US-level N/A escape hatch: when a US has no AC IDs, or all five techniques are clearly
     non-applicable to the entire US, write a single row with `AC ID` = `US-NNN (whole)` and
     give a one-line reason in any cell — the rest of the row may be left empty. -->

**Filling rules**:
- Y cell — quote the AC clause that triggers the technique (per `testing-standards.md §1.5`). Concrete clauses only: a numeric value, a list of classes, an explicit condition tuple, a state set, or a variant set.
- N cell — give a concrete reason tied to the AC (e.g. `N — input is a single role enum, no quantitative edge`). Avoid bare phrases like `N — not applicable` / `N — không cần thiết`; a future validator will flag those as insufficient.
- TC IDs column — list every TC that satisfies a Y cell on this row, with the technique tag in parentheses for cross-check (e.g. `TC-001 (BVA)`). A TC using multiple techniques is listed once but counted under each Y row that it satisfies.
- Current validator (TEST-3b) checks the trace + Technique title prefix and emits warnings for missing or malformed prefixes. A future minor release will additionally check matrix cell completeness and N-reason quality, and will hard-block `approve test` on issues. Generators SHOULD complete the full matrix now as a quality gate.
- Non-technique edge cases (dependency outage / search backend unreachable, object-storage 404, queue partition, race conditions, mid-request client disconnect, container OOM) belong to §4 Coverage Category Checklist under `Corner / Error Guessing`, NOT in this matrix — still required regardless of matrix outcome. Disambiguation: a numeric boundary like signed-URL TTL = 10 min is **BVA** (matrix Y), not Corner; a state transition crossing a permission change is **ST** (matrix Y, optionally `+Security`), not Corner. See `core/standards/testing-standards.md §1.5` → *Non-technique edge cases* for the full list.

## 4. Coverage Category Checklist

<!-- Use this as an internal quality guard while authoring. Not every feature needs every category, but omissions need a reason. -->
<!-- PROPOSAL-ONLY working artifact: a per-sprint self-guard that gates `approve test`; NOT promoted
     to Living Truth and NOT anchored (same as §3.5). §3 Rule / Branch Inventory is the part that
     reaches LT. -->

| Feature / Flow | AC +/- | BR / Rule | Basic Flow | EP/BVA | Decision / Data-Driven | State Transition | Corner / Error Guessing | Impact / Regression | NFR | SIT | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | covered / N/A | covered / N/A | covered / N/A | covered / N/A | covered / N/A | covered / N/A | covered / N/A | covered / N/A | covered / N/A | covered / N/A | |

---

## 5. Functional Test Cases

<!-- One block per TC. Copy the template below. Each TC starts with its `<!-- ID: TC-NNN -->` anchor line. -->

<!-- ID: TC-NNN -->
<!-- VERIFIES: US-NNN -->
### TC-NNN: [US-NNN][AC-NNN][Technique] {{TEST_CASE_TITLE}} `[planned-automated]` `P0`

**Classification and trace**

**Area**: AUTH | ORDER | PAYMENT
**Traceability**: FR-NNN, US-NNN, NFR-NNN
**Design states referenced**: SCREEN-NNN §Empty / Error states, or N/A
**API / NFR refs**: API-NNN, NFR-NNN, or N/A

**Execution profile**

**Manual / Auto boundary**: `automated` | `manual`
**Test Level**: `component` | `integration` | `e2e`
**Test Type**: `Functional`
**Export target**: `functional`
**Smoke**: `Y` | `N`

**Environment and data**

**Environment**: local | CI | staging | pipeline
**Data needs**: fixtures, seed volume, masking, isolation
**Teardown / reset**: reset hook, fixture cleanup, rollback, or N/A + reason
**Depends on**: TC-NNN or `—`

**Ownership and handoff**

**Automation intent**: Auto=Y/N + reason; target suite; required selectors/API contracts/data
**External QA handoff needs**: env, selectors, seed/reset, evidence, account roles, or N/A
**Owner of execution context**: QA team at staging | Dev team in CI | external QC

**Given**:
- System state: <!-- VD: Không có user nào với email này trong database -->
- Setup:
  ```json
  {
    "existing_user": null,
    "preconditions": "Clean state — no prior registration with this email"
  }
  ```

**When**:
- <!-- VD: POST /api/v1/auth/register với body hợp lệ -->

**Then**:
- [ ] <!-- VD: Response status 201 Created -->
- [ ] <!-- VD: Response body chứa { "id": "<uuid>", "email": "...", "status": "PENDING_VERIFICATION" } -->
- [ ] <!-- VD: Verification email được gửi đến email đã đăng ký -->
- [ ] <!-- VD: User record tồn tại trong DB với status = PENDING_VERIFICATION -->

**Test Data**:

```json
{
  "setup": { "description": "Mô tả trạng thái khởi đầu cụ thể" },
  "input": {
    "full_name": "Nguyen Van A",
    "email": "test-register@prism.dev",
    "password": "TestPass123!"
  },
  "expected_output": {
    "status": 201,
    "body": {
      "id": "<uuid — any valid UUID>",
      "email": "test-register@prism.dev",
      "status": "PENDING_VERIFICATION"
    }
  }
}
```

---

<!-- Repeat the block above for every functional test case. Each TC has unique TC-NNN. -->
<!-- Mỗi Must Have FR có ít nhất 2 TC: happy path + error path (TEST-2). -->
<!-- Error path TC example structure: same metadata + Given (conflict/invalid state) + When (invalid action) + Then (4xx response, no side effect, error message text). -->

---

## 6. SIT / Integration Test Cases

<!-- For cross-module / cross-service / external dependency flow coverage. Do not duplicate
     simple functional cases here; link to the functional TC where relevant. -->

<!-- ID: TC-NNN -->
<!-- VERIFIES: US-NNN -->
### TC-NNN: [US-NNN][AC-NNN][SIT] {{INTEGRATION_FLOW_TITLE}} `[planned-automated]` `P0`

**Classification and trace**

**Area**: SIT
**Traceability**: FR-NNN / NFR-NNN / US-NNN
**Flow refs**: `/docs/architecture/sequence.md §SEQ-NNN`, `/docs/architecture/api-specs.md §API-NNN`, `/docs/architecture/events.md §EVT-NNN`
**Systems involved**: Upstream, downstream, queue/topic, webhook provider, DB, cache

**Execution profile**

**Test Level**: `integration` | `e2e`
**Test Type**: `SIT`
**Export target**: `sit`
**Manual / Auto boundary**: `automated` | `manual`
**Smoke**: `Y` | `N`

**Environment and data**

**Environment**: local integration env | CI | staging | UAT
**Data needs**: seed source, account role, entity IDs, fixture, synthetic data constraints
**Teardown / reset**: rollback / compensation / reset path
**Depends on**: TC-NNN or `—`

**Integration expectations**

**System A expected**: expected result for caller / gateway / upstream / UI
**System B expected**: expected result for receiver / downstream / core integration
**Screen under test**: UI/screen name, or N/A + reason

**Ownership and handoff**

**Automation intent**: candidate suite, API contracts, event capture, logs, timing assumptions
**External QA handoff needs**: external QC env/data/evidence needs, or N/A
**Owner of execution context**: Dev / QA / external QC and target env

**Given**:
- <!-- Integration preconditions, dependency availability, queue/topic state, idempotency key, auth role -->

**When**:
- <!-- Trigger the cross-system flow -->

**Then**:
- [ ] Upstream response matches expected status/body/error envelope
- [ ] Downstream system receives/updates expected state
- [ ] Retry/idempotency behavior matches `/docs/architecture/sequence.md` §SEQ-NNN
- [ ] Rollback/compensation leaves each entity in the expected final state
- [ ] Async event/webhook/queue message is produced or consumed with expected schema
- [ ] No duplicate side effect on repeat request / retry

### SIT Coverage Checklist

| Flow | Happy Path | Contract / Schema | Failure / Timeout | Retry / Idempotency | Rollback / Compensation | Async / Event | Consistency | Notes |
|---|---|---|---|---|---|---|---|---|
| | TC-NNN | TC-NNN | TC-NNN | TC-NNN | TC-NNN | TC-NNN | TC-NNN | |

---

## 7. Non-Functional Test Cases

<!-- Every NFR TC must include the mandatory metadata fields from §1. -->
<!-- Use `**Area**: PERF | SEC | A11Y | LOAD | …` to indicate the NFR family. -->

### 7.1 Performance Tests

<!-- ID: TC-NNN -->
<!-- VERIFIES: NFR-NNN -->
### TC-NNN: [NFR-NNN][Performance] API Response Time Under Load `[planned-automated]` `P0`

**Classification and trace**

**Area**: PERF
**Traceability**: NFR-NNN

**Execution profile**

**Manual / Auto boundary**: `automated`
**Test Level**: `integration` | `e2e`
**Test Type**: `Performance`
**Export target**: `functional`
**Smoke**: `N`

**Environment and ownership**

**Environment**: staging | performance env | pipeline
**Data needs**: dataset size and shape only; no generated dataset file in Phase Test
**Teardown / reset**: seed refresh / cleanup / N/A + reason
**Depends on**: TC-NNN or `—`
**Automation intent**: Auto=Y; performance suite owner; tool from Architecture/context
**External QA handoff needs**: external performance execution needs, or N/A
**Owner of execution context**: Dev / QA / Performance team
**Tool**: k6 | Gatling | Architecture-approved tool, or TBD risk

**Test Environment**:
- Environment: <!-- VD: Staging — cùng infrastructure class với Production -->
- VM/instance size: <!-- VD: 2 vCPU, 4GB RAM — ghi rõ nếu staging nhỏ hơn prod -->
- Database: <!-- VD: Staging DB với {{PERF_DATA_SIZE}} records được seed sẵn -->

**Given**:
- {{PERF_DATA_SIZE}} records trong database (realistic data size)
- Warm-up: 2 phút warm-up traffic trước khi đo (để JIT và connection pool ổn định)

**When** (Ramp-up strategy):
- 0 → {{CONCURRENT_USERS}} users trong 2 phút (ramp-up)
- Giữ {{CONCURRENT_USERS}} users trong 5 phút (sustained load)
- Ramp-down 2 phút
- Target endpoints: <!-- VD: GET /api/v1/orders, POST /api/v1/checkout -->

**Then**:
- [ ] p50 latency < {{P50_TARGET}}ms
- [ ] p95 latency < {{P95_TARGET}}ms
- [ ] p99 latency < {{P99_TARGET}}ms
- [ ] Error rate < 0.1% trong sustained phase
- [ ] Throughput ≥ {{MIN_RPS}} RPS trong sustained phase
- [ ] Memory RSS stable (không tăng liên tục — không có memory leak)
- [ ] CPU usage < 80% trên application servers

### 7.2 Security Tests

<!-- Repeat the mandatory metadata block under every TC. Security execution must be scoped and authorized. -->
<!-- Common security TCs to cover: SQL Injection (NFR-NNN), XSS, Broken Access Control (IDOR),
     JWT integrity, CSRF, Rate Limiting. Each gets its own TC-NNN block with `**Area**: SEC`. -->

<!-- ID: TC-NNN -->
<!-- VERIFIES: NFR-NNN -->
### TC-NNN: [NFR-NNN][Security] SQL Injection Prevention `[planned-automated]` `P0`

**Classification and trace**

**Area**: SEC
**Traceability**: NFR-NNN

**Execution profile**

**Manual / Auto boundary**: `automated`
**Test Level**: `component` | `integration`
**Test Type**: `Security`
**Export target**: `functional`
**Smoke**: `N`

**Environment and ownership**

**Environment**: authorized non-production env | CI security check
**Data needs**: safe payload set and synthetic account/data only
**Teardown / reset**: cleanup side effects / verify no side effects / N/A + reason
**Depends on**: TC-NNN or `—`
**Automation intent**: Auto=Y; target security/API suite; safe payload scope; run environment
**External QA handoff needs**: external security/QC needs, or N/A
**Owner of execution context**: Dev / Security / external QC

**Given**:
- Standard API endpoints accepting user input (search, filter, login)

**When**:
- Input fields receive SQL injection payloads:
  - `'; DROP TABLE users; --`
  - `' OR '1'='1`
  - `1; EXEC xp_cmdshell('cmd')`
  - `' UNION SELECT * FROM users --`

**Then**:
- [ ] Tất cả payloads bị reject hoặc safely parameterized
- [ ] Không có database error nào exposed trong response
- [ ] Response trả về 400 Bad Request
- [ ] Không có side effect trong database

<!-- Repeat similar blocks (anchored TC-NNN, **Area**: SEC) for XSS Prevention, Broken Access Control (IDOR), JWT Security, CSRF Prevention, Rate Limiting. -->

### 7.3 Accessibility Tests

<!-- Manual assistive-tech checks can be Auto=N with explicit reason. -->

<!-- ID: TC-NNN -->
<!-- VERIFIES: NFR-NNN -->
### TC-NNN: [NFR-NNN][Accessibility] Keyboard Navigation `[planned-manual]` `P1`

**Classification and trace**

**Area**: A11Y
**Traceability**: NFR-NNN

**Execution profile**

**Manual / Auto boundary**: `manual`
**Test Level**: `e2e`
**Test Type**: `Accessibility`
**Export target**: `functional`
**Smoke**: `N`

**Environment and ownership**

**Environment**: browser/device/screen-reader matrix
**Data needs**: page state, account role, seeded content for target screens
**Teardown / reset**: N/A + reason unless state changes
**Depends on**: TC-NNN or `—`
**Automation intent**: Auto=N + reason, or Auto=Y for partial scan with required tooling
**External QA handoff needs**: external a11y QC needs, or N/A
**Owner of execution context**: QA / Accessibility specialist / external QC

**Given**:
- Application loaded in browser, mouse disconnected

**When**:
- Navigate through all interactive elements using Tab/Shift+Tab
- Activate elements using Enter/Space
- Test modal dialogs: open, navigate inside, close

**Then**:
- [ ] Tất cả interactive elements reachable via keyboard
- [ ] Tab order theo visual layout (trái-phải, trên-xuống)
- [ ] Focus indicator visible rõ ràng trên mọi element
- [ ] Không có keyboard trap (có thể ESC hoặc Tab ra khỏi mọi component)
- [ ] Modal: focus trapped bên trong khi open, trả về trigger element khi close

<!-- Repeat blocks (anchored TC-NNN, **Area**: A11Y) for Screen Reader Compatibility, Color Contrast & Visual, Focus management, etc. -->

---

## 8. Test Case Summary

| Area | Total Cases | Auto Candidates | Manual | Component | Integration | E2E | P0 | P1 | P2 |
|------|------------|-----------------|--------|-----------|-------------|-----|----|----|----|
| AUTH | | | | | | | | | |
| ORDER | | | | | | | | | |
| PAYMENT | | | | | | | | | |
| SIT / Integration | | | | | | | | | |
| PERF | | | | | | | | | |
| SEC | | | | | | | | | |
| A11Y | | | | | | | | | |
| **Total** | | | | | | | | | |

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `TEST-1`, `TEST-2`, `TEST-3`, `TEST-3b`, `TEST-4`, `TEST-5`, `TEST-6`, `TEST-7`, `TEST-8`
- [ ] Every Must Have feature (FR-NNN P0) has at least 2 test cases (happy + error path)
- [ ] Rule / Branch Inventory (§3) is authored as the singleton anchored block `<!-- ID: TEST-COVERAGE-001 -->` (so it merges into `/docs/testing/test-cases.md`), maps every in-scope AC / BR / rule / branch to TC IDs or `N/A + reason`, and — in later sprints — carries forward all prior rows (full cumulative table, `## Updated`)
- [ ] **Per-AC Technique Decision Matrix (§3.5) is filled for every in-scope AC**: every cell is Y (with AC clause cited) or N (with concrete reason); every Y row lists ≥1 TC with the matching technique tag in its title prefix; US-level `N/A + reason` rows are allowed when no AC IDs exist (per `core/standards/testing-standards.md §1.5`)
- [ ] Coverage Category Checklist marks applicable functional and SIT categories as covered or explicitly N/A
- [ ] Every test case has Area, Traceability (FR-NNN or NFR-NNN), plus Design states / API refs khi liên quan
- [ ] Every TC starts with `<!-- ID: TC-NNN -->` anchor line; `<!-- VERIFIES: ID-NNN -->` trace tag where applicable
- [ ] All TC IDs use strict format `TC-\d{3,}` (flat, no area in ID) — atomic issuance via `python .prism/core/tools/get_next_id.py --type TC`
- [ ] Test cases are detailed enough for planning and later implementation without asking QA
- [ ] Given/When/Then format used consistently with concrete pre-conditions and exact expected result
- [ ] Mỗi Must Have FR có ít nhất 1 TC đáp ứng `TEST-2` Execution-Ready + Implementation-Consumable Handoff: stable TC-NNN ID, manual/auto boundary, environment, data needs, teardown/reset khi state-changing, owner of execution context, traceability đầy đủ, và đủ behavioral detail để Dev viết repo test delta tương ứng mà không phải hỏi lại QA
- [ ] Phase Test KHÔNG ghi repo test delta, generated runtime data packs, or external QC automation code — chỉ owns test intent và generated TSV companions từ markdown
- [ ] Test data requirements provided for automated candidates and state-changing manual cases
- [ ] Automation candidates include target test level, data/contracts, and intended run environment
- [ ] External QA handoff needs are stated when testers / automation live outside the product repo
- [ ] Generated TSV companions have been exported from this Markdown and are not hand-edited
- [ ] Priority levels assigned and consistent with risk assessment in test plan
- [ ] Planned automated vs planned manual clearly tagged
- [ ] Security tests cover OWASP Top 10 relevant items
- [ ] Performance test thresholds match NFR targets in `/docs/architecture/nfr.md`
- [ ] Accessibility tests cover WCAG 2.1 AA requirements
- [ ] UI-affecting Must Have FRs có ít nhất 1 manual-observation TC khi `quality_profile.manual_observation_required_for_ui: true`
- [ ] Summary table counts are accurate
