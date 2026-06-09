# Phase Engine: Plan

## Trigger

`start plan` — requires: product + design + architecture ALL APPROVED.

In a newer sprint, `start plan` and `approve plan` also require all previous sprints to already be sealed. If any earlier sprint is still unsealed, Plan stays blocked in this sprint until that earlier sprint closes with `approve implement`.

**Planning is a separate lane from implementation.** This phase produces the task-level delivery plan. It does not write code, unit tests, or test cases.

## Behavior

1. Read the approved Product, Design, and Architecture effective truth, including `/docs/architecture/project-reference.md`, ERD, API specifications, and NFR package.

2. **Ask about planning context**:
  - Delivery phases or milestones to plan for?
  - **Team size**: how many **developers who actually drive AI code generation** will run this sprint in parallel (default `1`)? Count only the people who will write prompts, review AI output, and feed `feedback:` back to the AI. Do NOT count product owners, QA / testers, designers, or stakeholders — they participate via Test / Product / Design phases, not by occupying a Lane here. Each counted developer is budgeted **6 effective hours per day working with the AI** by default (writing prompts, reviewing diffs, iterating on `feedback:`); the remaining ~2 hours of the workday absorb stand-ups, code review of teammates, and meetings. Override only if `prism-config.md` declares a different `quality_profile.work_hours_per_day`.
  - Priority order: MVP first, risk-first, dependency-first, or other?
  - Technical sequencing constraints or rollout requirements?
  - Which ticket / task / board IDs, if any, must implementation preserve in code traceability markers?
  - Which APIs, handlers, services, jobs, modules, or migrations are the stable code surfaces for each task group?
  - Which modules / packages, public entrypoints, and dependency boundaries from `/docs/architecture/project-reference.md` are in-scope for each task group?
  - Do testers / QC automation execute outside the product repo; if yes, which environment, build, selector/API hook, seed/reset, account-role, feature-flag, and evidence handoff items must Dev provide?

   **Vague answer handling**: Accept 'not sure' / 'skip' gracefully — record as TBD with a note. Do not block on missing planning context. The only exception: when `team_size` is missing, default to `1` and proceed (linear timeline, no parallel lanes table required).

