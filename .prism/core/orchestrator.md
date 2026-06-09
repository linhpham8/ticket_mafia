# Orchestrator

> **Guided mode only.** This file handles explicit commands, natural-language command normalization, and gate-aware routing for Guided mode.
> Freedom mode uses `core/freedom-router.md`.
> Both modes share all `core/phase-*.md` files — phase questions, quality bars, and templates are identical.

Central routing engine. Parses user commands, enforces gates, manages context loading.

## Natural Language Intent Parsing

Users do not need to type exact commands. Parse intent from natural phrasing:

| Natural phrase | Interpreted as |
|----------------|---------------|
| "looks good", "ship it", "that's fine", "ok approve" | `approve [current phase]` |
| "approve these changes", "approve all generated changes" | `approve changes` |
| "this needs work on X", "change X to Y", "add Z" | `feedback: [extracted changes]` |
| "change X and approve" | `feedback: [changes], approve [phase]` |
| "revise the approved doc", "same-sprint correction", "start change: ..." | `start change: [extracted summary]` |
| "validate this change pack", "audit these changes", "validate change xyz" | `validate changes [pack-id|slug]` |
| "what's next?", "now what?", "where are we?" | `status` + next action suggestion |
| "I already have a PRD", "we have docs from Confluence" | guide to `import [phase]` flow |
| "pick up where we left off", "continue" | `resume` |
| "start over with a new version" | `new sprint` |
| "audit the user stories", "check the stories" | `validate user story` |
| "audit the design", "review the design rigorously" | `validate design` |
| "audit the architecture", "review the architecture rigorously" | `validate architecture` |
| "audit the plan", "review the plan rigorously" | `validate plan` |
| "audit the tests", "review the test plan" | `validate test` |
| "audit the code against spec", "is the code on contract" | `validate implementation --mode spec` |
| "audit the code quality", "code quality review", "standards check on the code" | `validate implementation --mode quality` |

If intent is ambiguous, state your interpretation and proceed — except for `feedback:`, `resume`, `continue`, `validate changes`, and `approve changes` when more than one active target is plausible. In those cases ask the user to choose; do not guess.

## Command Normalization

Normalize equivalent command forms before routing:

- Treat `arch` and `architecture` as the same phase name for `start`, `approve`, `validate`, `diff`, and `import`
- Treat `continue` as an alias of `resume` for both command-style and natural-language continuation requests
- If the user types an obvious one-edit typo of a known command or phase (for example `aprove`, `statuz`, or `architecure`), correct it, state the normalized command in one short line, and proceed
- If more than one correction is plausible, ask a one-line clarification instead of guessing

## Command Table

| Command | Action |
|---------|--------|
| `start product` | Begin Product phase — AI asks comprehensive questions |
| `start design` | Begin Design phase from the current Product package; if Product is still DRAFT, keep Design DRAFT with product validation pending |
| `start arch` | Begin Architecture phase from the approved Product package (`arch` = shorthand for architecture) |
| `start plan` | Begin implementation planning from approved Product + Design + Architecture |
| `start test` | Begin independent test-design / QA validation work |
| `start implement` | Begin code execution from an approved implementation plan |
| `start change: [content]` | Open a same-sprint change pack with id `v.x.y.z-slug` for an APPROVED artifact in the current or explicit sprint |
| `status` | Show the canonical status block: active target, DRAFT change packs with related phases/files, sprint states with lane files, blockers, and next step |
| `approve [phase]` | Mark a document phase APPROVED, or with `approve implement` close the sprint's only implementation pass and seal the sprint (sprint seal = the boundary that promotes content into Living Truth; see `core/version-manager.md § Core Concept`) |
| `approve changes [pack-id|slug]` | Approve the selected DRAFT change pack up to the current downstream phase; ask if ambiguous |
| `validate changes [pack-id|slug]` | Aggregate read-only audit for the selected DRAFT change pack: resolve impacted phases, run the existing phase validate command(s) for cycle `pack-<slug>`, and update the required active validate files |
| `feedback: [content]` | Parse feedback → resolve exactly one target → apply → output DRAFT |
| `new sprint` | Create the next sprint when product + design are APPROVED in the latest sprint and no DRAFT change pack remains open there; plan, test, implement in new sprint are gated until previous sprint seals |
| `diff [phase]` | Compare current vs previous sprint version |
| `resume` / `continue` | Detect last state from file layer → continue incomplete work |
| `import [phase]` | Import externally-created document, audit it against the phase standard, and synthesize a review-ready DRAFT |
| `validate user story` | Read-only audit of the current Product DRAFT package (cross-checks PRD lifecycle rules, epics, user stories, glossary, personas, market evidence, and proposal structure) — required before `approve product`; see `core/phase-product.md § Validate User Story Command` |
| `validate design` | Read-only audit of the current Design DRAFT against product fit, implementation-readiness, test-observability, and pending markers — required before `approve design`; see `core/phase-design.md § Validate Design Command` |
| `validate architecture` | Read-only audit of the current Architecture DRAFT across 3 layers (internal consistency, product fit, standards compliance) — required before `approve arch`; see `core/phase-architecture.md § Validate Architecture Command` |
| `validate plan` | Read-only audit of the current Plan DRAFT against delivery traceability, task-group field contract, sequencing, and repo-test-delta intent — required before `approve plan`; see `core/phase-plan.md § Validate Plan Command` |
| `validate test` | Read-only audit of the current Test DRAFT against coverage traceability, execution-ready + implementation-consumable handoff, rule / branch inventory, functional/SIT coverage, data requirements, automation intent, external QA handoff, and generated TSV export freshness — required before `approve test`; see `core/phase-test.md § Validate Test Command` |
| `validate implementation --mode spec` | Audit + runtime verification: static cross-check of code scope vs Product / Design / Architecture / Plan / repo test delta, PLUS runtime evidence (start app, run repo test suite, capture screenshots per Design state for UI changes). Required before `approve implement`; see `core/phase-implement.md § Validate Implementation Command` |
| `validate implementation --mode quality` | Read-only audit: does the current code scope meet coding / security / devsecops / architecture standards plus repo / maintainability rules? Required before `approve implement`; see `core/phase-implement.md § Validate Implementation Command` |

For architecture commands, `arch` and `architecture` are equivalent.

`validate *` is the only AI audit command family. There is no separate `review [phase]` command. Validate commands are user-invoked, produce structured reports, and write or update one active validate file per command in `docs/sprint-v{X}/tempo/in-progress/`. `validate changes` is an aggregate convenience command, not a separate audit surface: it runs the required underlying `validate [phase]` command(s) for the selected pack cycle and writes those command-owned active files. `approve *` and `approve changes` require those active files to already be clean, then re-run the required validate command(s) in console-only mode before deciding whether to lock APPROVED.

## Universal Quality Gate For Output-Producing Flows

This gate applies to every flow that creates or revises artifacts: `start [phase]`, `resume` / `continue`, `feedback:`, `start change:`, `import [phase]`, and any downstream delta synthesis.

Rules:

