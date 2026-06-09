# Phase Engine: Test

## Trigger

`start test` — requires: product + design + architecture ALL APPROVED.

In a newer sprint, `start test` and `approve test` also require all previous sprints to already be sealed. If any earlier sprint is still unsealed, Test stays blocked in this sprint until that earlier sprint closes with `approve implement`.

**Test is an independent lane.** It can run standalone for QA/test-design work, and its approved outputs can satisfy the reviewed test-case coverage that planning needs before implementation moves forward.

## Behavior

1. Read the approved Product package, Design, Architecture documents, and `/docs/architecture/project-reference.md`. Use `/docs/architecture/project-reference.md` to identify public entrypoints, module / package boundaries, dependency rules, and stable code surfaces that must influence risk coverage and test scope.

2. **Đọc test framework đã quyết ở Architecture (Tech Stack table — rows `Test (Unit) / (Integration) / (E2E) / (Contract) / Mocking`).** Phase Test KHÔNG quyết định framework, chỉ consume. Nếu Architecture chưa khai báo framework cho 1 layer → block, yêu cầu update Architecture trước khi continue.

3. Load the Test-specific standards through `core/standards/INDEX.md` (resolved via `prism.json` like other standards). Use `testing-standards.md` for coverage dimensions, defect taxonomy, exploratory checks, and authorized security / accessibility / performance test guidance. Do not load external testing rules from imported tools or web sources as source of truth.

4. **Ask about test strategy — with probes and defaults for vague answers** (KHÔNG hỏi framework — đã có ở Architecture):
   - Coverage targets per layer (repo unit / component / integration / e2e / contract)?
   - Risk-based prioritization: feature/flow nào có risk cao nhất, cần coverage sâu?
   - Planned execution environment: local, CI, staging, pipeline? *(Probe for who owns each environment and what data is available there.)*
   - Performance benchmarks: response time targets, load thresholds? *(Probe: p50 / p95 / p99, concurrent users, sustained duration, acceptable error rate, target dataset volume.)*
   - Security testing requirements: OWASP, penetration testing scope? *(Probe: auth flows, IDOR, CSRF, rate limiting, secret handling, external pentest yes/no.)*
   - Test data strategy: fixtures, factories, seeding? *(Probe: PII masking, isolation model, shared vs ephemeral DB, data volume for perf tests.)*
   - Manual vs automated boundary: what requires human verification? *(Probe: visual QA, accessibility with screen reader, exploratory UX paths, device/browser matrix.)*
   - External QA / tester workflow: will QC execute outside the product repo or in a separate automation repo? *(Probe for handoff needs: environment URL, stable selectors / `data-testid`, seed/reset hooks, test accounts as secret references, evidence expectations.)*

   **Vague answer handling**: Re-ask with a concrete example or offer a reasonable default. Accept `skip` / `not sure` gracefully — record as `TBD` with a risk note. Do not block unless the missing answer makes a release-critical test plan impossible to define.

   **Cross-validation before writing**: If NFR / architecture requires something stronger than the stated test strategy (e.g., strict performance target but no perf environment, security-sensitive auth flow but no security scope) → flag the contradiction and ask before writing.

5. **HLTC-style branch discovery before detailed test cases**: For complex features (many business rules, branching logic, rule precedence, AI / rule-engine fallback, high-risk SIT flow), first build a short high-level branch outline from AC / BR / User Stories / API / sequence docs. Use it to detect missing branches, unclear precedence, contradictory rules, missing negative paths, and high-risk integration paths. If gaps affect correctness, ask or propose them back to the user before generating detailed TC. This is an AI discovery/probe step, not a mandatory BA/QA/Dev review gate.

6. **Rule inventory and branch coverage (`TEST-3`)**: If upstream artifacts contain AC IDs, BR IDs, rule IDs, decision tables, states, or named flow branches, the testing proposal MUST include a Rule / Branch Inventory, authored as the singleton anchored block `<!-- ID: TEST-COVERAGE-001 -->` (per `core/templates/test-cases-template.md §3`) so it is promoted into `/docs/testing/test-cases.md` at sprint seal — `## New` in sprint 1, `## Updated` (full cumulative table) later. Every in-scope item maps to concrete `TC-xxx` IDs or `N/A + reason`. Unmapped in-scope rules block `approve test`.