3. **Plan depth requirements — non-negotiable**:

  - **User Story mapping (prominent)**: Every task group MUST list the User Story IDs it delivers (US-xxx) as a named field — not buried in notes. A task group with no US mapping is unacceptable unless it is explicitly infrastructure/tech-debt (and must be labeled as such).
  - **Code-traceability inputs per task group**: Every task group MUST expose the code-facing linkage inputs implementation needs: feature refs, user stories, task group reference, any explicit ticket / task / board IDs (`none provided` if absent), and the APIs / handlers / services / jobs / modules expected to carry the linkage markers in code.
  - **Architecture contract handoff per task group**: Every task group MUST expose the architecture-side contract it consumes from `/docs/architecture/project-reference.md` and the Architecture Traceability Map: `target_modules_packages`, `public_entrypoints_impacted`, `inherited_architecture_obligations`, and `allowed_diff_boundary`.
  - **Affected code surfaces**: Every task group MUST expose `affected_code_surfaces` as a named field listing the concrete code surfaces this task touches: APIs (paths + methods), services, handlers, jobs, migrations, UI modules. This drives `validate implementation --mode spec` review scope. Use `none` only for pure non-code task groups (and label them as such).
  - **QA test intent (`qa_test_refs`)**: Every task group MUST expose `qa_test_refs` listing the QA test intent it maps to in the Test phase. If Test is APPROVED or already has usable draft artifacts, list `TC-xxx` IDs and / or test scenarios from `/docs/testing/test-cases.md` and `test-plan-v{X}.md`. If Test has not started yet, or the test lane is not yet concrete enough, list the FR / NFR / US the task group is expected to be tested against with status `qa_test_intent_pending`.
  - **Repo test delta target (`repo_test_delta_target`)**: Every task group MUST expose `repo_test_delta_target` describing the in-repo test changes the task is expected to ship: which unit / integration / contract / component tests get added or modified, or an explicit `no test delta — [reason]` justification. `repo_test_delta_target` covers tests in the codebase only — it is dev-owned and distinct from `qa_test_refs`. If `quality_profile.repo_test_delta_required` is `true` (default), `no test delta` justifications must be substantive (e.g., "config-only change, covered by existing schema validation tests"); blank or trivial reasons block `approve plan`. This is the planning-level test *intent* (which unit / integration / contract tests, or `no test delta`); the detailed technique evidence is authored by Implement, not Plan (see `core/standards/unit-test-standards.md`).
  - **External QA readiness (`external_qa_readiness`, conditional)**: When Test declares external QA handoff or testers / QC automation live outside the product repo, every affected task group MUST expose the external-QA bridge it will deliver: target environment/build point, stable selectors / `data-testid`, API contract refs, seed/reset support, account roles as secret references only, feature flags/config, evidence expectations, and known limitations. If the template field is present but external QC is not in scope, use `N/A — no external QA handoff for this task group`.
  - **Delivery Traceability Index (`PLAN-1`)**: The plan MUST contain a compact index that links `FR / NFR / US -> architecture refs -> qa test intent -> external QA readiness when applicable -> task group -> affected_code_surfaces -> validation commands -> repo_test_delta_target`. This is the Plan-side bridge into execution.

  - **Review mode per task group (`review_mode`)**: Every task group MUST declare which `validate implementation` modes the task expects to be run before its scope can be considered done: `spec`, `quality`, or `both`. Default is `both` unless `quality_profile.review_modes_required` overrides.

  - **Validation commands to run**: Every task group MUST list the explicit validation commands Implement is expected to run (and pass) before declaring the task scope done. Typical entries: `validate implementation --mode spec`, `validate implementation --mode quality`. Optional task-specific entries (e.g., a security-sensitive task adding `security-standards check`) are allowed but may not replace the default modes implied by `review_mode`.

  - **Task Group Field Contract (`PLAN-2`)**: Every task group MUST expose the full named field set needed by Implement and Validate, including `User Stories`, `Feature References`, `Tracking IDs`, `target_modules_packages`, `public_entrypoints_impacted`, `inherited_architecture_obligations`, `allowed_diff_boundary`, `affected_code_surfaces`, `code_ownership_zones`, `shared_foundation_guard`, `blocks`, `blocked_by`, `qa_test_refs`, `repo_test_delta_target`, `review_mode`, `validation commands to run`, `Estimated Start / Day Range`, `Complexity`, `AI context fit`, and DOD checklist.
  - **Definition of Done per task group**: Every task group MUST have a DOD checklist (6–7 items minimum) covering: code merged to main, unit tests pass with line coverage ≥ `quality_profile.coverage_min_new_code`% AND branch coverage ≥ `quality_profile.coverage_branch_min_new_code`% on new code (both default 90; region for Swift), integration tests pass when the task has an integration surface, API contract matches api-specs, security review if auth/data-sensitive, design spec verified if UI, feature flag state documented if applicable, `repo_test_delta_target` shipped or justified, QA Handoff Bundle produced when `external_qa_readiness` is not N/A, `validate implementation` modes per `review_mode` passed.

  - **Complexity with explicit day definitions and AI context fit**: Use S/M/L sizing with these mandatory definitions (a "day" = `quality_profile.work_hours_per_day` of one developer **working with the AI**, default 6h):
     - S = ≤ 2 days
     - M = 2–3 days (target shape for most task groups)
     - L = > 3 days → MUST be split before `approve plan`
     A task group larger than 3 days produces too much code in one prompt and degrades generation quality. Split it into smaller task groups, do not collapse it.

     The day cap is necessary but not sufficient. Every task group must also fit one high-quality AI implementation context window: the selected Product stories, Design states, Architecture contracts, code ownership zone, and intended repo test delta must be small enough that the implementing AI can load and reason over them together without dropping contract details. If a 1–3 day task touches too many files, APIs, design states, data entities, or cross-cutting contracts to fit in one context window, split it by user-story slice, code ownership zone, contract surface, or module boundary before approval.

  - **Cumulative delivery timeline**: After sizing all task groups, compute a cumulative relative timeline from Day 1 using dependency order and available team capacity. Every task group MUST expose `Estimated Start / Day Range` as a named field using the format `Day X` or `Day X–Y`. Keep the format consistent across the whole plan; do not hide timeline details inside Delivery Notes.

  - **Code ownership zones (`code_ownership_zones`)**: Every task group MUST expose `code_ownership_zones` — the concrete list of files / folders / modules this task group is allowed to write to. This is stricter than `target_modules_packages`: it lists the actual paths (`src/payments/**`, `db/migrations/2026_05_*`, `web/features/orders/**`) that a developer or AI may touch. The plan engine MUST verify zero overlap between any two task groups scheduled on the same Day in the Parallel Execution Lanes table — overlap on the same day is a merge-conflict hazard and is a `PLAN-3` blocker.

    Because AI-generated code has high overlap risk, shared-foundation work is not considered safe parallel work even when the team has capacity. If multiple task groups need the same shared code zone (common models, base API clients, auth middleware, generated types, routing shell, design-system primitives, migrations touching the same tables), sequence that shared-area task first as a team-sync generation/review step, then assign separate non-overlapping feature / US slices in later lanes.

  - **Task-group dependency fields (`blocks`, `blocked_by`)**: Every task group MUST expose `blocks: [TG-id, ...]` (downstream task groups that wait on this one) and `blocked_by: [TG-id, ...]` (upstream task groups that must finish first). Use `[]` when there is no dependency. These fields drive both the dependency graph and the parallel lanes scheduling.

  - **Parallel Execution Lanes (conditional)**: When `team_size > 1` (recall: `team_size` counts only developers driving AI code generation, not QA / PO / designer), the plan MUST include a `Parallel Execution Lanes` table with one row per Day and one column per Lane (`Lane A`, `Lane B`, ... up to `team_size` lanes). Each cell names which task group runs in that lane that day, or is empty. The table MUST satisfy:
     - No two cells on the same Day share overlapping `code_ownership_zones`.
     - Shared code zones are either owned by exactly one lane for that Day or sequenced as an earlier team-sync generation/review step before parallel feature work begins.
     - Every cell respects `blocked_by` — a task group only appears after all of its dependencies have completed in an earlier Day.
     - Every task group from the breakdown appears at least once.
     - Capacity per cell is exactly one work-day for one developer (= `quality_profile.work_hours_per_day`).
     The table is `PLAN-3`. When `team_size == 1`, the lanes table is OPTIONAL and the plan may use a single-column daily schedule instead.

  - **Task-Group Dependency Graph**: The plan MUST include a Mermaid (or equivalent textual) directed graph at the **task-group** level (not phase level) showing each task group node and arrows for `blocks` / `blocked_by`. The graph MUST be consistent with the per-task fields. The previous phase-level dependency graph alone is no longer sufficient.

  - **Phase Acceptance Gate (not just a "Handoff" note)**: The plan MUST end with an explicit Phase Acceptance Gate section specifying:
     - Acceptance criteria (numbered list — what must be true)
     - Named approver role (Tech Lead / PO / QA Lead — not just "team")
     - Approval method (async via PR comment / sync meeting / written sign-off)

  - **Delivery Notes over Implementation Notes**: Use delivery language — what the team produces and when — not architectural commentary (that belongs in the architecture files already read).