1. Load the relevant template(s) and the shared quality bar in `core/phase-quality-standards.md`. For implementation/code flows, use the approved plan + approved upstream artifacts + repo coding standards + selected task-slice linkage metadata as the "template-equivalent" inputs.
2. Generate or revise the target artifact(s).
3. Re-audit every touched `DRAFT` / delta against both the template and the shared quality standard **before** saving or showing it.
4. Proactively fix every below-quality issue that can be resolved without new human input.
5. If human input is still required, keep the artifact `DRAFT` and capture the gap explicitly in `## Open Issues` (or a change-pack blocker note). Never silently lower quality to "get something out".
6. Only describe an artifact as review-ready when no preventable below-quality item remains.
7. For `validate *`, use the same shared quality standard in read-only mode, order findings from approval-blocking to minor, and grade each finding as `blocker`, `warn`, or `info`.

## Same-Sprint Change Routing

`start change:` is not a normal document phase. It opens a same-sprint change pack managed by `core/change-manager.md` and propagated by `core/change-propagation.md`.

Rules:

1. Use `start change:` only when the source artifact is already `APPROVED` in the current open sprint.
2. If the source artifact is still `DRAFT`, route to `feedback:` on that draft instead.
3. A change pack starts from the earliest affected phase and moves forward only.
4. If the next downstream phase has not started, propagation stops there.
5. If the next downstream phase is `DRAFT`, merge via `feedback:` into that draft.
6. If the next downstream phase is `APPROVED`, create a delta for it if impacted.
7. Multiple DRAFT change packs may coexist across branches or sprints; `status` must list them.
8. If the selected pack is the only plausible active target, `resume`, `feedback:`, `validate changes`, and `approve changes` act on it. If more than one pack matches, or the request could also apply to another unrelated active target, ask the user to choose by sprint, pack id, or slug.
9. `approve changes` approves everything generated in the selected pack up to the current downstream phase.
10. Any impacted downstream approval or closure is blocked until the change has been absorbed at the nearest required downstream phase.

## Feedback Target Resolution

`feedback:` must resolve to exactly one active target.

Possible active targets:

- a selected DRAFT change pack
- a DRAFT phase / lane in any running sprint
- the current implementation lane in the active session

Resolution order:

1. If the user names a target explicitly, use it. Accept forms such as `feedback implement: ...`, `feedback plan: ...`, `feedback sprint-v2 product: ...`, `feedback v1.3.8: ...`, or `feedback fix-payment: ...`.
2. If the current session already has one selected target and no unrelated active target is equally plausible, reuse that target.
3. If there is exactly one plausible active target in scope, use it automatically.
4. If the feedback could reasonably affect two or more unrelated targets, ask the user to choose. Examples: `test` vs `implement`, code vs `product`, or a change pack vs a new-sprint draft.
5. `validate changes` and `approve changes` only target change packs. `feedback:` may target a change pack, a phase draft, or the current implementation lane.
6. Do not guess.

## New Sprint Guard

`new sprint` can open a new sprint before the current sprint is fully complete. Multi-sprint behavior is governed by `core/sprint-manager.md`.

Rules:

1. Allow it when the **latest open sprint** has product + design `APPROVED` and no DRAFT change pack remains open there. Plan, test, and implement do not need to be approved.
2. Refuse it if any DRAFT change pack is still open in the latest sprint.
3. If the more restrictive old condition (all phases approved) is met, `new sprint` also still works as before.
4. Do not rewrite previous-sprint document statuses when creating the next sprint.
5. Create the next sprint folder, then make that sprint active for product/design/arch work.
6. No changelog file is created at sprint creation. Cross-sprint deltas live inside split proposal files (`## New` / `## Updated` / `## Removed` sections) plus `sprint-brief-v{X}.md` where present; `seal_sprint.py` merges proposals into Living Truth at `approve implement`.
7. Freedom mode: `new sprint` only creates a new folder. No trigger check, no plan gate. Changelog stays optional per `core/freedom-router.md § F9`.

## Gate Dependency Matrix

Before starting or approving a gated action, check prerequisites:

| Target Action | Requirement | Additional Validate Gate | Additional Cross-Sprint Gate |
|---|---|---|---|
| product (`start`) | _(none — entry point)_ | — | — |
| product (`approve`) | story readiness (`PROD-1`), open-risk (`PROD-2`), lifecycle-state (`PROD-3`), and Product Traceability Map (`PROD-4`) rules satisfied | active `validate user story` file is present, fresh, clean, and approval-time re-run finds no new gaps | `python .prism/core/tools/validate_proposal.py --file <each product proposal>` returns 0 blockers |
| design (`start`) | Product work exists in the current sprint (`DRAFT` or `APPROVED`) | — | — |
| design (`approve`) | product APPROVED + implementation-ready + test-observable rules satisfied | active `validate design` file is present, fresh, clean, approval-time re-run finds no new gaps, and `python .prism/core/tools/validate_proposal.py --file docs/sprint-v{X}/design/proposals/design-system-v{X}.md` returns 0 blockers | — |
| architecture (`start`) | product APPROVED | — | — |
| architecture (`approve`) | product APPROVED + planning-ready architecture rule (`ARCH-1`) satisfied, including C4 text-readable summary + Draw.io/XML coverage for all 3 required levels (System Context, Container, Component), plus at least 1 DFD Draw.io/XML source, coverage for meaningful data flows, and user group split coverage when flows materially differ (`ARCH-2`) | active `validate architecture` file is present, fresh, clean, approval-time re-run finds no new gaps across all 3 layers, and `python .prism/core/tools/validate_proposal.py --file <each architecture proposal>` returns 0 blockers | — |
| plan (`start`) | product + design + architecture | — | All previous sprints must be `sealed` |
| plan (`approve`) | product + design + architecture APPROVED, plus Delivery Traceability Index (`PLAN-1`), full task-group field set (`PLAN-2`) including `Feature References`, `Tracking IDs`, `target_modules_packages`, `public_entrypoints_impacted`, `inherited_architecture_obligations`, `allowed_diff_boundary`, `affected_code_surfaces`, `code_ownership_zones`, `shared_foundation_guard`, `blocks`, `blocked_by`, `qa_test_refs`, `repo_test_delta_target`, `review_mode`, `validation commands to run`, and `AI context fit`, concrete external QA readiness when external QC applies, every task group ≤ 3 days and one high-quality AI context window, and `PLAN-3` lanes / Task-Group Dependency Graph when `team_size > 1` | active `validate plan` file is present, fresh, clean, and approval-time re-run finds no new gaps | All previous sprints must be `sealed` |
| test (`start`) | product + design + architecture | — | All previous sprints must be `sealed` |
| test (`approve`) | product + design + architecture APPROVED + `TEST-1`, `TEST-2`, `TEST-3`, `TEST-3b`, `TEST-4`, `TEST-5`, `TEST-6`, `TEST-7`, and `TEST-8` satisfied, including `TEST-2` execution-ready + implementation-consumable handoff, `TEST-3b` trace + Technique title-prefix discipline, and `TEST-8` generated TSV exports | active `validate test` file is present, fresh, clean, approval-time re-run finds no new gaps, and `python .prism/core/tools/validate_proposal.py --file docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md` returns 0 blockers | All previous sprints must be `sealed` |
| implement (`start`) | plan | — | All previous sprints must be `sealed` |
| implement (`approve`) | test APPROVED + implemented task groups satisfy applicable code rules, including `CODE-10` local Docker Compose self-test path for runtime scopes | active `validate implementation --mode spec` AND `--mode quality` files are both present, fresh, clean, and both approval-time re-runs find no new gaps | — |