6.5. **Per-AC ISTQB Technique Decision Matrix (`TEST-3b`)**: Before authoring TC blocks, fill the Per-AC Technique Decision Matrix in `core/templates/test-cases-template.md §3.5` for every in-scope AC. Workflow:

   1. **Decide Y/N per cell** — for each `AC × {BVA, EP, DT, ST, DD}` cell, consult `core/standards/testing-standards.md §1.5` (each technique entry has Trigger, Emit pattern, Example, Exclusion):
      - `Y` cell — quote the AC clause that triggers the technique. Example: `Y — "cache TTL = 300s" defines a numeric boundary`.
      - `N` cell — give a concrete one-line reason tied to the AC. Example: `N — input is a single role enum with no edge`. Avoid generic phrases like "không cần thiết" / "not applicable" — a future validator will flag those as insufficient.
      - `US-level N/A` row — when a US has no AC IDs at all, or all five techniques clearly do not apply to the whole US, write one row with `AC ID = US-NNN (whole)` and a one-line reason; remaining cells may stay empty.

   2. **Emit TCs from every Y cell** — for each `Y`, produce ≥1 TC whose title prefix carries the matching trace + Technique tag. Canonical PRISM form is `[US-NNN][AC-NNN][Technique]`; imported aliases such as `[US-10.1][AC1][Technique]` are accepted when upstream product sources own those labels. A single TC may satisfy multiple `Y` cells when its title combines tags with `+` (e.g. `[US-010][AC-001][BVA+Negative]` satisfies both the BVA row and the Negative-path coverage on that AC).

   3. **Populate the `TC IDs generated` column** — list each TC ID that satisfies the row's Y cells, with the technique tag in parentheses for cross-check (e.g. `TC-001 (BVA), TC-002 (ST)`). A TC covering multiple ACs appears in the TC IDs column of each AC row it covers. A TC using multiple techniques on one AC is listed once on that AC row but counted under every Y column whose technique it carries (via the `+`-combined title tag).

   4. **Non-technique edge cases remain required** — edge cases that do NOT map cleanly to BVA / EP / DT / ST / DD belong to `Corner / Error Guessing` in §4 Coverage Category Checklist, NOT in this matrix. Examples: dependency outage (search backend unavailable, queue partition), object-storage 404 on a previously-valid object, race conditions, mid-transaction client disconnect, container OOM kill. Important disambiguation: a numeric boundary (signed-URL TTL = 10min, file size = 10MB) is **BVA**, not Corner; a state transition crossing a permission change is **ST** (combine with `+Security` if relevant), not Corner. See `core/standards/testing-standards.md §1.5` → *Non-technique edge cases remain required* for the full disambiguation list. The matrix is necessary but not sufficient — Corner / Error Guessing TCs must still be authored.

   **Current policy (2.0.0)**: missing or malformed trace + Technique title prefixes raise validator warnings with explicit `Recommended fix: …` messages; they do not yet block `approve test`. **Planned (a future minor release, not scheduled)**: empty matrix cells, generic `N` reasons, and missing title prefixes will hard-block `approve test`. Generators SHOULD treat the full matrix discipline as a quality gate now to avoid future churn.

7. **Functional and SIT coverage model (`TEST-4`)**:
   - Functional coverage includes AC positive/negative, BR/rule coverage, basic flow, the five ISTQB techniques (BVA / EP / Decision Table / State Transition / Data-Driven — applied per AC via step 6.5 matrix), corner/error guessing, impact/regression, and relevant NFR coverage.
   - SIT coverage includes API contract/schema, cross-service flow, retry/idempotency, rollback or compensation, async event / webhook / queue paths, and cross-system consistency.
   - Not every feature needs every category; any omitted category needs `N/A + reason`, not silence.

8. **Test data requirements (`TEST-5`)**: Test artifacts specify data needs, not generated runtime data files. Each executable TC declares concrete data requirements, including fixtures/seed source, golden dataset or mutation strategy when relevant, BVA/EP values, PII-safe constraints, isolation model, and teardown/reset expectation. Do not write `testing-output/`, TSV datasets, SQL teardown, or secrets during Phase Test.

