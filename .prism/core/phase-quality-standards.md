# Phase Quality Standards

Single source of truth for the detailed PRISM quality bar used by `import [phase]`, every output-producing flow (`start`, `resume`, `continue`, `feedback:`, `start change:`), and the user-invoked validate commands (`validate user story`, `validate design`, `validate architecture`, `validate plan`, `validate test`, `validate implementation --mode spec`, `validate implementation --mode quality`).

## How To Apply

1. Apply the General Standards first.
2. Apply the phase-specific standards for the active phase.
3. Apply the compact Quality Contract rule IDs where they clarify a finding or checklist item.
4. For output-producing flows (`start`, `resume`, `continue`, `feedback:`, `start change:`, `import`), fix proactively before saving / showing the artifact. Do not leave a known below-quality issue in place if you can resolve it without new user input.
5. For `import [phase]`, classify findings into: accepted as-is, needs normalization, needs improvement, missing, unclear, conflicting, or redundant / out of scope.
6. Ask about every missing, unclear, conflicting, keep / drop, and below-quality item that requires human input. Only normalize silently when the change is editorial or structural and does not alter the user's intended decision.
7. For `validate *` commands, report issues only and do not modify files. Findings are graded `blocker` / `warn` / `info`. `blocker` findings prevent the corresponding `approve *` gate from succeeding. If any blocker exists, or if required structural / rule coverage evidence is missing, the validate run MUST conclude `issues-found`; it MUST NOT conclude `clean`, `pass`, or approval-ready.

When in doubt, prefer asking instead of silently upgrading substantive product, design, architecture, planning, or test decisions.

## Freedom Mode Override

Freedom mode uses this quality bar for questions, templates, in-generation self-check, import audits, and optional read-only audits, but it has no approval workflow.

- Apply every relevant quality standard and self-check exactly as written.
- Ignore validate-as-approval-gate requirements in Freedom mode. Do not tell the user to run `approve *`, and do not block phase movement on an active validate file.
- If a Freedom-mode audit finds `blocker` items, treat them as quality issues to fix or explicitly accept, not as workflow gates.
- When using shared templates in Freedom mode, remove or rewrite guided-only workflow language (`status: DRAFT`, `approved_by`, `approve *`, approval gates, `dependencies_pending`, `Pending Validation Checklist`, `<!-- PENDING: validate against product -->`) into normal quality notes, assumptions, or open questions. Keep the underlying quality requirement; drop the guided gate semantics.
- Replace Guided post-output suggestions with Freedom-mode suggestions from `core/freedom-router.md`.

## PRISM Quality Contract

Rule IDs are compact and stable. Do not derive rule identity from heading numbers; headings may move. Use these IDs in validate findings, self-review checklists, and adapter prompts when they reduce ambiguity. Do not add IDs to every sentence.

Rule record format:

| Field | Meaning |
|---|---|
| `ID` | Stable rule ID |
| `Title` | Short rule name |
| `Applies to` | Phase / artifact / code surface |
| `Severity` | `blocker`, `warn`, or `info` |
| `Check` | Short validation method |
| `Fail signal` | Clearest failure condition |

### Core Rule Registry

| ID | Title | Applies to | Severity | Check | Fail signal |
|---|---|---|---|---|---|
| `DOC-1` | Numbered review-ready structure | Generated phase artifacts | warn / blocker by artifact | Top-level content sections are numbered, or an exception is documented for index/catalog/case-list artifacts or meta sections | Reviewer cannot cite sections reliably |
| `DOC-2` | Stable item IDs | Requirements, decisions, tests, task groups | blocker | Important items have stable IDs such as `FR-xxx`, `US-xxx`, `NFR-xxx`, `BR-xxx`, `ADR-xxx`, `TC-xxx`, or task group numbers | Important item cannot be referenced downstream |
| `DOC-3` | Required template section coverage | Generated phase artifacts | blocker for required sections | Validate compares artifact headings / required fields against the source template and records present / missing / N/A sections | Artifact can pass validate while missing a required section or field |
| `LINK-1` | Concrete cross-links | Related artifacts / sections | blocker when downstream depends on it | Links use file + section or stable ID | Dependency is described only as vague prose |
| `LINK-2` | Explicit dependency contract | Dependencies, assumptions, open issues | blocker / warn | Source, reason, downstream impact, and validation path are stated | Reviewer cannot tell what must be validated |
| `ORB-1` | Sprint context as evidence | Generated artifacts | warn / blocker for change packs | Artifact preserves sprint context and relevant source / effective-truth context | Cannot tell which sprint truth produced the artifact |
| `ORB-2` | Change-pack cycle trace | Deltas and validate-cycle references | blocker | Base or `pack-<slug>` cycle is explicit | Change cannot be audited against base or pack |
| `CODE-1` | Code traceability marker | API handlers, controllers, services, jobs, migrations, non-trivial business functions | blocker for business-facing code | Marker links sprint, feature, task group, and contract refs | Code surface cannot be traced to approved scope |
| `CODE-2` | No marker noise | Trivial helpers and boilerplate | warn | Marker appears only on meaningful code surfaces | Boilerplate comments obscure real ownership |
| `CODE-3` | Repo test delta | Implementation scope | blocker when `quality_profile.repo_test_delta_required` | Repo test delta shipped per the plan's `repo_test_delta_target`, or a substantive `no test delta` justification | Implementation ships without the planned repo test delta or a justification |
| `CODE-3a` | Test technique discipline | Repo test delta (unit + integration) | blocker (structural); self-review in Freedom | Tests carry technique evidence (structured-table preferred) per `unit-test-standards.md §2–5`; integration test present when an integration surface exists else `N/A + reason`; tests deterministic; `N/A + reason` instead of bulk-tagging | A surface with boundary / multi-condition / state / failure path ships tests with no technique evidence, or tests are non-deterministic |
| `CODE-3b` | Coverage target | Repo test delta on new code | DOD target | On new/changed logic: **line ≥ 90%** (`coverage_min_new_code`) AND **branch ≥ 90%** (`coverage_branch_min_new_code`; region for Swift) — flat, no tiers; exclusions per `unit-test-standards.md §8` | New non-excluded code below the 90% line OR 90% branch (region) coverage standard |
| `CODE-3c` | Property-based selection | Pure / algorithmic surfaces | blocker (structural, light); self-review in Freedom | `property_required` surfaces ship ≥1 real-invariant property test; `property_or_examples` accept a property OR an explicit invariant/boundary example set | A parser / serializer / validator / reducer / algorithm ships only scattered example tests with no property and no invariant example set |
| `CODE-3d` | Mutation (optional, suggested) | Repo test delta | not a gate — suggested only | PRISM suggests running mutation (with ETA, §9 tool), runs it on user request, writes the report to the Implement output folder; advisory `suggested_min_score`, triage survivors. Never auto-run, never blocks | (none — non-blocking; absence of a mutation report never fails a gate) |
| `CODE-4` | Single Responsibility | New / changed classes, components, functions, modules | warn / blocker if pervasive | Each unit has one named reason to change; mixing parsing + business + persistence in one unit is a fail | Class / component / function clearly does two or more unrelated things |
| `CODE-5` | Dependency direction + module boundary | Cross-module imports, layered architecture, feature folders | blocker | Dependencies flow per the declared layered direction and stay inside the task group's `code_ownership_zones`; cross-module imports go through declared `public_entrypoints`; no cyclic deps | Code imports another module's internals, breaks layer direction, or strays outside `code_ownership_zones` |
| `CODE-6` | Size limits (function / file / class / params / nesting) | All new or changed source files | warn / blocker by language profile in `coding-standards-*` §Code Quality Thresholds | Run linter / count check against threshold table | Function / file / class / parameter count / nesting exceeds the blocker threshold without ADR justification |
| `CODE-7` | Cyclomatic complexity | All new or changed functions | warn at 10 / blocker at 15 | Static analyzer or manual review of branch count | A function's cyclomatic complexity exceeds the blocker threshold without ADR justification |
| `CODE-8` | Test seam presence | Business / domain / application functions | warn / blocker for I/O-bound business code | Time / randomness / IDs / external I/O are injected behind an interface so unit tests can stub them | Hardcoded `now()` / `random()` / SDK construction inside business logic |
| `CODE-9` | DRY (no copy-paste business logic) | Cross-file duplicated logic | warn / blocker if pervasive | Two or more locations execute the same business rule with copy-paste structure | Same rule changed in one place fails to update the others |
| `CODE-10` | Local Docker Compose self-test | Runtime implementation scopes | blocker for runtime scopes (via `validate implementation --mode spec`) | Runtime scope provides a local Docker Compose self-test path (compose, startup/teardown, healthcheck, env sample, seed/reset, happy/error commands) or an accepted no-local-runtime rationale | Runtime scope lacks a local self-test path and records no accepted rationale |
| `VAL-1` | Validate file evidence contract | Active validate files | blocker | Validate file includes target fingerprint, structural coverage, rule coverage, findings, and conclusion | Reviewer cannot tell which sections or rules were checked |
| `ADAPT-1` | Adapter prompt contract | Shared adapter prompts / role prompts | warn | Procedural steps are numbered when order matters; gate / order / check flows use tables or numbered lists; mandatory field contracts use stable field-name bullets or tables plus Rule IDs | Prompt duplicates full rule bodies, relies on heading numbers as rule identity, forces all headings to be numbered, or leaves ordered procedures / field contracts as vague prose |