**Gate check procedure:**
1. Read the current-sprint files for the target phase and its upstream prerequisites.
2. Parse YAML frontmatter for `status`.
3. For `start design`:
  - if no Product artifact exists in the current sprint → block and tell the user to `start product` or `import product` first
  - if Product exists but is still `DRAFT` → allow `start design`, but the resulting Design draft MUST carry `dependencies_pending: [product]` and inline `PENDING` validation markers for Product-dependent assumptions
4. For all other actions above that require APPROVED prerequisites, if any prerequisite status ≠ `APPROVED` → inform user which gate is blocking.
5. For plan / test / implement start or approve: read `prism-config.md` `sprints` array. If any previous sprint has `sealed: false`, block with the message in `core/sprint-manager.md § Plan Gate`.
6. `test` is an independent QA lane. `approve test` does not block `start implement`.
7. `approve design` requires Product to be `APPROVED`. If Design still carries `dependencies_pending: [product]` or unresolved Product-validation `PENDING` markers, block and require the Pending Validation Checklist to be cleared first.
8. `approve implement` requires `test` to be APPROVED. If test is still DRAFT or missing, block with the message defined in `core/phase-implement.md § Gate`. Each sprint has exactly one implementation pass: `approve plan` opens it; `approve implement` closes it and seals the sprint. On success, also trigger sprint seal per `core/sprint-manager.md`.
9. `start plan` generates only `implementation-plan-v{X}.md`.
10. `start change:` can open immediately after the source phase is `APPROVED`; it does not use the normal phase gate matrix.
11. If a selected DRAFT change pack impacts the target phase, that phase cannot be approved or closed until the change has been absorbed at the nearest required downstream phase.
12. For every phase approval, `approve [phase]` uses the required active validate file(s) in `tempo/in-progress` and refuses to begin if:
  - the required active validate file is missing for the current DRAFT / code scope, OR
  - the active validate file is stale (artifact/code scope changed since the explicit validate run), OR
  - the latest explicit validate result in that active file still has `blocker`-level findings.
  For `approve implement` specifically, the gate requires BOTH `--mode spec` AND `--mode quality` active files to satisfy the conditions above. Running only one is not sufficient. See `Tempo Working Files` and `Validate Active Files` below.
13. For every deliverable proposal phase (product / design / architecture / testing), the phase validate command MUST run `validate_proposal.py` on each mergeable proposal file before reporting `clean`. Proposal validation blockers (missing anchors, malformed frontmatter, wrong split-target prefix, unknown top-level merge sections, or unmergeable anchored-block structure) block `approve [phase]`; do not defer these to sprint seal.

## Tempo Working Files

Every sprint contains auxiliary working files under:

```
docs/sprint-v{X}/tempo/in-progress/
docs/sprint-v{X}/tempo/completed/
```

Rules:

- `tempo/` is for auxiliary working files only: discuss notes, analysis notes, validate files, and other non-canonical working material.
- Official phase artifacts remain in their phase folders and never move into `tempo/`.
- `tempo/completed/` is immutable and ignored by orchestration after closure: never auto-load it, never use it for gates, never use it for resume, and never use it as effective truth.
- Create or update a `tempo/in-progress` file when the interaction is long-running, multi-turn, multi-item, requires checklist/status tracking, or the user explicitly asks for a file.
- Do not create a file for small discussions, small edits, or quick clarification turns unless the user explicitly asks for one.
- A `tempo/in-progress` working file may become the active target for the current discussion when the conversation is explicitly about that note/checklist; otherwise, do not let `tempo/` compete with normal phase routing.

## Phase Folder Map

Use this canonical map for every save, import, asset copy, resume scan, and status reference. The frontmatter `phase` value is a logical phase name; it is not always the folder name.

| Logical phase / command | Frontmatter `phase` | Sprint folder |
|---|---|---|
| Product | `product` | `docs/sprint-v{X}/product/` |
| Design | `design` | `docs/sprint-v{X}/design/` |
| Architecture / `arch` | `architecture` | `docs/sprint-v{X}/architecture/` |
| Plan | `plan` | `docs/sprint-v{X}/planning/` |
| Test plan | `test` | `docs/sprint-v{X}/testing/` |
| Testing proposal / testing delta | `testing` | `docs/sprint-v{X}/testing/` |
| Implement | `implement` | no versioned phase document; code/session lane plus validate files in `tempo/in-progress/` |

Rules:

- Never derive folder names by lowercasing the command or frontmatter phase. In particular, Plan uses `planning/` and Test uses `testing/`.
- Asset folders copy into the mapped phase folder's `assets/` subdirectory.
- Change packs always live in `docs/sprint-v{X}/changes/`; auxiliary working files always live in `docs/sprint-v{X}/tempo/`.

## Validate Active Files

`validate *` commands are user-invoked and remain mandatory before approval. Generation-time quality also remains mandatory: phase engines must self-apply validate-equivalent checks while producing output, so explicit validate is not the first quality pass. `review [phase]` is retired; if the user asks to review or audit a phase, normalize that request to the matching `validate *` command.

### Naming And Cycle

Each validate command owns exactly one active file at a time per cycle. The filename follows:

```
validate-<command>-<cycle>.md
```

Where:

- `<command>` is the validate command slug, one of: `user-story`, `design`, `architecture`, `plan`, `test`, `implementation-spec`, `implementation-quality`.
- `<cycle>` is `base` for the sprint's initial approval cycle, or `pack-<slug>` for a specific change pack (slug matches the change-pack folder name).

Examples:

- `validate-user-story-base.md` — base Product approval cycle
- `validate-architecture-pack-fix-payment.md` — change pack `fix-payment` validating Architecture
- `validate-implementation-spec-base.md` and `validate-implementation-quality-base.md` — both modes for base Implement approval

### Lifecycle

1. **Mutable while running** — the active file lives in `docs/sprint-v{X}/tempo/in-progress/`. Each `validate *` run on the same cycle writes or updates this single file (overwrite allowed within the cycle).
2. **Sealed on approval success** — when `approve [phase]` (base cycle) or `approve changes` (pack cycle) succeeds for the cycle, the engine MUST:
   - add YAML frontmatter `status: APPROVED`, `approved_at: <UTC ISO timestamp>`, `cycle: base | pack-<slug>` to the file
   - move the file from `tempo/in-progress/` to `tempo/completed/` keeping the same filename
   - for `approve changes`, seal every required active validate file for every impacted phase in that pack cycle
3. **Immutable in completed** — a file under `tempo/completed/` MUST NOT be overwritten or deleted by AI for any reason. It is the audit record for the approval that consumed it.
4. **New cycle = new file** — starting a change pack on a previously approved phase opens a new cycle (`pack-<slug>`) and creates a new file in `tempo/in-progress/`. The previously sealed file (e.g. `<command>-base.md` or an earlier `pack-<other-slug>.md`) in `tempo/completed/` remains untouched.

### Active File Contents

For each explicit `validate *` run, write or update the active file in `tempo/in-progress/` with at least:

- command
- target fingerprint
- timestamp (UTC)
- `blocker` / `warn` / `info` counts
- structural coverage against the source template / expected output sections (`DOC-3`)
- rule coverage by Rule ID, including phase-specific rules and shared rules such as `DOC-*`, `LINK-*`, `ORB-*`, `CODE-*`
- structured findings report
- latest conclusion (`clean` or `issues-found`)