9. **Automation intent, not runnable automation code (`TEST-6`)**: Test artifacts may mark automation candidates (`Auto=Y/N`), suggested QA test level (`component`, `integration`, `e2e`), mapping from TC to future script/suite, required data, required selectors/API contracts, and intended run environment. `component` should reuse a framework already chosen in Architecture or explicitly available in project context; Phase Test must not invent a new tool. Phase Test does not generate Robot/Playwright/Pytest code and does not replace repo test delta. Architecture can support automation skeletons, but runnable QC automation requires implementation/runtime surfaces or explicit user-provided equivalents.

10. **External QA handoff contract (`TEST-7`)**: When testers execute outside the product repo or in a separate QC automation repo, include a lightweight External QA Handoff section in the Test artifacts. It should list TC IDs, priority, manual/automation candidate, data/teardown needs, target environment type, API/design/sequence refs, expected evidence, and testability needs from Dev (stable selectors / `data-testid`, seed/reset hooks, test account roles as secret references, feature flags). This remains a handoff contract, not execution output.

11. **Generated TSV export contract (`TEST-8`)**: During the active sprint, `docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md` is the canonical Test case source. At sprint seal, its `TC-NNN` anchors merge into `/docs/testing/test-cases.md` Living Truth. The engine MUST generate deterministic TSV companions from the active testing proposal after writing or materially changing Test artifacts. The generated files live under `/docs/sprint-v{X}/testing/generated/`: `test-cases-functional-v{X}.tsv`, `test-cases-sit-v{X}.tsv`, and `test-cases-export-manifest-v{X}.json`. They are generated views for QC import/handoff only, not separate editable source. If markdown and TSV differ, markdown wins and the TSV must be regenerated. The default export command is `python .prism/core/tools/export_test_cases.py --test-cases docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md --output-dir docs/sprint-v{X}/testing/generated`. The functional TSV header has 17 columns: 15 IEEE 29119/ISTQB-compatible (STT, Summary, Test Level, Precondition, Test Data, Step summary, Expected result, Priority, Story Linkages, Test Type, Smoke, Auto, Phụ thuộc TC, Teardown, Trace) plus 2 PRISM-unique (`Design Refs` from `**Design states referenced**`, `API Refs` from `**API / NFR refs**`). Optional `--per-us` flag emits one TSV per User Story under `<output-dir>/per-us/` (cases tracing to multiple US IDs appear in each group; cases without US trace go into `test-cases-functional-no-us-v{X}.tsv`). The combined file is always emitted; the per-US split is additive and opt-in.

12. **Assumption blocks**: For any test decision not confirmed by upstream artifacts (e.g., seed size, browser matrix, manual boundary, masking approach, external QC environment, selector availability), insert an inline assumption block or explicit open risk. Do not make silent testing assumptions.

13. **Phase Test ownership boundary**: Phase Test owns the `qa test intent` only — `test-plan-v{X}.md` and `proposals/test-cases-v{X}.md` (`TC-NNN` items), plus deterministic generated TSV companions under `testing/generated/`. It does NOT own `repo test delta` (in-repo unit / integration / contract / component tests written by Dev / AI), generated runtime data packs, or external QC automation repositories. Repo test delta is planned in Plan via `repo_test_delta_target`, executed in Implement, and audited by `validate implementation --mode spec`. Test must not duplicate or replace repo test definitions.

14. **Execution-ready and implementation-consumable handoff rule (`TEST-2`, hard rule)**: Every Must Have FR MUST have at least one test case that is executable without re-asking QA and detailed enough for Dev to author the corresponding repo test delta without asking QA for clarification. That means each TC has:
   - stable `TC-xxx` ID
   - explicit `manual` / `auto` boundary
   - environment (local / CI / staging / pipeline) and data needs (fixtures, seed volume, masking, isolation)
   - owner of the execution context (who runs it where)
   - Given / When / Then with concrete pre-conditions and exact expected result (no "verify it works" handwaving)
   - traceability to `FR-xxx`, the relevant Design states, and the relevant API / NFR identifiers
   - teardown/reset expectation when the TC creates, updates, deletes, locks, or mutates state
   - automation intent and external-QA handoff needs when the TC is marked as a candidate for external QC automation

   A TC also violates `TEST-2` if it describes only the QA-side observation (e.g., "navigate to dashboard and check banner appears") without enough behavioral detail for Dev to write a corresponding repo test. Missing any of these on a Must Have FR's TC blocks `approve test`.