4. Produce the implementation plan in one pass, then run the shared self-check in `core/phase-quality-standards.md` before presenting it.

## Input Context

- Required: **Effective Truth** for product + design + architecture (per `core/version-manager.md § Effective Truth`). Compose via `python .prism/core/tools/effective_truth.py --phase all --up-to-sprint v{X}`. The composed views contain `/docs/product/prd.md` + `/docs/product/epics/EP-NNN-{slug}.md` + `/docs/design/design-system.md` + `/docs/architecture/architecture.md` Living Truth merged with the active sprint's APPROVED proposals + change-pack deltas. All three upstream artifact phases (product/design/architecture) must be APPROVED in the active sprint, and any earlier unsealed sprints must be sealed, before `start plan` (per `core/sprint-manager.md § Plan Gate`).
- Required: architecture effective truth files — `/docs/architecture/project-reference.md`, `/docs/architecture/erd.md`, `/docs/architecture/api-specs.md`, `/docs/architecture/nfr.md`
- Optional: `/docs/architecture/sequence.md`, `/docs/architecture/adr.md`, `/docs/architecture/data-flow.md`, `/docs/architecture/events.md`, prior sprint's `implementation-plan-v{X-1}.md`, `prism-config.md`
- Prohibited inputs: sealed sprints' files (their content already lives in Living Truth — load Living Truth instead), other sprints' DRAFT proposals, snapshots folder (audit-only), execution outputs from later phases