Phase-specific hard rules map to these IDs plus local IDs:

| ID | Title | Applies to |
|---|---|---|
| `PROD-1` | Story Readiness Rule | Must Have user stories |
| `PROD-2` | Open Risk Rule | Vague KPI / NFR / important constraints |
| `PROD-3` | Entity Lifecycle State Rule | Product lifecycle entities |
| `PROD-4` | Product Traceability Map Rule | Epic FR / US coverage |
| `PROD-5` | Industry Lens Evidence Rule | Sprint-brief Industry Lens declaration (Principle 17) |
| `DES-1` | Implementation-Ready Design Rule | Must Have FR design blocks |
| `DES-2` | Test-Observable Design Rule | Design states, errors, validation behavior |
| `ARCH-1` | Planning-Ready Architecture Rule | Architecture package |
| `ARCH-2` | Data Flow Diagram Rule | Architecture data-flow package |
| `PLAN-1` | Delivery Traceability Index Rule | Implementation plan |
| `PLAN-2` | Task Group Field Contract | Plan task groups |
| `PLAN-3` | Parallel Execution Lanes Rule | Plan when `team_size > 1` |
| `TEST-1` | Coverage Traceability Index Rule | Test plan |
| `TEST-2` | Execution-Ready + Implementation-Consumable Handoff Rule | Test cases for Must Have FRs |
| `TEST-3` | Rule / Branch Inventory Rule | Test cases |
| `TEST-3b` | Per-AC ISTQB Technique Decision Matrix Rule | Test cases (matrix + TC title prefix) |
| `TEST-4` | Functional + SIT Coverage Rule | Test plan and test cases |
| `TEST-5` | Test Data Requirements Rule | Test cases |
| `TEST-6` | Automation Intent Rule | Test cases |
| `TEST-7` | External QA Handoff Rule | Test plan and test cases |
| `TEST-8` | Generated TSV Export Contract | Generated Functional/SIT TSV companions |
| `CODE-3` | Repo Test Delta Rule | Implementation scope |
| `CODE-3a` | Test Technique Discipline Rule | Repo test delta (unit + integration) |
| `CODE-3b` | Coverage Target Rule | Repo test delta on new code |
| `CODE-3c` | Property-Based Selection Rule | Pure / algorithmic surfaces |
| `CODE-3d` | Mutation Suggestion (optional, non-gate) | Repo test delta |
| `CODE-10` | Local Docker Compose Rule | Runtime implementation scopes |

## Validate Commands And Approve Gates

`validate *` is the only AI audit command family. `review [phase]` is retired; if the user asks for a review/audit of a phase, normalize that request to the matching validate command.

The following user-invoked validate commands gate their corresponding approve actions:

| Validate command | Phase | Blocks |
|---|---|---|
| `validate user story` | Product | `approve product` |
| `validate design` | Design | `approve design` |
| `validate architecture` | Architecture | `approve arch` |
| `validate plan` | Plan | `approve plan` |
| `validate test` | Test | `approve test` |
| `validate implementation --mode spec` | Implement | `approve implement` (one of two required modes) |
| `validate implementation --mode quality` | Implement | `approve implement` (one of two required modes) |

Rules:

- Validate commands are user-invoked and must be run explicitly before `approve [phase]` can begin.
- `approve *` then re-runs the required validate command(s) as a final full confirmation pass before locking APPROVED. This approval-time re-run does not replace the explicit validate step.
- The corresponding `approve *` gate REFUSES if the required active validate file is missing, stale, or its latest explicit validate result still contains `blocker`-level findings.
- The corresponding `approve *` gate also REFUSES if the active validate file lacks `VAL-1` evidence: target fingerprint, `DOC-3` structural coverage, Rule ID coverage, findings, and conclusion.
- A validate file with `blocker > 0`, missing required `DOC-3` / Rule Coverage evidence, or missing phase-specific hard-rule coverage MUST record latest conclusion `issues-found`; `clean` is valid only when blocker count is zero and required coverage evidence is present.
- For `approve implement`, BOTH `--mode spec` AND `--mode quality` must have been run and cleared (`blocker` count = 0). Running only one is not sufficient.
- A material edit to the artifact (via `feedback:`, `import`, change-pack absorption, etc.) invalidates the active validate file for that artifact; validate must be re-run.
- See `core/orchestrator.md § Tempo Working Files` and `§ Validate Active Files` for how active validate files are recorded and consumed by approve gates.

### Validate File Naming And Sealing

Validate files are cycle-scoped and sealed on approval. Naming pattern, lifecycle, and immutability rules are defined in `core/orchestrator.md § Validate Active Files § Naming And Cycle / § Lifecycle`. Summary:

- Active filename: `validate-<command>-<cycle>.md` where `<cycle>` is `base` or `pack-<slug>`.
- Mutable in `tempo/in-progress/` during the cycle; sealed and moved to `tempo/completed/` on successful approval (`approve [phase]` for base, `approve changes` for pack).
- Sealed files in `tempo/completed/` are immutable and MUST NOT be overwritten by any subsequent validate run; a new cycle creates a new file.
- A material edit to the artifact (`feedback:`, `import`, change-pack absorption) invalidates the active in-progress file for that cycle and forces re-running validate before the corresponding approve gate can proceed.
- Active validate files follow `VAL-1`: they record target fingerprint, structural coverage (`DOC-3`), Rule ID coverage, ordered findings, counts, and conclusion.

## Quality Profile

Phase prompts and validate commands read policy from `quality_profile` in `prism-config.md` (schema v2). When `quality_profile` is missing or a field is absent, fall back to these defaults:

| Field | Default |
|---|---|
| `review_modes_required` | `[spec, quality]` |
| `repo_test_delta_required` | `true` |
| `coverage_min_new_code` | `90` (LINE coverage on new code; no tiers) |
| `coverage_branch_min_new_code` | `90` (BRANCH coverage on new code; region for Swift; no tiers) |
| `require_contract_tests` | `conditional` (require for cross-service / public APIs) |
| `required_standards_profiles` | `[architecture-principles, architecture-solution, backend, security, devsecops]` (plus `frontend` / `ai` / `iot` / `unit-test` when applicable) |
| `manual_observation_required_for_ui` | `true` |
| `work_hours_per_day` | `6` (effective hours per day per developer working with the AI — prompt + review + feedback loop) |
| `test_design` | `technique_source: testing-standards-1.5`, `reuse_qa_matrix: optional`, `integration_when_surface: true`, `na_with_reason: required`, `technique_evidence: structured-table`, `deterministic: true`, `fold_data_driven: true` + exclusions |
| `property_based` | `enabled: true`, `property_required: […]`, `property_or_examples: […]`, `invariant_must_be_real: true`, `max_examples: 200`, `ci_seed: fixed` |
| `mutation_testing` | `mode: suggest-only`, `suggested_min_score: 80`, `triage_required: true` (optional — never auto-run, never a gate) |
| `code_thresholds` | absent → use the per-language defaults in `coding-standards-*.md §Code Quality Thresholds` |

Field meaning:

- `review_modes_required` — which `validate implementation` modes Plan must declare in `review_mode` and Implement must self-apply before declaring the scope done; Guided approval also requires them
- `repo_test_delta_required` — whether non-trivial code changes must ship a repo test delta or substantive `no test delta` justification
- `coverage_min_new_code` — LINE coverage on new code ≥ 90% (base-PRISM field); no risk tiers. Read by `CODE-3b`.
- `coverage_branch_min_new_code` — BRANCH coverage on new code ≥ 90% (region for Swift, whose llvm-cov has no branch); no risk tiers. Paired with `coverage_min_new_code`. Read by `CODE-3b`; full rules in `unit-test-standards.md`
- `require_contract_tests` — whether services / APIs must add contract tests (always / never / conditional)
- `required_standards_profiles` — logical profile names that map to standards files via `<paths.standards>/INDEX.md` (e.g. `architecture-principles` → `architecture-principles.md`, `backend` → `coding-standards-backend.md`, `frontend` → `coding-standards-frontend.md`, `ai` → `coding-standards-ai.md`, `iot` → `iot-standards.md`, `unit-test` → `unit-test-standards.md`, `architecture-solution` → `architecture-solution-standards.md`). `validate implementation --mode quality` and `validate architecture` Layer 3 must check against the mapped files. INDEX is the source of truth — keep this list in sync with INDEX entries.
- `manual_observation_required_for_ui` — whether Test phase must include manual observation TCs for UI changes
- `work_hours_per_day` — effective hours per day per developer working with the AI (prompt + review + `feedback:` loop). Used by Plan to size task groups and to compute the cumulative `Day X` timeline. The remaining workday absorbs stand-ups, peer review, and meetings. Override per-project when the team has a different cadence.
- `test_design` — Tier-1 design discipline for generated tests: ISTQB technique source, optional read-only reuse of the QA matrix, integration-only-when-surface, `N/A + reason` anti-bulk-tagging, structured-table evidence, deterministic tests, fold-to-data-driven, and exclusions. Read by `CODE-3a`. Full rules in `unit-test-standards.md`.
- `property_based` — which code shapes require a property test vs accept property-or-examples, the real-invariant guard, example cap, and fixed CI seed. Read by `CODE-3c`.
- `mutation_testing` — `mode: suggest-only` (PRISM never auto-runs it), an advisory `suggested_min_score` and triage expectation WHEN run. Mutation is optional and never a gate; PRISM suggests it and runs it on user request. Read by `CODE-3d`.
- `code_thresholds` — per-language override for `CODE-6` (size limits) and `CODE-7` (cyclomatic) defaults defined in each `coding-standards-*.md §Code Quality Thresholds`. When absent, the per-language defaults apply.

## In-Generation Self-Check (all output-producing flows)

Every output-producing flow MUST run this self-check loop internally **before outputting any artifact** — not just during `import` or before approval. This includes phase engines plus `feedback:`, `resume` / `continue`, and `start change:`. This prevents low-quality output from reaching the user at all.

This self-check is internal and must not be conflated with user-invoked `validate *` gates. During generation, the engine MUST proactively apply the same quality dimensions used by validate commands (scope-appropriate checks), so output is already near validation-pass quality before it is shown. This is different from executing a validate command: explicit validate runs remain user-invoked and are still mandatory before the corresponding approve gate.