15. **Design State Coverage Traceability Index** (bắt buộc): test plan phải map mỗi state đã định nghĩa trong design (Empty / Loading / Populated / Error / etc.) với ít nhất 1 test case (manual hoặc automated). State không có TC → block `approve test`.

16. **Coverage Traceability Index is mandatory (`TEST-1`)**: `test-plan-v{X}.md` MUST contain a Coverage Traceability Index linking Must Have FRs, prioritized NFRs, relevant US refs, Design refs, API refs, and project / boundary refs to concrete `TC-xxx` IDs (or an explicit uncovered gap with rationale). `proposals/test-cases-v{X}.md` then owns the case-level details behind those IDs until sprint seal promotes them into `/docs/testing/test-cases.md`.

17. **Manual UI observation rule**: mỗi UI task slice trong runtime validate (xem `phase-implement.md` `validate implementation --mode spec`) phải:
    1. Screenshot mỗi state đã design (theo Design State Coverage Traceability Index ở step 15).
    2. Visual-compare screenshot vs mockup `docs/design/design-system.md` (Living Truth) + active sprint's `design/proposals/design-system-v{X}.md`.
    3. Note discrepancy ≥ 5% pixel diff hoặc layout shift đáng kể như blocker.

    Tool đề xuất (optional, không bắt buộc): Percy / Chromatic / BackstopJS / Storybook visual test cho web; Maestro / iOS XCUITest snapshot cho mobile.

18. **Output comprehensive test artifacts** covering all requirement traceability, run the TSV exporter, then run the shared self-check in `core/phase-quality-standards.md` before presenting them.

## Input Context

- Required: **Effective Truth** for product + design + architecture (per `core/version-manager.md § Effective Truth`). Compose via `python .prism/core/tools/effective_truth.py --phase all --up-to-sprint v{X}`. The composed views contain the Living Truth tree merged in memory with active sprint's APPROVED proposals + change-pack deltas. Any earlier unsealed sprints must be sealed before `start test` (per `core/sprint-manager.md § Plan Gate`).
- Required: architecture effective truth entries for project reference, API specs, NFRs, sequence, ERD, data-flow, events, and ADRs as relevant to the test scope
- Required standards: `testing-standards.md` resolved via `core/standards/INDEX.md`
- Optional: `/docs/architecture/sequence.md`, `/docs/architecture/erd.md`, `/docs/architecture/data-flow.md`, `/docs/architecture/events.md`, `implementation-plan-v{X}.md`
- Prohibited inputs: sealed sprints' files, other sprints' DRAFT proposals, snapshots folder (audit-only)

Test has two artifact types (per `core/version-manager.md § Folder Structure Per Sprint`): `test-plan-v{X}.md` is sprint-only work process; `proposals/test-cases-v{X}.md` is the mergeable Test proposal whose `TC-NNN` items route into `/docs/testing/test-cases.md` at sprint seal. The test code itself (in the repo) IS a deliverable but lives in code, not in docs.

## Output (canonical docs + generated companions)

Written to `/docs/sprint-v{X}/testing/`:

| File | Content |
|------|---------|
| `test-plan-v{X}.md` | Strategy, scope, risk coverage, planned execution model, environments, external QA handoff summary |
| `proposals/test-cases-v{X}.md` | Anchored `TC-NNN` items with `<!-- VERIFIES: ID-NNN -->` + the singleton `TEST-COVERAGE-001` Rule / Branch Inventory block — both route to `/docs/testing/test-cases.md` at sprint seal. Detailed cases, functional/SIT coverage, data requirements, automation intent, traceability. |
| `generated/test-cases-functional-v{X}.tsv` | Generated Functional / Regression / NFR TSV companion derived from `proposals/test-cases-v{X}.md` |
| `generated/test-cases-sit-v{X}.tsv` | Generated SIT TSV companion derived from `proposals/test-cases-v{X}.md` |
| `generated/test-cases-export-manifest-v{X}.json` | Stable export manifest with source hash and generated file paths |

Only `test-plan-v{X}.md` and `proposals/test-cases-v{X}.md` are canonical active sprint Test artifacts. Generated TSV companions are deterministic export views and must not be manually edited. AI MUST NEVER write `/docs/testing/test-cases.md` directly.

The mergeable test proposal must additionally pass `python .prism/core/tools/validate_proposal.py --file docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md`.