`target fingerprint` means the validated scope plus a deterministic freshness marker.

Latest conclusion semantics:

- `clean` is allowed only when `blocker: 0` and every required structural / rule coverage check for the validate command is explicitly present.
- `issues-found` is mandatory when any `blocker` exists, when `DOC-3` / Rule Coverage evidence is missing, or when a phase-specific hard rule is missing required coverage.
- A validate run MUST NOT report `clean`, `pass`, or approval-ready while it has unresolved blocker findings. That active validate file fails the approval gate.

Recommended active validate file shape:

```markdown
# Validate <command> — <cycle>

## 1. Target
- Command:
- Target files / code scope:
- Target fingerprint:
- Timestamp (UTC):

## 2. Structural Coverage (`DOC-3`)
| Artifact | Source template / expected contract | Required sections / fields checked | Missing | N/A with reason |
|---|---|---|---|---|

## 3. Rule Coverage (`VAL-1`)
| Rule ID | Scope checked | Result | Notes |
|---|---|---|---|

## 4. Findings
| Severity | Rule ID | Location | Finding | Required fix |
|---|---|---|---|---|

## 5. Conclusion
- blocker:
- warn:
- info:
- latest conclusion: `clean` | `issues-found`
```

Missing `DOC-3` structural coverage or Rule Coverage in an active validate file is itself a `blocker [VAL-1]` for approval because the approval gate cannot prove which output sections and rules were audited.

### Target Fingerprint Algorithm

For Product / Design / Architecture / Plan / Test:

1. Resolve the exact file set for the validate command using the Phase Folder Map and the phase package contract. Exclude `tempo/**`, `changes/**`, and binary `assets/**` unless the validate command explicitly audits an asset manifest.
2. Sort file paths lexicographically by POSIX-style sprint-relative path.
3. For each file, read UTF-8 text, normalize CRLF to LF, and ensure the hash input ends with one newline. Include YAML frontmatter; do not strip whitespace, comments, placeholders, or status fields.
4. Build the hash input as repeated blocks:

  ```text
  ---FILE docs/sprint-v{X}/phase-folder/name-v{X}.md---
  [normalized file content]
  ---END FILE---
  ```

5. `target fingerprint` records the sorted file list and the first 12 characters of `sha256` over the full hash input.

For Implement:

1. Record the task-group reference, selected `affected_code_surfaces`, current `HEAD` SHA from `git rev-parse HEAD`, and the explicit diff base used for the audit.
2. Hash the implementation delta as the first 12 characters of `sha256` over:
  - `git diff --binary <diff-base> -- <affected_code_surfaces>`
  - plus sorted untracked files under `<affected_code_surfaces>` with the same `---FILE ...---` block format above.
3. If git metadata is unavailable, record `git: unavailable` and use the Product / Design / Architecture / Plan / Test file-hash algorithm over the resolved affected code surfaces instead.
4. The Implement fingerprint is fresh only when task-group reference, affected surfaces, `HEAD`, diff base, sorted changed-file list, and delta hash all still match.

An active validate file is stale when:

- its stored `target fingerprint` no longer matches the current scope fingerprint, OR
- a `feedback:`, `import [phase]`, or change-pack absorption has occurred since the explicit validate run, OR
- for Implement, the underlying code diff has advanced since the recorded commit / diff base

## Approval-Time Validate Re-Run

When the user types `approve [phase]`, the gate first checks the required active validate file(s). If they are present, clean, and not stale, `approve` then re-runs the required validate command(s) in console-only mode as a final full confirmation pass.

Rules:

1. Product / Design / Architecture / Plan / Test: re-run the single required validate command.
2. Implement: re-run BOTH `--mode spec` and `--mode quality`.
3. If the approval-time re-run is clean, proceed with the normal approval flow.
4. If the approval-time re-run finds any blocker or material gap, do not approve.
5. On such a failure, show the new findings in console first and ask the user whether they want to write/update the corresponding active validate file(s) in `tempo/in-progress` as the next follow-up checklist.
6. Do not write those new approval-time findings to file automatically on failure.

### Refusal message templates

Missing or stale validate result:

```text
⚠ Cannot approve [phase] — validate result is missing or stale.
→ Required: [command]
→ Active validate file: [path or "missing"]
→ Last explicit validate run: [timestamp or "never"]
→ Stale because: [hash mismatch | feedback applied | code advanced | not run]
→ Run [command] on the current DRAFT, then approve [phase].
```

Validate result still has blockers:

```text
⚠ Cannot approve [phase] — validate result still has blockers.
→ Required: [command]
→ Active validate file: [path]
→ Last explicit validate run: [timestamp]
→ Blockers: [N]
→ Resolve blockers via feedback:, then re-run [command], then approve [phase].
```

Approval-time re-run found new gaps:

```text
⚠ Cannot approve [phase] — approval-time validate re-run found new gaps.
→ Required: [command]
→ Active validate file: [path]
→ New findings: [summary]
→ Nothing has been written yet.
→ Do you want PRISM to update the active validate file with these findings as a checklist?
```

For `approve implement`, list both modes' status side by side so the user sees exactly which mode is missing or has blockers.

## Context Loading Rules

Load ONLY what the current phase needs. Never load the entire `/docs` folder.

After selecting the eligible documents below, apply `core/context-strategy.md` to decide whether they should be loaded in full, summarized, or split by domain.

Product package (2-tier model): the active sprint's mergeable output is split under `docs/sprint-v{X}/product/proposals/` by Living Truth target. Anchors route by ID prefix: BR (+ the singleton `PRD-OVERVIEW-001` narrative) → `/docs/product/prd.md`; GLOSS / PERSONA / MR → their product LT files; EP creates `/docs/product/epics/EP-NNN-{slug}.md`; FR / US route with `<!-- EPIC: EP-XXX -->`; AC routes with `<!-- US: US-XXX -->` and is appended inside that US block. Each EP block must include the `PROD-4` Product Traceability Map (`EP -> FR -> related US`). AI loads the **product effective truth** for downstream phases via `effective_truth.py --phase product --up-to-sprint v{X}`.

| Active Phase | Required Context | Optional | NEVER Load |
|---|---|---|---|
| product | `prism-config.md` | previous Product package (if new sprint) | design, arch, impl, test |
| design | current Product package in the active sprint (APPROVED effective truth if approved, otherwise latest DRAFT working package) | `/docs/design/design-system.md` (Living Truth from prior sealed sprints), `prism-config.md` | arch, impl, test |
| architecture | Product package APPROVED | previous architecture package including `project-reference` when present, `prism-config.md` | impl, test |
| plan | Product package, `design`, `architecture`, `project-reference`, `erd`, `api-specs`, `nfr` APPROVED | `sequence`, `adr`, `data-flow`, `events`, `test-plan`, `test-cases`, `prism-config.md`, `implementation-plan-v{X-1}.md` | code outputs |
| test | Product package, `design`, `architecture`, `project-reference`, `api-specs`, `nfr` APPROVED | `sequence`, `erd`, `data-flow`, `events`, `implementation-plan`, `prism-config.md` | code outputs |
| implement | `implementation-plan`, Product package, `design`, `architecture`, `project-reference`, `sequence`, `erd`, `api-specs`, `nfr` APPROVED, plus applicable standards resolved via `<paths.standards>/INDEX.md` (`paths.standards` from `prism.json`, default `.prism/core/standards`) | `adr`, `data-flow`, `events`, `test-plan`, `test-cases`, `prism-config.md` | unrelated sprint drafts |
| change (selected pack) | source artifact, current downstream artifacts, approved packs affecting them, `prism-config.md`, selected `change-request.md`, selected `impact-matrix.md` | previous approved packs for the same artifact | unrelated DRAFT packs in other sprints, unrelated future-phase drafts |