Plan is a **sprint-only work process** artifact (per `core/version-manager.md § Folder Structure Per Sprint`). It does NOT merge into Living Truth at sprint seal — it stays in `docs/sprint-v{X}/planning/` forever.

## Output

Written to `/docs/sprint-v{X}/planning/`:

| File | Template | Content |
|------|----------|---------|
| `implementation-plan-v{X}.md` | `core/templates/implementation-plan-template.md` | Task-level phases, task groups (each ≤ 3 days and one AI context window), full `PLAN-2` fields including `Feature References`, `Tracking IDs`, `code_ownership_zones`, `shared_foundation_guard`, `blocks`, `blocked_by`, and `AI context fit`, cumulative delivery timeline, Parallel Execution Lanes table (when `team_size > 1`), Task-Group Dependency Graph, delivery traceability index, ownership, delivery risks |

The plan must satisfy `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `PLAN-1`, `PLAN-2`, and (when `team_size > 1`) `PLAN-3`.

## Boundary With Test And Implement

- `start test` runs in parallel with `start plan` — both require the same approved prerequisites.
- `start implement` consumes the approved implementation plan and writes code plus unit tests.
- `approve implement` requires `test` to be APPROVED. Test can run concurrently with implementation, but must be approved before the implementation pass can close.
- `approve plan` does NOT require `test` to be APPROVED. It requires explicit `qa_test_refs` as QA test intent: concrete `TC-xxx` refs when Test is already concrete enough, or `qa_test_intent_pending` when Test is not ready yet.
- Test declares external QA handoff needs; Plan maps them into `external_qa_readiness`; Implement supplies the runnable-slice QA Handoff Bundle when the code/environment exists. External QC automation itself can remain outside PRISM and outside the product repo.
- When Test becomes APPROVED, implementation must reconcile the approved QA test package against the plan's `qa_test_refs` before `approve implement` closes the scope.

## Gate

Tech Lead / Dev Lead checks → `validate plan` → `approve plan` or `feedback: [...]`

`approve plan` is blocked if any of the following are true:

- any previous sprint is not yet sealed
- a task group violates `PLAN-2` by missing `US mapping`, `Feature References`, `Tracking IDs`, `DOD`, `Estimated Start / Day Range`, `target_modules_packages`, `public_entrypoints_impacted`, `inherited_architecture_obligations`, `allowed_diff_boundary`, `affected_code_surfaces`, `code_ownership_zones`, `shared_foundation_guard`, `blocks`, `blocked_by`, `qa_test_refs`, `repo_test_delta_target`, `review_mode`, `validation commands to run`, or `AI context fit`
- external QC is expected but the affected task group does not expose concrete `external_qa_readiness`
- any task group is sized > 3 days (L), or exceeds one high-quality AI implementation context window, and has not been decomposed
- a task group declares `no test delta` without a substantive justification when `quality_profile.repo_test_delta_required` is `true`
- `team_size > 1` but the plan is missing the Parallel Execution Lanes table, OR two task groups in the same Day row share overlapping `code_ownership_zones`, OR shared-foundation work is parallelized without an explicit team-sync / sequencing guard (`PLAN-3`)
- the Task-Group Dependency Graph is missing or contradicts the per-task `blocks` / `blocked_by` fields
- the plan violates `PLAN-1` by omitting the Delivery Traceability Index, or that index cannot connect upstream scope to QA test intent, external QA readiness when applicable, task groups, code surfaces, validation commands, and repo test delta
- Test is already concrete enough but `qa_test_refs` still do not point to any `TC-xxx` or test-scenario references; OR Test is not ready yet and the task group does not carry explicit `qa_test_intent_pending`
- the active `validate plan` file is missing, stale, or its latest explicit result still contains `blocker`-level findings (see `core/orchestrator.md § Validate Active Files`)
- an active upstream or direct change pack impacts Plan and Plan has not absorbed that change through:
  - `feedback:` if Plan is `DRAFT`, or
  - a Plan delta if Plan is already `APPROVED`

## Validate Plan Command

`validate plan` is a user-invoked audit command. It runs read-only against the current Plan DRAFT and approved upstream artifacts, produces a structured `blocker` / `warn` / `info` report, and writes or updates the active validate file for this command (named per `core/orchestrator.md § Validate Active Files`). It must be run on the current DRAFT before `approve plan` and re-run after any `feedback:` or change-pack absorption that materially changes the plan.

During normal Plan generation, the engine must already self-apply the same delivery-readiness logic before outputting the draft.

`approve plan` requires that active validate file to already be present and clean, then re-runs `validate plan` in console-only mode as a final full confirmation pass. If that approval-time run finds any blocker or material gap, do not approve; show the findings to the user first and ask whether they want to update the active validate file into a follow-up checklist.

### Scope

Validate Plan checks:

- `DOC-3`: required sections / fields from `core/templates/implementation-plan-template.md` are present or explicitly marked N/A with reason.
- `VAL-1`: the active validate file records structural coverage and rule coverage for `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `PLAN-1`, `PLAN-2`, and `PLAN-3`.
- Upstream fit: Product, Design, Architecture, `/docs/architecture/project-reference.md`, ERD, API specs, and NFR references are approved, loaded, and reflected in the plan.
- `PLAN-1`: every Must Have FR / prioritized NFR / relevant US maps to architecture refs, QA test intent, external QA readiness when applicable, task group, affected code surfaces, validation commands, and repo test delta target.
- `PLAN-2`: every task group exposes `User Stories`, `Feature References`, `Tracking IDs`, `target_modules_packages`, `public_entrypoints_impacted`, `inherited_architecture_obligations`, `allowed_diff_boundary`, `affected_code_surfaces`, `code_ownership_zones`, `shared_foundation_guard`, `blocks`, `blocked_by`, `qa_test_refs`, `repo_test_delta_target`, `review_mode`, `validation commands to run`, `Estimated Start / Day Range`, `Complexity`, `AI context fit`, and DOD checklist.
- `PLAN-3`: when `team_size > 1`, the Parallel Execution Lanes table exists, has one column per developer (up to `team_size`), every task group appears, no two cells on the same Day have overlapping `code_ownership_zones`, shared-foundation work is sequenced or team-synced before parallel work, and every cell respects `blocked_by`. The Task-Group Dependency Graph exists and is consistent with the per-task `blocks` / `blocked_by` fields.
- Task-group size: every task group is sized ≤ 3 days and fits one high-quality AI implementation context window; any larger or context-overloaded task group is split before approval.
- QA intent: concrete `TC-xxx` / scenario refs are used when Test is concrete enough; otherwise `qa_test_intent_pending` links to the FR / NFR / US to be tested. When external QC is expected, `external_qa_readiness` maps the Test handoff needs to delivery work.
- Repo test delta: non-trivial code tasks declare concrete in-repo test changes (the test *intent*: which unit / integration / contract tests), or a substantive `no test delta` reason when allowed by `quality_profile`.
- Sequencing realism: dependencies, capacity assumptions, cumulative day ranges, ownership, parallel lanes (when applicable), and L-sized task splits are coherent.
- Open Issues: every `## Open Issues` row is closed before approval.