**Step 1 — Depth gate** (run mentally before writing each artifact):
- Does every NFR/KPI have a concrete number? If not → flag as open risk, do not leave it vague.
- Does every user story have complete AC with exact behavior? If not → surface the gap.
- Does every API endpoint have field-level request/response schema? If not → do not substitute with a JSON blob.
- Does every sequence flow with multi-step DB writes have `[TX BEGIN/COMMIT/ROLLBACK]`? If not → add it.
- Does every ERD entity have a full DDL block? If not → do not substitute with "key fields".
- Does the artifact satisfy `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, and `ORB-1` where applicable? If not → add the missing structure / links / sprint evidence before output.

**Step 2 — Assumption capture** (run when writing decisions):
- Any time you make a product / design / architecture / planning / test decision where the upstream docs or user input are silent or ambiguous → insert `> Assumption: [...] / Validate: [...] / Change trigger: [...]` inline. Do not make silent assumptions.

**Step 3 — Completeness scan** (run before final output):
- For Product: Are all required Product question areas answered with numbers and specifics, or explicitly flagged as TBD-with-risk? Does every Must Have user story satisfy the Story Readiness Rule (`persona`, `AC`, `scope`, `testability`, `traceability`)? Does every epic include a `PROD-4` Product Traceability Map with one row per FR and valid `EP -> FR -> US` coverage? Are all vague KPI / NFR / important constraint items captured as explicit open risks? Does every meaningful lifecycle entity satisfy `PROD-3` with concrete states, valid transitions, triggers, invalid transitions, timeout / expiry / cancel / retry / escalation rules where applicable, and trace to affected BR / FR / US where known — or is the product explicitly marked `N/A — stateless / no meaningful lifecycle`? Does sprint-brief contain the `## Industry Lens Applied (PROD-5)` section with all five fields populated (detected vertical, confidence high/medium/low, items count by tag, region-only items, cross-domain tension), reflecting whether Principle 17 fired or explicitly fell back to baseline?
- For Design: Does every Must Have FR have ≥1 flow + ≥1 wireframe (all 4 states) + ≥1 error state with exact copy? Are all states test-observable (stable identifier, visible signal, exit condition)? When Product is DRAFT, are dependent decisions wrapped in both the assumption block and `<!-- PENDING: validate against product -->`?
- For Architecture: Do the depth-critical companion artifacts (`api-specs`, `erd`, `sequence`, `events`, `nfr`, `project-reference`) meet the depth requirements in `phase-architecture.md §5`, and are `adr` + `data-flow` consistent with the overall architecture entrypoint? Does the package include at least 3 C4 levels (System Context + Container + Component) as text-readable summaries and Draw.io/XML source references that agree with each other? Does `data-flow` include at least one DFD Draw.io/XML source using standard DFD notation, and does it cover every meaningful data movement? When multiple user groups have materially different actors, permissions, or data paths, are DFDs split by user group? Do C4 / DFD Draw.io connectors avoid cutting through shapes or containers, using arc line jumps (`jumpStyle=arc`) for unavoidable crossings? Does the package satisfy the Planning-Ready Architecture Rule (Architecture Traceability Map covers Must Have FRs; FR → component / API / sequence / data ownership traceability; integrations classified; NFR §8 mapping complete; bounded contexts and data ownership matrix where required; companion artifacts cross-linked)?
- For Plan: Does every task group have US mapping, Feature References, Tracking IDs, DOD checklist, S/M/L sizing with **all task groups ≤ 3 working days**, explicit `AI context fit`, `Estimated Start / Day Range` using `Day X` or `Day X–Y`, `target_modules_packages`, `public_entrypoints_impacted`, `inherited_architecture_obligations`, `allowed_diff_boundary`, `affected_code_surfaces`, `code_ownership_zones`, `shared_foundation_guard`, `blocks`, `blocked_by`, `qa_test_refs`, `repo_test_delta_target`, `review_mode`, and `validation commands to run`? Does the plan include a Delivery Traceability Index? Are there task groups > 3 days or context-overloaded groups that must be split? Is the relative timeline cumulative and dependency-aware? When `team_size > 1`, does the plan ship a Parallel Execution Lanes table with zero `code_ownership_zones` overlap on the same day, explicit sequencing/team-sync for shared-foundation work, plus a Task-Group Dependency Graph (`PLAN-3`)? Are `qa_test_refs` concrete when Test is ready, or explicitly `qa_test_intent_pending` when it is not? Does external QC have a concrete readiness bridge when Test declares external QA handoff? Are `no test delta` justifications substantive when `quality_profile.repo_test_delta_required` is `true`?
- For Test: Does every Must Have FR and prioritized NFR appear in a Coverage Traceability Index and map to at least one `TC-xxx` or an explicit accepted gap? Does every Must Have FR have at least one TC with concrete pre-conditions and exact expected result, manual / auto boundary, environment, data needs, teardown/reset for state changes, owner of execution context, and traceability to FR / Design states / API / NFR? Are in-scope AC / BR / rules / branches mapped to TC IDs or `N/A + reason`? Are functional/SIT coverage dimensions explicit? Are data requirements, automation intent, and external QA handoff present when applicable without generating runtime data packs or runnable automation code? Are TCs detailed enough for Dev to write the corresponding repo test delta without re-asking QA?
- For Implement: Has the code change shipped a repo test delta (or substantive `no test delta` justification)? Does that test delta follow `unit-test-standards.md` — every non-excluded test carries technique evidence (structured-table) with an observable assertion and is deterministic (`CODE-3a`); `property_required` surfaces ship a property test or an invariant/boundary example set (`CODE-3c`); new code targets line ≥ `coverage_min_new_code`% AND branch ≥ `coverage_branch_min_new_code`% (region for Swift, `CODE-3b`)? Has the engine **suggested** running mutation with an ETA where it adds value (`CODE-3d` — optional, never auto-run, never blocking)? Does the touched code stay within `allowed_diff_boundary` and the task group's `code_ownership_zones`, and follow `/docs/architecture/project-reference.md`? Does new code respect `CODE-4..CODE-9` (single responsibility, declared dependency direction, size / complexity thresholds in the language's coding standards file, test seams, no copy-paste business logic), AND follow the idiomatic patterns of the chosen language / framework (applied from model training knowledge; official framework docs may be consulted when uncertain — but project standards must still come through INDEX) without pasting idioms across ecosystems? Does every business-facing function carry the `CODE-1` traceability comment? For runtime scopes, does the project satisfy `CODE-10` with a local Docker Compose self-test path, or an explicit accepted no-local-runtime rationale? Has the engine attempted the applicable auto-test steps from `phase-implement.md §11` — lint, unit tests, integration tests, docker-backed runtime exercise, and browser / UI verification (frontend changes only; skipped for backend-only slices) — recording results in an `Auto-test summary` block before output? When a step that *should* apply cannot be auto-run (no docker daemon, no headless browser, no sandbox shell), has the engine emitted a `User self-test steps` block with copy-pasteable commands, expected outputs, and a "make next turn auto-runnable" hint — without using this as a reason to block `approve implement` (the runtime gate lives in `validate implementation --mode spec`, which is user-invoked)? If external QA applies, is the QA Handoff Bundle complete and clearly separate from QC execution / automation? Does the output explicitly suggest `validate implementation --mode spec` and `validate implementation --mode quality` for the completed task group before starting the next task group? Has generation already self-applied both validate dimensions (`spec` and `quality`): traceable to approved scope, aligned with contracts, covered by the intended repo test delta, and free of any known blocker likely to fail explicit validate?

**Step 4 — Self-review against "Treat As Below Quality If" list**: Before outputting, scan the relevant phase's "Treat As Below Quality If" list. If any item applies to the output being generated → fix it proactively rather than leaving it for the reviewer to catch.

## Consistency And Revision Standard

When revising an existing artifact or code slice, PRISM must preserve the local schema unless there is a deliberate, full-set normalization.

- Preserve existing numbering, heading shape, table shape, ID scheme, naming pattern, and sibling ordering when they are already valid.
- Prefer local delta over broad restyling. Do not rewrite untouched sibling sections just because a new format looks cleaner.
- If normalization is necessary, apply it consistently across the full related set. Never leave half old / half new structure in the same artifact set.
- Preserve valid IDs, anchors, and cross-links. If one changes, update all linked references in the touched scope.
- Feedback on code or documents must keep surrounding contracts consistent, not just the edited paragraph or file.

## General Standards

- Canonical output file names, phase folders, and Markdown filename suffixes follow `core/version-manager.md § Canonical Artifact Naming`.
- YAML frontmatter is present and valid for the active mode.
- `DOC-1`: Review-ready generated phase artifacts use numbered top-level content sections, unless the artifact is an index/catalog/case list where stable item IDs carry the structure and the exception is obvious. Meta sections such as `Appendix` and `Self-Review Checklist` may stay named rather than numbered. This rule does not require PRISM prompt/source headings to be numbered.
- `DOC-2`: Important requirements, decisions, tests, risks, task groups, and code-facing surfaces have stable IDs or stable names that downstream phases can cite.
- `DOC-3`: Validate commands compare generated artifacts against their source templates and record required sections / fields as present, missing, or intentionally N/A. Missing required sections or fields are blockers unless the template explicitly permits N/A and the artifact records the reason.
- `LINK-1`: Related sections and artifacts cross-link by file + section or stable ID when downstream work depends on them.
- `LINK-2`: Dependencies, assumptions, and open issues state source, reason, downstream impact, and validation path.
- `ORB-1`: Generated artifacts preserve sprint context and, where change packs or prior deltas matter, state the source / effective truth used.
- Required template sections exist, or are explicitly marked not applicable / intentionally skipped.
- No placeholder text such as `TBD`, `TODO`, or empty headings remains in review-ready content. Two narrow exceptions:
  - Risk-managed `TBD` is allowed ONLY for **non-functional measurable items** (NFR target, KPI baseline / target / timeframe, performance threshold, capacity number, compliance scope) — and must be captured in an open-risk, open-issues, or assumption block with owner or validator, deadline or change trigger, and downstream impact.
  - `TBD` is **never acceptable** for structural deliverables: FR, AC, persona definition, scope boundary, testability note, traceability link, ID assignment, or any contract field (API field, ERD column, event payload field, state name, error copy). When those cannot be resolved now, do NOT invent them as `TBD`. Record them in an `## Open Questions` / `## Pending Discussion` block (what was raised, why unresolved, who needs to weigh in) and treat the affected artifact as not yet present — the corresponding next-phase gate cannot pass on it.