Additional tempo rules:

- Never auto-load `tempo/completed/**`.
- Load `tempo/in-progress/**` only when it is the explicit active target for the current discussion/checklist, or when `approve *` / `validate *` needs the active validate file(s).

If Design starts from a Product draft, carry the Product dependency forward in Design via `dependencies_pending: [product]` and inline `PENDING` validation markers until Product is approved and Design is re-validated.

**Context overflow protection:**
- If context exceeds 60% of window → warn user and propose fitting strategy
- NEVER truncate information without asking user first
- See `context-strategy.md` for size-specific handling

## Recency Metadata Contract

- `created` is set once when a document is first written or first imported.
- `updated` is the primary recency field and MUST be refreshed on every write, revision, import save, and auto-save.
- If one user action writes multiple files in the same lane, stamp that file set with the same `updated` timestamp.
- On `status` or `resume`, if a file is missing `updated` or the value is malformed, warn briefly, fall back to the file's modified timestamp for that turn, and normalize the frontmatter on the next write.

## State Detection

To determine current project state on `resume` or session start:

1. Find the highest sprint number in `/docs/sprint-v{X}/`
2. Scan all documents in that sprint for their `status` and `updated` frontmatter
3. Use `updated` as the primary recency field. If it is missing or invalid, fall back to the file's modified timestamp for this turn and tell the user it will be normalized on the next write
4. Scan all sprints for change packs whose `change-request.md` is `DRAFT`
5. If exactly one DRAFT change pack exists in scope, treat that pack as the highest-priority active work only when no unrelated active target from the current session plausibly competes with it
6. If multiple DRAFT change packs exist and the request is `status`, list them all without blocking
7. If multiple plausible active targets exist and the request is `resume`, ask the user to choose one unless the command already names a sprint, id prefix, slug, or phase / lane
8. Otherwise, identify the most recently updated phase with `DRAFT` status → that's where work continues
9. If multiple phases tie on `updated` within the same lane, prefer the later-stage document in that lane
10. If multiple phases tie on `updated` across independent lanes (e.g. `plan` and `test`), present a compact resume-choice block that shows lane, related files, last updated timestamp, current status, and exact reply options
11. If the latest sprint has product + design `APPROVED` and no DRAFT change pack remains open there → inform user sprint is ready for `new sprint`; if architecture and plan are also `APPROVED`, mention `start implement` too

Implementation work is session-scoped rather than file-scoped. If the current chat is clearly mid-implementation, treat `implement` as another plausible target for `feedback:` even when file-layer recency would otherwise point to a document draft.

When step 7 applies, use this format:
```
Multiple DRAFT change packs found:

sprint-v1 / v1.3.8-fix-payment
  earliest: product
  downstream: architecture

sprint-v2 / v2.7.2-new-auth
  earliest: architecture
  downstream: test

Reply with:
- resume v1.3.8
- resume fix-payment
- resume in sprint-v1
- or describe another task
```

When step 10 applies, use this format:
```
Multiple active DRAFT lanes found in sprint-v{X}:

1. plan
  files: implementation-plan-v{X}.md
  updated: YYYY-MM-DD HH:MM
  status: DRAFT

2. test
  files: test-plan-v{X}.md, proposals/test-cases-v{X}.md
  updated: YYYY-MM-DD HH:MM
  status: DRAFT

Reply with:
- resume plan
- continue plan
- resume test
- continue test
- or describe another task
```

Do not ask the user to choose when the tie is only between files inside the same phase/lane; in that case, prefer the later-stage document automatically.

**Note on `start implement`**: This phase produces code, not documents. If the user is mid-implementation, `resume` will find all phases `APPROVED` (correct state) and report the sprint is ready for `start implement`. The user selects which plan phase/task group to continue from.

## Status Output

On `status`, render the canonical block defined in `core/status-format.md`.

Additional rules:
1. `status` never blocks because multiple DRAFT change packs or multiple active targets exist; it is the discovery tool the user uses to choose one.
2. For every started phase / lane, include a `files:` line in the canonical location and order defined by `core/status-format.md`.
3. For every DRAFT change pack, include `earliest`, `downstream`, `phases`, `files`, and `blockers` in the canonical field order defined by `core/status-format.md`.
4. For any DRAFT that contains `dependencies_pending` in frontmatter:
  - if listed prerequisite phases are still not APPROVED → show `waiting on: [phases]`
  - if all listed prerequisite phases are now APPROVED → show `follow-up: pending validation checklist required before approve`
5. Sprint labels, blocked-lane wording, drift-warning placement, started-lane `files:` lines, change-pack `phases:` / `files:` lines, and the final `next:` suggestion must follow `core/status-format.md` exactly.

## Unified Validate Flow

`validate *` is the only AI audit command family in Guided mode. The old `review [phase]` command is retired to avoid two overlapping audit surfaces. If the user types `review product`, `review design`, `review arch`, `review plan`, `review test`, or `review implement`, normalize the request to the matching validate command and state that normalization in one short line.

### Command Mapping

| User asks for | Normalize to |
|---|---|
| `review product`, `validate product`, `audit user stories` | `validate user story` |
| `review design`, `audit design` | `validate design` |
| `review arch`, `review architecture`, `audit architecture` | `validate architecture` |
| `review plan`, `audit plan` | `validate plan` |
| `review test`, `audit test` | `validate test` |
| `review implement`, `audit code against spec` | `validate implementation --mode spec` |
| `code quality review`, `audit code quality` | `validate implementation --mode quality` |
| `review changes`, `audit change pack`, `validate change [pack-id|slug]` | `validate changes [pack-id|slug]` |

If `review implement` is ambiguous between spec correctness and code quality, prefer `validate implementation --mode spec` first and tell the user to run `validate implementation --mode quality` after spec is clean. Do not run both silently unless the user explicitly asks for both.

### Change Pack Aggregate

`validate changes [pack-id|slug]` is a read-only aggregate command for DRAFT change packs. It does not create `validate-changes-*.md`. It resolves exactly one change pack, derives the impacted phases from `change-request.md`, `impact-matrix.md`, generated delta files, and the current downstream phase, then runs the existing validate commands for that pack cycle.

The validation target is the selected pack's proposed truth, not the frozen base artifact alone: `base artifact + all APPROVED deltas for that artifact + the selected DRAFT pack delta`. Exclude DRAFT deltas from every other pack. If the selected pack changes Product from `1+2=3` to `1+2=4`, then every underlying validate command in that pack cycle checks consistency against `1+2=4`.