A `blocker` finding in any area above blocks `approve plan`.

### Expected Output

```text
validate plan: implementation-plan-v{X}.md
blocker: 2
warn: 1
info: 0

Findings:
- blocker [PLAN-2]: Task Group 2.1 lacks `allowed_diff_boundary`, `code_ownership_zones`, `shared_foundation_guard`, `AI context fit`, and `repo_test_delta_target`.
- blocker [PLAN-3]: team_size=3 but Parallel Execution Lanes places TG 1.1 and TG 1.3 on Day 2 with overlapping code_ownership_zones (`src/payments/**`). Re-sequence or re-scope.
- warn [PLAN-1]: Delivery Traceability Index maps FR-018 to a task group but leaves QA intent as vague text instead of `TC-xxx` or `qa_test_intent_pending`.

→ Fix blockers with `feedback plan: ...`
→ Then `validate plan`
→ Then `approve plan`
```

The active validate file is named and lifecycled per `core/orchestrator.md § Validate Active Files` (cycle-scoped: `validate-plan-<cycle>.md` in `tempo/in-progress/` while running, sealed and moved to `tempo/completed/` on approval success).

## Same-Sprint Change Handling

- If Plan has not started, future `start plan` reads effective truth.
- If Plan is `DRAFT`, merge impacted upstream changes via `feedback:`.
- If Plan is `APPROVED`, same-sprint changes use a Plan delta in the selected change pack.

## Quality Standard

Plan like a **Staff Engineer** — explicit sequencing, realistic scope, task boundaries that are implementable, and test intent / external QA readiness when applicable mapped to delivery phases.