- Statements are specific, actionable, and decision-ready.
- IDs, terminology, and cross-links stay internally consistent.
- `VAL-1`: Active validate files must prove what was checked. They include target fingerprint, structural coverage (`DOC-3`), rule coverage by Rule ID, ordered findings with severity and Rule ID where applicable, and a latest conclusion.
- `ADAPT-1`: Adapter prompts use compact Rule IDs for auditable instructions, but do not rely on heading numbers as rule identity. Number procedural steps where order matters. Use tables or numbered lists for gate / order / check flows. Use stable field-name bullets or tables for mandatory field contracts. Leave conceptual headings unnumbered when numbering would only add maintenance drift.
- Module, package, public entrypoint, dependency-boundary, and naming-convention changes are owned by `/docs/architecture/project-reference.md`; Plan, Test, and Implement consume those names and must not invent incompatible aliases.
- Risks, assumptions, dependencies, and deferred items are explicit where relevant.
- The document reads like a deliverable, not a note dump.

## Product Standard

### Must Be True

- Every requirement is traceable with stable FR-xxx IDs.
- User stories map to FR-xxx and include usable acceptance criteria.
- KPIs and NFRs are measurable, bounded, and testable.
- MoSCoW prioritization is complete.
- PRD, epics, user stories, personas, glossary, and market research agree with each other.
- Key assumptions, constraints, dependencies, and risks are explicit.
- `PROD-1`: Every Must Have user story satisfies the Story Readiness Rule: explicit `persona`, `AC` in Given / When / Then form, `scope` (in / out), `testability`, and `traceability` to FR / NFR.
- `PROD-2`: Vague KPI / NFR / important constraint that cannot be made measurable in this phase appears as an explicit row in the Product `## Open Risks` section with what is missing, downstream impact, validator, and any provisional default.
- `PROD-3`: Every meaningful lifecycle entity has concrete states, valid transitions, triggers, invalid transitions, timeout / expiry / cancel / retry / escalation rules where applicable, and trace to affected BR / FR / US where known; products without lifecycle entities state `N/A — stateless / no meaningful lifecycle` with reason.
- `PROD-4`: Every epic includes a `Product Traceability Map` table with one row per FR, the owning EP, related US IDs, priority / coverage status, and accepted-gap notes for non-Must / deferred FRs where needed. Every Must Have FR maps to at least one Must Have US.
- `PROD-5`: In guided mode, sprint-brief MUST contain `## Industry Lens Applied (PROD-5)` section reflecting Principle 17 (Domain-Informed Inquiry). In freedom mode, record the same fields as an in-chat / artifact-local note; no sprint-brief gate exists. This rule is the **canonical source** for the calibration rubric, edge case handling, declaration template, and blocker conditions. Adapter Principle 17 captures the behavioral core; this rule captures the audit contract. Full contract below.

  **Sprint-brief section template** (5 mandatory fields — verbatim header required):

  ```markdown
  ## Industry Lens Applied (PROD-5)
  - Detected vertical: <vertical name | "none — baseline">
  - Detection confidence: <high | medium | low>
  - Items surfaced: <N> [industry-standard] / <M> [common] / <K> [niche]
  - Region-specific items global-only: <count> — <list or "none">
  - Cross-domain tension: <"yes" + 1-sentence describe | "no">
  ```

  **Calibration rubric** (qualitative bet-money, NOT self-graded %):
  - `[industry-standard]` ONLY when you'd bet money this applies in ≥9/10 similar products in this vertical globally (e.g., banking always needs transaction audit log; e-commerce always needs cart).
  - `[common]` when applies in roughly 5–8/10 products but varies by region/segment/size.
  - `[niche]` when applies in <5/10 or uncertain or subset-specific.
  - For volatile items (compliance numbers, regulator/standards-body rules, league rules, regional payment methods, local market patterns): consult current authoritative sources when available before naming specific rule IDs or numbers. If not verified this turn, mark the item `unverified-current-source` and ask the user to confirm with their compliance/domain owner only if the item is material.
  - If detection signal is weak (generic SaaS, internal tool, no clear vertical keyword): do NOT fire industry layer — fall back to baseline categories rather than fabricate a vertical. Sprint-brief still requires the section with `Detected vertical = none — baseline`, counts = 0, tension = no.

  **Edge cases**:
  - Cross-domain product (e.g., hospital with ticketing + billing) → surface checklists for BOTH verticals, flag tension explicitly, ask user which is the primary lens.
  - Niche/regional vertical (VN-specific gaming, local fintech subset) → declare "training data may be limited for this niche — I will verify current sources where available; please supplement from domain knowledge if the source cannot be verified."
  - Generic/internal tools (no clear vertical signal) → skip industry layer, proceed with baseline categories, don't invent a vertical to justify firing.

  **Blocker conditions** (`approve product` refuses if any):
  - Missing `## Industry Lens Applied (PROD-5)` section in sprint-brief.
  - Any of the 5 fields missing, blank, or filled with placeholder (`TBD`, `?`, `<...>`).
  - Item count by tag inconsistent with PRD body (e.g., declares 3 `[industry-standard]` but PRD has 0 items tagged accordingly).
  - When `Detected vertical = none — baseline`: section still required, fields must show the negative case (counts = 0, region-only = 0 — none, tension = no). Silent omission is NOT allowed — fall-back must be explicit.

  See Principle 17 (`adapters/shared/guided.md` § Core Principles) for the source behavioral rule. Adapter Principle 17 references this section by name; do not duplicate detail back into the adapter.

### Treat As Below Quality If

- Targets use vague wording such as "fast", "good UX", or "high adoption".
- Stories exist without clear user value, persona context, or acceptance criteria.
- An epic lacks the Product Traceability Map, or the map omits / misstates any EP / FR / US relationship.
- Priorities are implied but not explicitly ranked.
- Personas, glossary terms, or market claims conflict with the requirement set.
- Important product bets appear unsupported or disconnected from the stated scope.
- A Must Have user story is missing `persona`, `AC`, `scope`, `testability`, or `traceability`.
- A Must Have FR has no Must Have user story.
- A KPI / NFR / important constraint is `TBD` or vague but is not captured as an explicit open risk.
- A lifecycle entity is described vaguely ("has many statuses") or lacks valid transitions, triggers, invalid transitions, or applicable timeout / cancel / retry / escalation rules.
- The sprint-brief lacks the `## Industry Lens Applied (PROD-5)` section, or the section exists but any of the five required fields is missing / `TBD` / placeholder. Or the sprint-brief claims a vertical was detected but the PRD body contains no items tagged `[industry-standard]` / `[common]` / `[niche]` consistent with the declared counts.

## Design Standard

### Must Be True

- Every relevant FR-xxx has design coverage or an explicit defer note.
- Core user flows are complete, including entry, success, error, and edge states.
- Components, patterns, responsive behavior, and design tokens are defined clearly enough for downstream work.
- Accessibility expectations are explicit.
- Linked wireframes, prototypes, and assets support the written design rather than replacing it.
- `DES-1`: Every Must Have FR satisfies the Implementation-Ready Design Rule: 4 states (`Empty` / `Loading` / `Populated` / `Error`), exact error copy per error trigger, validation behavior per input field, and explicit FR / US mapping.
- `DES-2`: Every Must Have FR satisfies the Test-Observable Design Rule: each state has a stable identifier or label QA can target, a visible signal that distinguishes it, and an exit condition.
- When Product is still DRAFT, every design decision dependent on movable Product fields carries both an inline `> Assumption / Validate / Change trigger` block AND a `<!-- PENDING: validate against product -->` marker.

### Treat As Below Quality If

- Flows skip key states, transitions, or actor handoffs.
- Screen descriptions are too vague to implement or test.
- Token usage, component behavior, or responsive rules are implied instead of defined.
- Accessibility is mentioned generically without concrete expectations.
- Visual or interaction decisions contradict product intent.
- A Must Have FR is missing any of the 4 states, exact error copy, or validation behavior.
- A state is described only as visual mood / animation without an observable signal.
- Design depends on movable Product fields without both the assumption block and the `PENDING` marker.

## Architecture Standard

### Must Be True