| Impacted scope | Required validate command |
|---|---|
| Product delta / Product DRAFT absorption | `validate user story` |
| Design delta / Design DRAFT absorption | `validate design` |
| Architecture delta / Architecture DRAFT absorption | `validate architecture` |
| Plan delta / Plan DRAFT absorption | `validate plan` |
| Test delta / Test DRAFT absorption | `validate test` |
| Implement code scope affected by the pack | `validate implementation --mode spec` and `validate implementation --mode quality` |

For every command above, the cycle is `pack-<slug>` and the active file uses the normal naming contract, for example `validate-design-pack-fix-payment.md`. The target fingerprint MUST include the selected pack id / slug, `change-request.md`, `impact-matrix.md`, the generated delta file(s) for that impacted phase, any downstream DRAFT artifact that absorbed the pack, and the effective-truth base inputs used to apply the selected DRAFT delta. If the pack impacts multiple phases, run all required phase validates and return one combined summary.

If more than one DRAFT change pack is plausible, ask the user to choose by sprint, pack id, id prefix, or slug before auditing. Do not validate an arbitrary pack.

### Process

1. Read the current DRAFT / code scope for the target validate command.
2. Evaluate against the shared phase quality standard in `core/phase-quality-standards.md` and the phase-specific validate command definition.
3. If an `## Open Issues` section exists in a DRAFT, surface all `open` rows at the top of the validate output; they must be closed before `approve [phase]`.
4. Output a structured `blocker` / `warn` / `info` report and write or update the command's active validate file in `docs/sprint-v{X}/tempo/in-progress/`.
5. Do not modify phase artifacts or code during validate. Fixes happen through `feedback:` or a new implementation pass.

For `validate changes`, repeat this process for each underlying phase command identified above, then output an aggregate result ordered by severity and phase order. The pack is clean only when every required underlying validate result is clean and fresh.

### Output Shape

```text
validate design: docs/sprint-v1/design/proposals/design-system-v1.md
blocker: 1
warn: 2
info: 0

Findings:
- blocker: FR-014 has no Error state with exact copy, so Test cannot write executable cases.
- warn: Empty state for SCR-003 lacks a stable QA-visible identifier.

Active validate file updated:
docs/sprint-v1/tempo/in-progress/validate-design-base.md

Next:
→ feedback design: [fix blockers]
→ validate design
→ approve design
```

### Key Rules

- **Single audit surface**: use `validate *`; do not expose `review [phase]` as a command.
- **Read-only during validate**: never edit files or code while running a validate command.
- **Persisted result**: every validate command updates exactly one active validate file.
- **Approval gate**: every `approve [phase]` checks the required active validate file(s), then re-runs validate in console-only mode before approving.
- **Implement has two required audits**: `validate implementation --mode spec` and `validate implementation --mode quality`; both are required before `approve implement`.

## Post-Output Behavior

After completing any phase output:

1. **Write to file** — save to the mapped phase folder from `Phase Folder Map` before presenting anything and refresh its `updated` timestamp
2. If one action writes multiple files in the same lane, stamp that file set with the same `updated` value
3. **Confirm** — one line: what file was written, status set to DRAFT
4. **Suggest next actions** — always append this block:

```
→ [filename] written. When ready:
  • [validate user story | validate design | validate architecture | validate plan | validate test | validate implementation --mode spec | validate implementation --mode quality]
                                         — required audit before approve
  • approve [phase]                      — mark APPROVED, open gates to: [list next phases]
  • feedback: [your changes]             — revise and stay DRAFT
  • feedback: [changes], approve [phase] — apply changes → show diff → approve if the change is small and safe; otherwise ask again
```

The corresponding validate line(s) MUST appear in the suggestion block for every phase. If the user requests `approve [phase]` while the validate gate is unsatisfied, refuse with the message templates in `Validate Active Files § Refusal message templates`.

**Feedback + approve combo rule**: Parse feedback → apply changes → output a brief diff summary ("Changed: X, Y, Z") → mark APPROVED only when the change is small and safe; otherwise ask for confirmation before approval. User sees what changed before anything locks.

Use this heuristic before auto-approving:
- **Small / safe changes**: wording cleanups, local renames, traceability renumbering, one missing field, one localized correction in one document → apply, show diff summary, approve in one pass
- **Large / risky changes**: new scope, contract changes, multi-file architecture changes, new compliance/security assumptions, or broad restructuring → apply changes, summarize, then ask for confirmation before approval

**After `approve [phase]`**: Confirm APPROVED, then immediately state which gates are now open:
```
✓ [phase] APPROVED.
→ Gates now open: [phase-a], [phase-b]   ← or "start implement" if plan was the gate
→ Other: describe what you'd like to do instead
```

For `approve test`: confirm APPROVED, then note that `approve implement` is now unblocked (if plan is also approved and implementation is in progress).

For `approve implement`: before closing, verify `test` is APPROVED. If not, block per `core/phase-implement.md § Gate`. If test is APPROVED, confirm the current implementation pass is accepted, then suggest the next practical action — run validation / release steps, check status, or start a new sprint if scope changes are needed.

## Approval Guard For Pending Dependencies

Before approving a DRAFT, inspect its YAML frontmatter for `dependencies_pending`.

If the field is absent or empty, use the normal approval flow.

If `dependencies_pending` exists:

1. Read the listed prerequisite phases in the current sprint
2. If any listed phase is not APPROVED, refuse approval with:

```text
⚠ Cannot approve [phase] yet.
→ Pending prerequisite approvals: [phase-a], [phase-b]
→ Complete or import those phases first, then return to this draft
→ Other: describe what you'd like to do
```

3. If all listed phases are APPROVED but the draft still contains `<!-- PENDING: ... -->` markers or unresolved soft-gate assumptions, do not approve yet. Generate a Pending Validation Checklist that:

  - enumerates each `<!-- PENDING: ... -->` marker
  - includes the nearest section heading or file context
  - states which approved prerequisite or input it must be validated against

```text
⚠ [phase] still contains assumptions created before its prerequisite gates were approved.
→ Pending Validation Checklist:
  1. [section or file context] — [PENDING text]
    validate against: [approved phase/input]
→ Recommended: feedback: validate the pending checklist against the approved inputs
→ Or: validate [phase]
→ After all checklist items are resolved and the PENDING markers are removed, approve [phase]
```

4. Only approve after the listed prerequisite phases are APPROVED and the pending-assumption markers have been cleared from the draft

This guard primarily protects drafts created before prerequisite approvals were cleared, but it applies whenever the field exists.

## Approval Guard For Open Issues

Before approving any DRAFT, check whether it contains an `## Open Issues` section.

If the section is absent, or all rows have `status: closed`, proceed with normal approval.

If any row has `status: open`, block approval:

```text
⚠ Cannot approve [phase] — the DRAFT has open issues that must be resolved first.
→ Open issues:
  - OI-001: [summary]
  - OI-002: [summary]
→ Resolve each item (feedback: [answer] or discuss with PRISM), then approve [phase].
→ Other: describe what you’d like to do
```

This guard applies in guided mode. In freedom mode there is no approval gate, so this guard does not apply.

## Approval Guard For Validate Result

This guard applies to every phase approval and to `approve changes`. Product uses `validate user story`; Design uses `validate design`; Architecture uses `validate architecture`; Plan uses `validate plan`; Test uses `validate test`; Implement uses BOTH `validate implementation --mode spec` AND `validate implementation --mode quality`. `approve changes` uses the same command set that `validate changes [pack-id|slug]` derives for the selected pack cycle.