Test artifacts must satisfy `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `TEST-1`, `TEST-2`, `TEST-3`, `TEST-3b`, `TEST-4`, `TEST-5`, `TEST-6`, `TEST-7`, and `TEST-8`.

## QA / Dev Boundary

| QA Writes | Dev References During Planning |
|-----------|-----------------------------|
| Test plan | Independent QA strategy and validation constraints |
| Test proposal (`TC-NNN` case specs) | Reusable test intent for planning and later implementation |
| Acceptance criteria | Pass/fail definition per feature |
| Test data requirements | Fixtures / seeding approach |
| Automation intent / external QA handoff | Optional input for Plan and separate QC automation repo |
| Manual test scenarios | _(QA executes manually)_ |

Test cases must be detailed enough for planning and later implementation **without asking QA for clarification**.

## Gate

QA Lead checks → `validate test` → `approve test` or `feedback: [...]`

`approve test` does not block `start implement`. Dev can begin coding as soon as the plan is approved.

`approve test` is required before `approve implement`. An implementation pass cannot be closed until test is APPROVED. This enforces convergence — test and implement run in parallel, but both must be approved to close the sprint.

`approve test` is blocked if any of the following are true:

- any previous sprint is not yet sealed
- the Coverage Traceability Index violates `TEST-1`: missing a Must Have FR or a prioritized NFR, and no explicit accepted gap is recorded
- a Must Have FR's TC violates `TEST-2` — missing `manual` / `auto` boundary, environment, data needs, teardown/reset for state changes, owner, exact expected result, or traceability
- a Rule / Branch Inventory violates `TEST-3` — in-scope AC / BR / rule / branch has no TC mapping and no `N/A + reason`
- Functional or SIT coverage violates `TEST-4` — relevant coverage categories are omitted without rationale
- test data requirements violate `TEST-5` — state-changing TC lacks data source, isolation, or teardown/reset expectation
- automation intent violates `TEST-6` — `Auto=Y` cases lack target test level, required data/contracts, or run environment
- external-QA handoff violates `TEST-7` — external QC execution is expected but required handoff/testability needs are missing
- generated TSV exports violate `TEST-8` — required generated files are missing, stale against the manifest/source hash, manually edited, or not derivable from `docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md`
- `python .prism/core/tools/validate_proposal.py --file docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md` returns any blocker, including missing / malformed anchors, duplicate IDs, wrong split-target prefixes, malformed frontmatter, unknown top-level merge sections, or unmergeable H2 structure inside an anchored block
- a TC violates `TEST-2` — too vague for Dev to author a corresponding repo test delta
- the active `validate test` file is missing, stale, or its latest explicit result still contains `blocker`-level findings (see `core/orchestrator.md § Validate Active Files`)
- a selected or otherwise in-scope DRAFT change pack impacts Test and Test has not absorbed that change through:
  - `feedback:` if Test is `DRAFT`, or
  - a Test delta if Test is already `APPROVED`

## Validate Test Command

`validate test` is a user-invoked audit command. It runs read-only against the current Test DRAFT and approved upstream artifacts, checks the generated TSV export freshness, produces a structured `blocker` / `warn` / `info` report, and writes or updates the active validate file for this command (named per `core/orchestrator.md § Validate Active Files`). It must be run on the current DRAFT before `approve test` and re-run after any `feedback:` or change-pack absorption that materially changes the test package.

During normal Test generation, the engine must already self-apply the same coverage-readiness logic before outputting the draft, then run the TSV exporter. The user should not need to run export scripts manually.

`approve test` requires that active validate file to already be present and clean, then re-runs `validate test` in console-only mode as a final full confirmation pass. If that approval-time run finds any blocker or material gap, do not approve; show the findings to the user first and ask whether they want to update the active validate file into a follow-up checklist.

### Scope

Validate Test checks:

- **Proposal structure check**: run `python .prism/core/tools/validate_proposal.py --file docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md`. Any blocker (malformed anchors, duplicate IDs, missing required frontmatter keys, missing routing tags, unknown top-level merge sections, unmergeable H2s inside anchored blocks, or wrong split-target prefix) blocks `approve test`; Updated/Removed target existence is confirmed by `seal_sprint.py` against routed LT files.
- `DOC-3`: required sections / fields from `core/templates/test-plan-template.md`, `core/templates/proposal-template.md`, and `core/templates/test-cases-template.md` are present in the plan/proposal or explicitly marked N/A with reason.
- `VAL-1`: the active validate file records structural coverage and rule coverage for `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `TEST-1`, `TEST-2`, `TEST-3`, `TEST-3b`, `TEST-4`, `TEST-5`, `TEST-6`, `TEST-7`, and `TEST-8`.
- Upstream fit: Product, Design, Architecture, `/docs/architecture/project-reference.md`, API specs, and NFR references are approved, loaded, and reflected in risk coverage.
- `TEST-1`: every Must Have FR and prioritized NFR maps to relevant US, Design / API refs, project / boundary refs, concrete `TC-xxx` IDs, manual / auto mix, and coverage status or an explicit accepted gap.
- `TEST-2`: each Must Have FR has at least one test case with stable ID, manual / auto boundary, environment, data needs, teardown/reset for state changes, owner, Given / When / Then, exact expected result, traceability, and enough behavioral detail for Dev to author the corresponding repo test delta without re-asking QA.
- `TEST-3`: every in-scope AC / BR / rule / branch maps to TC IDs or `N/A + reason`.
- `TEST-3b`: Per-AC Technique Decision Matrix (`core/templates/test-cases-template.md §3.5`) is filled for every in-scope AC (each `AC × {BVA, EP, DT, ST, DD}` cell is Y with cited clause or N with concrete reason); every Y produces ≥1 TC carrying the matching trace + Technique title prefix (`[US-NNN][AC-NNN][Technique]`, multi-tag via `+`; imported aliases such as `[US-10.1][AC1][BVA]` are accepted during normalization). **Current release: emitted as `warn` only** — does not block `approve test`. **Planned**: will be promoted to `blocker` in a future minor release. See `core/standards/testing-standards.md §1.5` for technique trigger/exclusion rules.
- `TEST-4`: applicable functional and SIT coverage categories are present or explicitly marked N/A with rationale.
- `TEST-5`: executable test cases define concrete data, PII-safe constraints when relevant, isolation, and teardown/reset expectations.
- `TEST-6`: automation candidates define test level, data/contracts, and run environment without generating runnable automation code in Phase Test.
- `TEST-7`: external QA handoff is present when testers / automation live outside the product repo.
- `TEST-8`: generated Functional/SIT TSV companions and export manifest exist under `testing/generated/` and match the current testing proposal. Validate by running `python .prism/core/tools/export_test_cases.py --test-cases docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md --output-dir docs/sprint-v{X}/testing/generated --check`.
- QA / Dev boundary: Test owns QA test intent and does not replace `repo_test_delta_target`, in-repo test definitions, generated runtime data packs, or external QC automation repositories.
- Open Issues: every `## Open Issues` row is closed before approval.