- `architecture/proposals/architecture-v{X}.md` acts as the package entrypoint and cross-links the supporting architecture proposal files.
- Required package artifacts exist and stay consistent: `api-specs`, `erd`, `sequence`, `data-flow`, `events`, `nfr`, `adr`, `project-reference`, plus C4 / overview content. C4 System Context + Container + Component are present as text-readable summaries and Draw.io/XML source references. At least one DFD Draw.io/XML source exists, and additional DFDs cover every meaningful data movement. If multiple user groups have materially different actors, permissions, or data paths, DFD coverage is split by user group. If a scope has no current data for one artifact, that file still exists with an explicit no-current-data / not-applicable note.
- Product scope and NFRs are reflected in the technical design.
- `ARCH-1`: Architecture Traceability Map exists in `architecture/proposals/architecture-v{X}.md` and covers every Must Have FR plus the key US links downstream phases need, and each Must Have FR traces to component / API / sequence / data ownership where applicable.
- `ARCH-2`: The package has at least one Data Flow Diagram with text-readable inventory and Draw.io/XML source using standard DFD notation (external actor / system rectangle, process circle, data store open-ended rectangle, labeled arrows). Every meaningful data movement is covered, and materially different user-group flows are split by user group.
- `validate architecture` MUST fail with `blocker` and latest conclusion `issues-found` when C4 lacks any of the 3 required levels (System Context, Container, Component), any required C4 Draw.io/XML source reference is missing, the package lacks at least one DFD Draw.io/XML source, a meaningful data movement is not covered by DFD, or materially different user-group flows are not split.
- APIs, data ownership, integration boundaries, security, observability, deployment, and failure handling are explicit enough for planning and test design.
- `/docs/architecture/project-reference.md` captures the code-facing project engineering contract: module map, source-tree / package organization, public entrypoints, dependency boundaries, active naming, and stable code surfaces.
- External integrations are classified as provider / listener / bi-directional, and webhook or multi-partner abstraction patterns are explicit when applicable.
- Event contracts define retry, replay requirement, replay window / TTL, max attempts, and dead-letter handling.
- Collection APIs make filtering, sorting, field selection, and pagination behavior explicit.
- ADRs capture the real trade-offs and rationale behind major decisions.
- NFR priority attributes each have at least one Architecturally Significant Scenario (Context → System Response → Metrics).
- Bounded Contexts and Data Ownership Matrix are present for Modular Monolith / Service-based / Microservices architectures.
- Component Interaction Overview explains the overall interaction mechanism (coordinator, sync/async, special patterns).
- C4 text-readable summaries and Draw.io/XML source references agree on actors, containers, components, and key relationships across all 3 required C4 levels.
- DFD text inventory and Draw.io/XML source agree on external actors, processes, data stores, and labeled data flows.
- C4 / DFD Draw.io connector routing is clear: connectors do not cut across or run through shapes, containers, or boundaries; unavoidable crossings use arc line jumps (`jumpStyle=arc`); labels remain readable.
- Component Deployment Matrix and Integration Deployment Matrix are present and include security mechanism per entry.
- STRIDE Threat Model covers components that handle sensitive data.
- Assumptions are explicit with confidence level and confirmation action.
- Significant Decisions are identified using the correct criteria (hard to reverse, quality attributes, deviation from standards, high cost).
- Company standards from `prism/core/standards/` have been applied (arch principles, solution standards, coding standards, security, devsecops).

### Treat As Below Quality If

- Trade-offs are asserted without rationale.
- NFR handling is vague, unmeasurable, or disconnected from the product package.
- NFR priority attributes are missing their Architecturally Significant Scenarios.
- Cross-file contracts disagree on entities, endpoints, events, or ownership.
- Deployment, resilience, security, or observability assumptions are missing or hand-waved.
- External integrations lump provider and listener behavior together, or leave webhook / partner-integration behavior implicit.
- Event failure handling omits replay policy, retention / TTL, or max attempts.
- Collection endpoints omit filter / sort / field-selection behavior or leave pagination semantics ambiguous.
- Companion artifacts exist but cannot be traced back to the architecture overview (`LINK-1`).
- `/docs/architecture/project-reference.md` is missing, weak, or inconsistent with the component / API / event / boundary model in the architecture package.
- Architecture violates `ARCH-1`: a Must Have FR cannot be traced to component / API / sequence / data ownership; integrations lack classification or contract reference; NFR §8 mapping incomplete; bounded contexts / data ownership matrix missing where required; companion artifacts not cross-linked.
- Architecture Traceability Map is absent, partial, or does not cover all Must Have FRs.
- C4 exists only as prose, or Draw.io/XML source is missing for a required C4 view or contradicts the text-readable C4 summary.
- DFD exists only as prose, lacks at least one Draw.io/XML source, misses a meaningful data movement, fails to split materially different user-group flows, omits core DFD shapes, or has unlabeled arrows (`ARCH-2`).
- C4 / DFD Draw.io connectors cut through containers, actors, processes, data stores, or boundaries; crossing lines lack arc jumps; or connector labels are unreadable.
- `validate architecture` Layer 1 (internal consistency), Layer 2 (product fit), or Layer 3 (standards compliance) reports a `blocker`-level finding that has not been resolved.
- Bounded Contexts are missing for distributed / modular architecture styles.
- Component interaction overview is absent or too vague to understand the overall interaction mechanism.
- Component or integration deployment matrices are absent, making security decisions per component/integration unclear.
- STRIDE analysis is absent or covers only generic threats without component specificity.
- Significant Decisions do not meet the "significant" criteria or lack trade-off rationale.
- Technology choices deviate from company standards without an ADR justification.
- `api-specs` endpoints lack field-level request schema tables or use JSON blob substitutes — field name/type/required/validation must be explicit.
- `api-specs` lacks an Error Code Catalog — per-endpoint errors alone are insufficient.
- `erd` entities use "key fields" notes instead of full DDL (`CREATE TABLE` with types, constraints, FKs).
- `erd` indexing section is absent or lists indexes without justifying the access pattern each serves.
- `sequence` flows with multi-step DB writes are missing `[TX BEGIN/COMMIT/ROLLBACK]` annotations.
- `sequence` external service calls are missing `[TO: Xms]` timeout annotations.
- `events` payload schema uses empty `"data": {}` instead of field-level types.
- `events` lacks Kafka Contract (topic name, partition key, consumer group) or DLQ Contract.
- `nfr` lacks §8 Config Mapping Table bridging NFR targets to `application.yml` / IaC config keys.

## Plan Standard

### Must Be True