Before approving any DRAFT in those phases, read the active validate file(s) in `tempo/in-progress` and check the latest explicit result(s) for the required validate command(s).

For Product / Design / Architecture / Plan / Test (single required command):

1. If no active validate file exists for the required command on the current DRAFT, refuse with the "missing or stale" template in `Validate Active Files § Refusal message templates`.
2. If the latest explicit validate result in that file is stale per the Staleness rule, refuse with the same template and the staleness reason filled in.
3. If `blocker` count > 0 in the latest row, refuse with the "still has blockers" template.
4. Otherwise, re-run the required validate command in console-only mode.
5. If that approval-time re-run is clean, proceed with the normal approval flow (which still also checks Pending Dependencies and Open Issues).
6. If that approval-time re-run finds new gaps, refuse with the "approval-time re-run found new gaps" template and ask whether PRISM should update the active validate file.

For Implement (two required modes):

1. Apply the same checks for `--mode spec`.
2. Apply the same checks for `--mode quality`.
3. Both must satisfy all checks. Running only one is not sufficient.
4. If both baseline files are valid, re-run BOTH modes in console-only mode before approval.
5. The refusal message must show the status of BOTH modes side by side so the user sees exactly which mode is missing, stale, still has blockers, or found new approval-time gaps.

For `approve changes`:

1. Resolve exactly one DRAFT change pack.
2. Derive the required underlying validate commands using `Unified Validate Flow § Change Pack Aggregate`.
3. For each required command, require the active `validate-<command>-pack-<slug>.md` file to exist, be fresh, include `VAL-1` evidence, and have zero blockers.
4. Re-run every required command in console-only mode against the selected pack cycle.
5. If all re-runs are clean, proceed with normal `approve changes` closure and seal every consumed pack-cycle validate file.
6. If any required command is missing, stale, blocked, or finds approval-time gaps, refuse and show the per-phase status so the user knows whether to run `validate changes [pack-id|slug]` or targeted `validate [phase]`.

This guard applies in guided mode. In freedom mode there is no approval gate, so this guard does not apply.

On `feedback: [content]`:

1. Parse feedback content (supports Confluence comment paste)
2. Resolve exactly one target using `Feedback Target Resolution`
3. If the resolved target is a selected or explicit DRAFT change pack, apply feedback to that pack and any downstream draft that must absorb the change
4. If the resolved target is a phase draft, map feedback items to the relevant sections in that draft
5. If the resolved target is the current implementation lane, apply feedback only to the active code-execution scope for this session and preserve or update feature-linkage markers on touched APIs / business-facing code
6. Apply changes → set affected documents back to `DRAFT` when documents are modified
7. Preserve the local numbering / heading / table / ID schema of untouched sibling sections unless a deliberate full-set normalization is required
8. Re-audit every touched draft / delta against its template and the shared phase quality standard in `core/phase-quality-standards.md`; proactively fix any below-quality issue exposed by the edit
9. If a feedback item creates a conflict, ambiguity, or scope question that cannot be resolved in this turn, add a row to the `## Open Issues` section of the affected DRAFT and continue — do not block the save
10. Output updated documents or code for re-check
11. Inform user: "Updated N targets. Continue with feedback, validate, or approve?"

## Refusal Flow For APPROVED Or Non-Active Documents

If the user tries to modify an APPROVED document via `feedback:`, `import [phase]`, or a direct edit request in the current sprint, block with a clear refusal and the next valid step:

```text
⚠ [phase] in sprint-v{X} is APPROVED and frozen as a base artifact.
→ To change it in the current open sprint: start change: [what changed]
→ If the sprint is already sealed: new sprint
→ To inspect differences first: diff [phase]
→ Other: describe what you'd like to do
```

If the user is pointing at an older sprint while a newer sprint is active, state that explicitly and direct the user back to the active sprint instead of editing the older one in place.

## Import Flow

`import [phase]` handles **three sub-cases** — the same command covers all.

### Inbox File Naming Convention

Before running `import [phase]`, the user drops files into `docs/inbox/` using these names:

#### Product — `import product`

| File Name | Maps to Product Output (2-tier model) |
|-----------|------------------------|
| `docs/inbox/product.md` | Fold into `product/proposals/prd-v{X}.md` and epic proposals as needed. NFR items go to `architecture/proposals/nfr-v{X}.md`. |
| `docs/inbox/epics.md` | Fold into `product/proposals/epics/EP-NNN-{slug}-v{X}.md` `## New` (EP-NNN epic file creation + nested FR-NNN with `<!-- EPIC: EP-XXX -->` tag) |
| `docs/inbox/user-stories.md` | Fold into owning epic proposal `## New` (US-NNN items with `<!-- EPIC: EP-XXX -->` routing tag → inside `/docs/product/epics/EP-XXX-{slug}.md`) |
| `docs/inbox/glossary.md` | Fold into `product/proposals/glossary-v{X}.md` as GLOSS-NNN items targeting `/docs/product/glossary.md` at seal |
| `docs/inbox/personas.md` | Fold into `product/proposals/personas-v{X}.md` as PERSONA-NNN items targeting `/docs/product/personas.md` at seal |
| `docs/inbox/market-research.md` | Fold into `product/proposals/market-research-v{X}.md` as MR-NNN items targeting `/docs/product/market-research.md` at seal |
| `docs/inbox/product-assets/` | `assets/` — images, PDFs, research data referenced across the Product package |

#### Design — `import design`

| File Name | Maps to Design Section |
|-----------|----------------------|
| `docs/inbox/design.md` | Primary design specification |
| `docs/inbox/design-system.md` | §1 Design Principles & Brand + §4 UI Components + §5 Design Tokens |
| `docs/inbox/wireframes.md` | §3 Wireframe Descriptions (text annotations for wireframe images) |
| `docs/inbox/user-flows.md` | §2 User Flows |
| `docs/inbox/prototype.md` | Prototype links, interaction specs — referenced in §2 + §3 |
| `docs/inbox/design-assets/` | Figma exports, mockup images, wireframe PNGs — copied to sprint |

#### Architecture — `import arch`