A `blocker` finding in any area above blocks `approve test`.

### Expected Output

```text
validate test: test-plan-v{X}.md + proposals/test-cases-v{X}.md + generated TSV exports
blocker: 1
warn: 1
info: 0

Coverage Map:
| Requirement / Rule ID | Source | Covered TC IDs | Status | Gap |
|---|---|---|---|---|

Gap Analysis:
| Rule ID | Missing Group | Gap | Suggested TC | Priority | Clarifying Question |
|---|---|---|---|---|---|

Supplemental TC Suggestions:
| Suggested TC ID | Summary | Test Level | Data | Expected Result | Trace | Note |
|---|---|---|---|---|---|---|

Findings:
- blocker [TEST-1]: FR-022 appears in Product but has no TC ID and no accepted gap in the Coverage Traceability Index.
- warn [TEST-2]: TC-004 has expected result text but no explicit test data owner (Area: payments).

→ Fix blockers with `feedback test: ...`
→ Then `validate test`
→ Then `approve test`
```

The active validate file is named and lifecycled per `core/orchestrator.md § Validate Active Files` (cycle-scoped: `validate-test-<cycle>.md` in `tempo/in-progress/` while running, sealed and moved to `tempo/completed/` on approval success).

## Same-Sprint Change Handling

- If Test has not started, future `start test` reads effective truth.
- If Test is `DRAFT`, merge impacted changes via `feedback:`.
- If Test is `APPROVED`, same-sprint changes use a Test delta in the selected change pack.

## Quality Standard

Test like a **fintech QA Lead** — risk-based prioritization, traceability to every requirement, clear pass/fail criteria, no ambiguous test steps.