- Every Must Have feature is represented in task groups or an explicit defer decision.
- Sequencing is realistic and dependency-aware.
- Task groups reference the required product, design, and architecture inputs.
- The plan consumes `/docs/architecture/project-reference.md` and the Architecture Traceability Map explicitly enough that implementation knows which modules / packages / public entrypoints / boundaries are in-scope.
- Task groups expose code-traceability inputs clearly enough for implementation to place stable linkage markers in code: feature refs, US refs, relevant code surfaces, and explicit tracking IDs or `none provided`.
- Task groups expose a consistent relative timeline through `Estimated Start / Day Range`, computed cumulatively from Day 1 and aligned with dependency order and team capacity.
- Every task group exposes `User Stories`, `Feature References`, `Tracking IDs`, `target_modules_packages`, `public_entrypoints_impacted`, `inherited_architecture_obligations`, `allowed_diff_boundary`, `affected_code_surfaces`, `code_ownership_zones`, `shared_foundation_guard`, `blocks`, `blocked_by`, `qa_test_refs` (TC-xxx or pending intent), `repo_test_delta_target` (in-repo test changes or substantive `no test delta` justification), `review_mode` (`spec` / `quality` / `both`), `validation commands to run`, and `AI context fit`.
- Every task group is sized at most 3 working days (default 6h / day per developer working with the AI — prompt, review, `feedback:` loop) and fits one high-quality AI implementation context window. Anything larger or context-overloaded MUST be split before `approve plan`. Larger task groups force longer AI generations, which degrade code quality and increase rework.
- `PLAN-1`: Delivery Traceability Index exists and links upstream scope to QA test intent, external QA readiness when applicable, task groups, code surfaces, validation commands, and repo test delta.
- `PLAN-2`: Every task group exposes the full field contract needed by Implement and Validate: US mapping, feature references, tracking IDs, architecture handoff fields, code surfaces, `code_ownership_zones`, `shared_foundation_guard`, `blocks` / `blocked_by`, QA intent, repo test delta target, review mode, validation commands, timeline, complexity, `AI context fit`, and DOD.
- `PLAN-3`: When `team_size > 1`, the plan contains a Parallel Execution Lanes table (Day × Lane × Task Group) where no two task groups on the same day share overlapping `code_ownership_zones`, shared-foundation work has an explicit team-sync / sequencing guard before parallel feature lanes, and a Task-Group Dependency Graph that visualizes `blocks` / `blocked_by`.
- Ownership boundaries, rollout assumptions, and risks are explicit.
- Linked test coverage, external QA readiness when applicable, or QA follow-up is visible.

### Treat As Below Quality If

- Tasks are too large, too vague, or not independently actionable.
- A task group is ≤ 3 days but still too large for one high-quality AI context window because it spans too many Product stories, Design states, Architecture contracts, code surfaces, or repo test deltas.
- Dependency order is unclear or obviously unsafe.
- Work items lack the design or architecture references needed to execute.
- Risks, rollout constraints, or ownership handoffs are omitted.
- Test implications are implied but not stated.
- Task groups lack User Story (US-xxx) mapping — a task group with no US mapping and no explicit "tech/infra" label is unacceptable.
- Task groups omit tracking-ID status or code surfaces, leaving implementation unable to place stable feature linkage markers in code.
- Task groups omit `User Stories`, `Feature References`, `Tracking IDs`, `target_modules_packages`, `public_entrypoints_impacted`, `inherited_architecture_obligations`, `allowed_diff_boundary`, `affected_code_surfaces`, `code_ownership_zones`, `shared_foundation_guard`, `blocks`, `blocked_by`, `qa_test_refs`, `repo_test_delta_target`, `review_mode`, `validation commands to run`, or `AI context fit` (`PLAN-2`).
- Any task group is sized at more than 3 working days or exceeds one high-quality AI context window and has not been split.
- `team_size > 1` but the plan is missing the Parallel Execution Lanes table, OR the table places two task groups on the same day with overlapping `code_ownership_zones`, OR shared-foundation work is parallelized without an explicit team-sync / sequencing guard (`PLAN-3`).
- The Task-Group Dependency Graph is missing, vague, or contradicts the per-task `blocks` / `blocked_by` fields.
- Delivery Traceability Index is absent, stale, or cannot connect upstream scope to execution slices (`PLAN-1`).
- A task group declares `no test delta` without substantive justification while `quality_profile.repo_test_delta_required` is `true`.
- `qa_test_refs` stay vague even though Test is already concrete enough to provide `TC-xxx`; or Test is not ready and the plan does not mark `qa_test_intent_pending`.
- External QC is expected by Test or the team, but `external_qa_readiness` does not name the delivery environment/build point, testability hooks, data/reset needs, feature flags/config, and evidence expectations.
- Task groups omit `Estimated Start / Day Range`, use inconsistent day formats, or assign day ranges that ignore dependency order or team capacity.
- Task groups lack a Definition of Done checklist.
- L-sized (>3d) or context-overloaded task groups exist without being decomposed.
- Phase Acceptance Gate is absent or uses vague language ("team reviews") instead of named approver + specific criteria.

## Test Standard

### Must Be True

- Every Must Have FR has test coverage.
- `TEST-1`: Coverage Traceability Index exists and links Must Have FRs plus prioritized NFRs to design / API / project-boundary refs and concrete `TC-xxx` IDs or explicit accepted gaps.
- Test cases use stable TC-xxx IDs.
- Test cases have strong Given / When / Then structure with clear expected results.
- Manual versus automated intent is explicit.
- Risk, negative, edge, and regression coverage is appropriate for the scope.
- Test environment, data, tooling, and prerequisites are clear enough to execute.
- Phase Test owns `qa test intent` only (`test-plan-v{X}.md`, testing `proposals/test-cases-v{X}.md`, and generated TSV companions); it does NOT own `repo test delta` (in-repo unit / integration / contract / component tests), generated runtime data packs, or external QC automation repositories. Repo test delta is dev-owned and lives in Plan / Implement.
- `TEST-2`: Every Must Have FR satisfies the Execution-Ready + Implementation-Consumable Handoff Rule: TC has stable ID, manual / auto boundary, environment, data needs, teardown/reset when state changes, owner of execution context, Given / When / Then with concrete pre-conditions and exact expected result, traceability to FR / Design states / API / NFR, and enough behavioral detail for Dev to author the corresponding repo test delta without re-asking QA.
- `TEST-3`: Rule / Branch Inventory maps every in-scope AC / BR / rule / branch to TC IDs or `N/A + reason`.
- `TEST-3b`: Per-AC ISTQB Technique Decision Matrix (`core/templates/test-cases-template.md §3.5`) is filled before TC blocks for every in-scope AC. Each `AC × {BVA, EP, DT, ST, DD}` cell is `Y` with the AC clause quoted (per `core/standards/testing-standards.md §1.5` Trigger / Emit pattern / Example / Exclusion), `N` with a concrete AC-tied reason, or covered by a `US-NNN (whole)` N/A row. Every `Y` cell produces ≥1 TC whose title carries the matching trace + Technique prefix (`[US-NNN][AC-NNN][Technique]`; imported aliases such as `[US-10.1][AC1][BVA]` are accepted during normalization; multi-technique TCs combine with `+`). Non-technique edge cases (infra failure, dependency outage, race conditions, worker/queue failures, mid-transaction failures) belong to `Corner / Error Guessing`, not in this matrix. Current release emits validator warnings (TEST-3b) for missing or malformed title prefixes; a future minor release will additionally check matrix cell completeness and hard-block on issues.
- `TEST-4`: Functional and SIT coverage dimensions are present or explicitly N/A with rationale.
- `TEST-5`: Test cases define concrete data requirements, PII-safe constraints when relevant, isolation, and teardown/reset expectations.
- `TEST-6`: Automation candidates define target test level, required data/contracts, and run environment without generating runnable automation code in Phase Test.
- `TEST-7`: External QA handoff is present when testers / automation live outside the product repo.
- `TEST-8`: Generated Functional/SIT TSV companions and export manifest exist under `testing/generated/`, are derived from the active `docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md`, and pass `core/tools/export_test_cases.py --check`.
- When `quality_profile.manual_observation_required_for_ui` is `true`, UI-affecting Must Have FRs include at least one manual-observation TC covering the visible user-facing behavior.

### Treat As Below Quality If