| File Name | Maps to Architecture Output (2-tier model) |
|-----------|---------------------------|
| `docs/inbox/architecture.md` | Fold into `architecture/proposals/architecture-v{X}.md` (ARCH-COMP-NNN / ARCH-NNN items) — overall architecture document, package entrypoint, text-readable C4 summary plus Draw.io/XML references, cross-links to supporting files |
| `docs/inbox/project-reference.md` | Fold into `architecture/proposals/project-reference-v{X}.md` as PR-NNN items targeting `/docs/architecture/project-reference.md` at seal |
| `docs/inbox/sequence.md` | Fold into `architecture/proposals/sequence-v{X}.md` as SEQ-NNN items targeting `/docs/architecture/sequence.md` at seal |
| `docs/inbox/sad.md` | Alias for `architecture/proposals/architecture-v{X}.md` — overall architecture document and package entrypoint |
| `docs/inbox/erd.md` | Fold into `architecture/proposals/erd-v{X}.md` as ENT-NNN items targeting `/docs/architecture/erd.md` at seal |
| `docs/inbox/adr.md` | Fold into `architecture/proposals/adr-v{X}.md` as ADR-NNN items targeting `/docs/architecture/adr.md` at seal |
| `docs/inbox/data-flow.md` | Fold into `architecture/proposals/data-flow-v{X}.md` as FLOW-NNN DFD items targeting `/docs/architecture/data-flow.md` at seal; Draw.io/XML source belongs in `arch-assets/` |
| `docs/inbox/api-specs.md` | Fold into `architecture/proposals/api-specs-v{X}.md` as API-NNN items targeting `/docs/architecture/api-specs.md` at seal |
| `docs/inbox/events.md` | Fold into `architecture/proposals/events-v{X}.md` as EVT-NNN items targeting `/docs/architecture/events.md` at seal |
| `docs/inbox/nfr.md` | Fold into `architecture/proposals/nfr-v{X}.md` as NFR-NNN items targeting `/docs/architecture/nfr.md` at seal |
| `docs/inbox/c4.md` | Merge into `architecture/proposals/architecture-v{X}.md` as text-readable C4 summary; Draw.io/XML source belongs in `arch-assets/` |
| `docs/inbox/arch-assets/` | Architecture assets such as `c4-model.drawio`, `dfd-*.drawio`, infrastructure diagrams, supporting images |

#### Plan — `import plan`

| File Name | Maps to |
|-----------|---------|
| `docs/inbox/implementation-plan.md` | `implementation-plan-v{X}.md` |

#### Test — `import test`

| File Name | Maps to |
|-----------|---------|
| `docs/inbox/test-plan.md` | `test-plan-v{X}.md` |
| `docs/inbox/test-cases.md` | Fold into `testing/proposals/test-cases-v{X}.md` as TC-NNN items targeting `/docs/testing/test-cases.md` at seal |

After `import test` synthesizes or updates `docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md`, run the Test TSV exporter the same way `start test` does so `testing/generated/` stays derived from the canonical active-sprint Markdown.

`start implement` is an execution lane, not a document-import lane. Use `import plan` for planning artifacts and `start implement` to execute an approved plan.

**Auto-detect fallback**: If no inbox file matches the target phase, AI reports:
`"No inbox file found for [phase]. Use the inbox naming table in orchestrator.md, drop the matching file(s) into docs/inbox/, and run import again."`

### Asset Folders

`{phase}-assets/` directories contain binary files (images, PDFs, Figma exports, diagrams). On import:

1. Copy folder contents to the mapped phase folder's `assets/` subdirectory
2. For images AI can read: describe and reference in the document
3. For images/PDFs AI cannot read: note `"Asset: [filename] — human review required"`, reference by path
4. Move original folder to `docs/inbox/processed/`

### Case A: Complete document from outside

User has a finished document. Drop into inbox, then run `import [phase]`.

1. Read **all** file(s) from `docs/inbox/` matching the target phase (primary + supplementals + assets)
2. Map imported content into the target phase outputs per the naming table above:
  - For `import product`: each inbox file folds into matching `docs/sprint-v{X}/product/proposals/*-v{X}.md` files as routed product anchors. If only `product.md` exists, decompose it into product split proposal sections. If only supplementals exist, synthesize GLOSS / PERSONA / MR proposal items, then ask targeted questions for any missing, unclear, conflicting, below-quality, or keep / drop decision items that remain.
  - For `import design`: supplementals map into the design document per the section rules above.
  - For `import arch`: project-reference / sequence / erd / adr / data-flow / api-specs / events / nfr fold into matching `docs/sprint-v{X}/architecture/proposals/*-v{X}.md` files as routed anchors; `c4.md` folds into architecture overview items; `arch-assets/` carries C4 / DFD Draw.io / XML source assets and supporting diagrams. Never write `/docs/architecture/*.md` directly.
3. **Copy assets**: if `{phase}-assets/` folder exists, copy to sprint
4. Audit the merged result against the template **and** the same shared phase quality standard used by `validate *` in `core/phase-quality-standards.md`
5. Classify imported material into: accepted as-is, needs normalization, needs improvement, missing, unclear, conflicting, redundant / out of scope
6. Flag inconsistencies with existing approved documents in current sprint
7. Ask one targeted clarification batch only for missing, unclear, below-quality, conflicting, or keep / drop decision items — do not re-ask already clear content
8. Normalize and synthesize the phase output so the sprint draft is clean, traceable, and review-ready
9. Save to the mapped phase folder as `DRAFT`
10. Move imported inbox file(s) to `docs/inbox/processed/`
11. Report: "Import audit complete (N files + M assets processed). Accepted: [...]. Normalized: [...]. Remaining clarification items: [...]."

### Case B: Partial / in-progress document from outside

User started a document externally (e.g., half-finished Architecture). Drop partial file into inbox, then run `import [phase]`.

1. Read **all** matching content from `docs/inbox/` (primary + supplementals + assets)
2. Merge supplementals into primary structure (same mapping as Case A)
3. Copy assets if present
4. Audit merged result against the template and the same shared phase quality standard used by `validate *` in `core/phase-quality-standards.md`
5. Classify what is already usable, what needs normalization, what needs improvement, what is missing, what is unclear, what conflicts, and what is redundant / out of scope
6. **Ask one targeted clarification batch** for only the missing, unclear, below-quality, conflicting, or keep / drop decision items — do not re-ask content already answered clearly by any inbox file
7. Normalize and synthesize the document per template so the saved draft is clean and review-ready
8. Save as `DRAFT` in the mapped phase folder — output the full completed document for review

### Case C: Mid-phase continuation (session interrupted)

User was doing a phase in PRISM but the session ended before the output was finalized.

1. User types `resume`
2. AI reads existing files in the mapped phase folder
3. If a `DRAFT` file exists: load it, identify what's incomplete or awaiting follow-up, and continue from that point
4. If no file exists: tell user to use the inbox naming table above, drop the matching file(s) into `docs/inbox/`, then fall into Case B
5. Never restart from scratch if partial work exists

### Common Rules for All Import Cases

- **Never auto-approve** — imported/resumed documents always start as `DRAFT`
- **Never overwrite approved documents** — if phase is already `APPROVED` in an open sprint, use `start change:`; if the sprint is sealed, require `new sprint`; if a newer sprint is already active, continue there instead
- **Never re-ask** content that is already clear and sufficient — only ask about missing, unclear, below-quality, conflicting, or keep / drop decision items
- Import should produce a normalized, review-ready `DRAFT`, not a raw pass-through copy of the source material
- Preserve original inbox files in `docs/inbox/processed/`, but normalize sprint outputs to PRISM templates and quality bars
- If ambiguity or conflict remains unresolved, save the `DRAFT` and append an `## Open Issues` section listing all unresolved items — never silently bake ambiguity or conflict into the final text
- Only suggest approval after the DRAFT's `## Open Issues` section has no open rows; otherwise direct the user to the clarification batch, `feedback:`, or `validate [phase]`
- Report clearly: what was imported, what PRISM accepted as-is, what it normalized, and what still needs human review
- `docs/inbox/` is a staging area only — files there have no status; they become DRAFT after import
- For architecture, always create all 9 companion files. If a scope has no current data or is not applicable, write that file with a concise no-current-data / not-applicable note so downstream phases can see the accepted boundary explicitly