- Expected results are vague or unverifiable.
- Coverage exists on paper but misses important feature paths, risks, or negative scenarios.
- Coverage Traceability Index is missing, stale, or leaves Must Have FRs / prioritized NFRs unmapped to design / API / project-boundary refs and TC IDs (`TEST-1`).
- Rule / Branch Inventory omits in-scope AC / BR / rules / branches or leaves them unmapped without rationale (`TEST-3`).
- Functional or SIT coverage categories are silently omitted instead of covered or marked N/A (`TEST-4`).
- Traceability back to FRs is partial or inconsistent.
- Manual / automated ownership is unclear.
- A Must Have FR's TC is missing manual / auto boundary, environment, data needs, teardown/reset for state changes, owner, exact expected result, or traceability (`TEST-2`).
- Automation candidates lack target test level, required data/contracts, or run environment (`TEST-6`).
- External QC is expected but handoff/testability needs are missing (`TEST-7`).
- Generated TSV companions are missing, stale, manually edited, or not derivable from the current canonical Markdown (`TEST-8`).
- TCs describe only QA-side observation without enough behavioral detail for Dev to write the corresponding repo test delta (`TEST-2`).
- Test artifacts duplicate or attempt to specify repo test delta, generated runtime data packs, or external automation code (those are not QA test intent).

## Implementation Standard

### Must Be True

- Code, migrations, and config changes match the approved plan plus approved Product / Design / Architecture artifacts.
- Code placement, naming, public entrypoint usage, and dependency direction stay consistent with `/docs/architecture/project-reference.md`.
- API handlers, DTOs, entities, and SQL / ORM mappings follow the contracts in `api-specs`, `erd`, and `sequence` exactly enough that downstream tests do not need reinterpretation.
- `CODE-1`: New or materially changed APIs and non-trivial business code carry concise traceability markers that map back to the selected sprint, Feature refs, User Stories, Task Group, relevant API / contract, and any explicit pack / tracking IDs from approved inputs.
- `CODE-4..CODE-9`: New or changed code respects the software design principles documented in `coding-standards-backend.md §1`, `coding-standards-frontend.md §1`, and `coding-standards-ai.md §1A` (single responsibility, declared dependency direction and module boundaries, size / complexity thresholds, test seams, DRY). Concrete thresholds live in §Code Quality Thresholds of each coding standards file.
- **Framework idiom adherence**: generated code follows the idiomatic patterns of the chosen language / framework. Idioms are intentionally NOT enumerated in PRISM standards (they would bloat and drift); the AI applies them from its training knowledge of the chosen stack and may consult official framework docs when uncertain (a narrow exception to the "never load standards from web" rule, applicable only to framework idioms and not to PRISM project standards). Do not paste idioms across ecosystems.
- Required tests and config updates are shipped with the code change.
- `CODE-3`: Repo test delta is shipped per the plan's `repo_test_delta_target`, OR a substantive `no test delta` justification is provided when `quality_profile.repo_test_delta_required` is `true`.
- `CODE-3a..3d`: The repo test delta follows `unit-test-standards.md` — PRISM-gated structure (technique evidence + deterministic + property selection; `CODE-3a` / `CODE-3c`), a single flat coverage standard on new code — line ≥ 90% (`coverage_min_new_code`) AND branch ≥ 90% (`coverage_branch_min_new_code`; region for Swift) (`CODE-3b`), and mutation that is **optional / suggested** (`CODE-3d` — PRISM suggests it with an ETA and runs it on request, never auto-runs, never blocks). PRISM does not run coverage tools as a gate; it runs available local test commands and reads a report if present.
- `CODE-10`: Runtime implementation scopes provide a local Docker Compose self-test path (compose file or project-declared equivalent, startup/teardown, healthcheck, env sample, seed/reset where stateful, happy/error self-test commands), or an explicit accepted no-local-runtime rationale.
- Repo test delta covers the test intent declared in `qa_test_refs`; if `qa_test_refs` is still pending, repo tests cover the FR / NFR / US the task group was scoped against.
- If Test is already APPROVED, the delivered scope and repo test delta can be reconciled against concrete TC refs in the approved QA package.
- When Plan/Test declares external QA handoff for the selected scope, implementation produces a QA Handoff Bundle with build / commit / version, target environment URL, changed endpoints / screens, API contract refs, selector map / stable DOM hooks, seed/reset refs, test account roles as secret-source references only, feature flags/config, known limitations, and evidence location.
- Before implementation is declared done, both `validate implementation --mode spec` and `--mode quality` have been self-applied on the current scope and have no remaining `blocker` findings; Guided `approve implement` also requires explicit validate files for both modes.
- Timeouts, retries, rate limits, circuit-breaker values, and replica assumptions come from approved config / IaC mapping rather than magic numbers embedded in code.
- Logging, metrics, error codes, and security-sensitive behavior follow the active repo standards.
- Feedback preserves or updates traceability markers when code scope changes.

### Treat As Below Quality If

- Field names, types, status codes, schema constraints, or state transitions drift from the approved artifacts.
- Code drifts from `/docs/architecture/project-reference.md` without an approved architecture / plan change.
- Code edits files outside the task group's declared `code_ownership_zones` without a recorded plan amendment (`CODE-5`).
- A class / component / function mixes unrelated responsibilities (e.g. HTTP parsing + business rules + persistence in one unit) (`CODE-4`).
- Cross-module imports reach into another module's internals instead of going through the declared `public_entrypoints` (`CODE-5`).
- A function / file / class / parameter count / nesting depth / cyclomatic complexity exceeds the blocker threshold in the language's coding standards file without an ADR (`CODE-6`, `CODE-7`).
- Business logic hardcodes `now()` / `random()` / SDK construction, leaving no test seam (`CODE-8`).
- Generated tests carry no technique evidence on a surface with a boundary / multi-condition / state / failure path, are non-deterministic, or bulk-tag techniques instead of using `N/A + reason` (`CODE-3a`); a `property_required` surface ships neither a property test nor an invariant/boundary example set (`CODE-3c`); line coverage on new code is below `coverage_min_new_code` OR branch coverage below `coverage_branch_min_new_code` without an accepted exclusion (`CODE-3b`).
- The same business rule is copy-pasted across two or more locations (`CODE-9`).
- Generated code ignores the idiomatic patterns of the chosen language / framework, or pastes idioms from a non-matching ecosystem. Idiom drift is a `warn` by default and a `blocker` when it produces measurable defects (perf, leak, security, contract drift).
- Magic numbers / strings / operational thresholds embedded as literals instead of bound from `nfr-v{X}.md §8` config or named constants.
- Business-facing code or APIs lack feature linkage markers (`CODE-1`).
- Traceability markers are stale, generic, or inconsistent with the approved task slice.
- Ticket / task IDs are invented instead of copied from approved inputs.
- Boilerplate traceability comments are sprayed across trivial helpers while the actual business entrypoints remain unlinked (`CODE-2`).
- Code hardcodes operational values that should come from `nfr-v{X}.md §8` or deployment config.
- Implementation skips the tests, migrations, or config changes required for the delivered scope.
- Logging / error handling is inconsistent with the approved error catalog or observability standards.
- Feedback on code is applied narrowly but leaves the surrounding contract or tests inconsistent.
- Test data or environment assumptions are missing.
- Repo test delta is missing or trivial when the change scope materially modifies behavior, and no substantive `no test delta` justification is provided.
- Repo test delta does not match `repo_test_delta_target` from the approved plan and the divergence has no recorded rationale.
- Repo test delta does not cover the test intent declared in `qa_test_refs` (or the equivalent FR / NFR / US scope when QA test intent is still pending).
- Test is APPROVED, but implementation cannot be reconciled against the approved TC refs that the scope should satisfy.
- External QC handoff is expected, but implementation output lacks the QA Handoff Bundle or leaves environment/build, selectors/API refs, seed/reset, account-role secret refs, feature flags/config, known limitations, or evidence location vague.
- Runtime scope lacks a Docker Compose local self-test path and does not record an accepted no-local-runtime rationale (`CODE-10`).
- Either `validate implementation --mode spec` or `--mode quality` has not been self-applied, or has unresolved `blocker` findings, when implementation is being declared done.
