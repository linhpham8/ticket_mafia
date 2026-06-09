# Change Manager — Same-Sprint Change Pack Model

## Core Concept

A **change pack** is the standard mechanism for updating APPROVED artifacts inside an open sprint.

Naming:
- sprint baseline: `sprint-v{X}`
- same-sprint change pack id: `v{X}.{Y}.{Z}-{slug}`

Format rules:
- `X` = sprint number
- `Y` and `Z` = generated numeric segments used only to keep the full pack id unique inside the sprint
- `slug` = short semantic summary derived from the change request

The full pack id must be unique inside its sprint. If an id or slug candidate would collide with an existing pack, regenerate or extend it before creating the pack folder.

Examples:
- first payment fix pack in `sprint-v1` → `v1.3.8-fix-payment`
- architecture correction in `sprint-v2` → `v2.7.2-auth-contract`

Base artifacts remain frozen. Change packs add immutable delta files inside their own folder.

### Delta target (2-tier model)

Per `core/version-manager.md § Living Truth`, deltas target the corresponding sprint **proposal** file, not the Living Truth `/docs/product/prd.md` / `/docs/design/design-system.md` / `/docs/architecture/architecture.md` files directly. Living Truth is updated only by `seal_sprint.py` at sprint seal:

| Phase | Delta filename | Target proposal | Living Truth merge target (at sprint seal) |
|---|---|---|---|
| Product | `product-delta-v{X}.{Y}.{Z}-{slug}.md` | matching `docs/sprint-v{X}/product/proposals/*-v{X}.md` | `/docs/product/prd.md` (+ `/docs/product/epics/EP-NNN-{slug}.md` if delta touches EP / FR / US / AC IDs) |
| Design | `design-delta-v{X}.{Y}.{Z}-{slug}.md` | `docs/sprint-v{X}/design/proposals/design-system-v{X}.md` | `/docs/design/design-system.md` |
| Architecture | `architecture-delta-v{X}.{Y}.{Z}-{slug}.md` | matching `docs/sprint-v{X}/architecture/proposals/*-v{X}.md` | `/docs/architecture/architecture.md` |
| Testing | `testing-delta-v{X}.{Y}.{Z}-{slug}.md` | `docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md` | `/docs/testing/test-cases.md` |

Deltas follow the same `## New` / `## Updated` / `## Removed` anchor convention as proposals (per `core/templates/delta-template.md`). `seal_sprint.py` applies APPROVED deltas after APPROVED proposals in pack-version order at sprint seal.

## Public Commands

- `start change: [description]`
- `feedback: [changes]`
- `validate changes [pack-id|slug]`
- `approve changes [pack-id|slug]`
- `status`
- `resume`
- `new sprint`

When more than one DRAFT change pack exists, the user may identify the target pack by:
- sprint scope such as `sprint-v1`,
- pack id or id prefix such as `v1.3.8`,
- slug such as `fix-payment`.

## Trigger

Use `start change:` when the user wants to revise an APPROVED artifact inside an open sprint.

Do **not** use it when the source artifact is still `DRAFT`.

## Preconditions

Before opening a change pack, verify all of the following:

1. The target sprint is not sealed by `approve implement`.
2. The source artifact exists in the target sprint.
3. The source artifact is `APPROVED`.

If the source artifact is `DRAFT`, do not create a change pack. Route to normal `feedback:` on that draft.

PRISM does **not** require a global pack lock. Multiple DRAFT change packs may coexist across branches or sprints. Ambiguity is resolved by selection, not by deleting or renaming packs.

## Pack Creation Flow

On `start change: [description]`:

1. Determine the target sprint:
   - if the user explicitly names a sprint (`sprint-v1`, `sprint-v2`), use it,
   - otherwise use the current working sprint.
2. Generate a pack id `v{X}.{Y}.{Z}-{slug}`.
3. Create `/docs/sprint-v{X}/changes/{pack-id}/`.
4. Write `change-request.md` with `status: DRAFT` and the pack id.
5. Run `core/change-propagation.md`.
6. Write `impact-matrix.md`.
7. Create delta files only for the artifacts that must be updated now.
8. Before saving or presenting the pack, run the Universal Quality Gate from `core/orchestrator.md` on every generated delta and any downstream `DRAFT` it touches: apply the relevant template plus `core/phase-quality-standards.md`, fix below-quality items proactively, and leave only human-dependent gaps as blockers / open issues.
9. Report:
   - selected sprint,
   - pack id,
   - earliest affected phase,
   - current downstream phase on each active branch,
   - generated files,
   - blockers.

## Pack Selection And Disambiguation

PRISM may see zero, one, or many DRAFT change packs.

Selection rules:

1. If exactly one DRAFT pack is in scope, use it automatically.
2. If more than one DRAFT pack exists and the user command does not clearly identify one, do **not** guess.
3. Ask the user to choose one pack with a compact list that shows sprint, pack id, and slug.
4. Once a pack is chosen, keep that pack as the working target for subsequent `feedback:`, `validate changes`, `approve changes`, and `resume` requests until the user switches target or the pack is approved.
5. A selected pack stays sticky only while it remains the only plausible active target. If the current request could also apply to another unrelated active draft or the current implementation lane, ask the user to clarify instead of assuming the pack still wins.

Standard prompt:

```text
⚠ I found multiple DRAFT change packs:
   sprint-v1 / v1.3.8-fix-payment
   sprint-v2 / v2.7.2-new-auth
→ Which one should I use?
→ Reply with: v1.3.8 / sprint-v1 / fix-payment / v2.7.2 / new-auth
```

`status` must never block on this ambiguity. It lists all DRAFT packs and their status.

## Current Downstream Rule

A change pack propagates only until the **current downstream phase** on each active branch.

Meaning:
- if a downstream phase has not started, stop there,
- if a downstream phase is `DRAFT`, merge the change through `feedback:` into that draft,
- if a downstream phase is `APPROVED`, generate a delta for it if impacted,
- do not generate future-phase deltas beyond the latest already-existing downstream artifact on that branch.

Later phases read effective truth when they start.

## `feedback:` During A Selected Change Pack

While a selected DRAFT change pack is in focus, `feedback:` applies to:
- `change-request.md`,
- `impact-matrix.md`,
- generated delta files inside that pack,
- removing or shrinking draft delta scope before approval when some generated delta files are no longer needed,
- any downstream draft artifact that must absorb the change.

Before saving, re-audit every touched change-pack file, delta, and downstream draft against its template plus `core/phase-quality-standards.md`; proactively fix below-quality items and record only unresolved human decisions as blockers or `## Open Issues`.

If the current session is clearly focused on that pack and no unrelated active target competes with it, `feedback:` applies there automatically.

If the target pack is ambiguous, or the feedback could also reasonably target another active draft or the current implementation lane, ask the user to choose one before editing.

## `validate changes`

`validate changes [pack-id|slug]` audits the selected DRAFT change pack without editing it.

It means:
- resolve exactly one DRAFT change pack,
- read `change-request.md`, `impact-matrix.md`, generated delta files, and any downstream DRAFT artifacts that absorbed the pack,
- assemble the selected pack's proposed truth as `base artifact + all APPROVED deltas + this selected DRAFT pack's delta` for each touched artifact,
- derive every impacted phase up to the current downstream phase,
- run the existing phase validate command(s) for those impacted phases using cycle `pack-<slug>`,
- write or update the normal active validate files, such as `validate-user-story-pack-<slug>.md`, `validate-design-pack-<slug>.md`, `validate-architecture-pack-<slug>.md`, `validate-plan-pack-<slug>.md`, `validate-test-pack-<slug>.md`, `validate-implementation-spec-pack-<slug>.md`, and `validate-implementation-quality-pack-<slug>.md`.

There is no `validate-changes-<slug>.md` file. The command is an aggregate runner over the existing validate commands so `approve changes` can consume the same per-phase evidence as normal phase approval.

Validate the selected pack's DRAFT delta as the candidate truth for that pack cycle. Do not validate only the frozen base artifact, and do not include DRAFT deltas from unrelated packs. A pack that changes Product from `1+2=3` to `1+2=4` should pass only when every impacted downstream artifact/code scope is consistent with `1+2=4`; stale `1+2=3` references in impacted scope are blockers.

If a pack impacts Implement, run both implementation modes. Running only spec or only quality is not enough for pack closure.

## `approve changes`

`approve changes` closes the selected DRAFT change pack as a whole.

It means:
- approve everything generated inside the selected pack,
- only up to the current downstream phase on each active branch.

If more than one DRAFT pack exists and no pack is already selected in context, ask the user to choose the target pack first.

Approval succeeds only when:
1. all required delta files in the pack are complete,
2. all required downstream drafts have absorbed the change,
3. no blocker remains for the current downstream phase,
4. the touched delta files / downstream drafts have no unresolved `## Open Issues` rows and satisfy the relevant template plus shared phase quality standard,
5. every required pack-cycle validate file from `validate changes [pack-id|slug]` is present, fresh, includes `VAL-1` evidence, and has zero blockers,
6. approval-time console-only re-runs of those same validate commands find no new gaps,
7. any delta that overlaps an artifact already changed by another APPROVED pack in the same sprint has been refreshed so the selected pack already reflects that current effective truth.

On success:
- mark the pack `APPROVED`,
- mark each generated delta artifact `APPROVED`,
- seal every consumed `validate-<command>-pack-<slug>.md` file from `tempo/in-progress/` into `tempo/completed/`,
- update effective truth immediately.

## Guardrails

1. APPROVED base artifacts are never overwritten in place.
2. Multiple DRAFT change packs may coexist, but every change-related action must resolve to exactly one target pack.
3. Only one implementation pass may be open at a time.
4. Flow is forward-only from the earliest affected phase.
5. If Product is impacted, Product must be updated.
6. If Product is not impacted, do not pull Product backward.
7. If a downstream phase is impacted and waiting for approval or closure, it must absorb the selected change before it can approve or close.
8. `approve implement` is blocked while unresolved DRAFT change packs remain in the sprint being sealed.
9. After `approve implement`, no new change pack may open in that sprint.

## Block And Prompt Messages

### Sprint sealed

```text
⚠ Cannot start change — this sprint is already sealed by approve implement.
→ Use: new sprint
→ Or: for an urgent production defect, follow § Hotfix Flow (below)
→ Other: describe what you'd like to do
```

### Source still draft

```text
⚠ Cannot start change — the source artifact is still DRAFT.
→ Use: feedback: [changes]
→ Approve the phase normally when ready
→ Other: describe what you'd like to do
```

### Ambiguous target pack

```text
⚠ I found multiple DRAFT change packs and this request does not identify one clearly.
→ Reply with sprint, pack id, id prefix, or slug
→ Example: sprint-v1 / v1.3.8 / fix-payment
```

### Implement already blocked by unresolved changes

```text
⚠ Cannot approve implement — unresolved DRAFT change pack(s) remain in this sprint.
→ Finish the pack with: feedback: ... / validate changes [pack-id|slug] / approve changes
→ Check blockers with: status
→ Other: describe what you'd like to do
```

## Hotfix Flow (urgent production defect)

For a production bug needing an urgent fix — **bug-fix only, never new features**:

1. **Code fix is your dev process, outside PRISM**: create a `hotfix/{desc}` branch from `main`, fix, test (include a regression test that prevents recurrence), commit, deploy. Standard Safety Guard + Git hygiene stay fully active.
2. **Reflect doc impact via a change**: if the fix touches requirement / design / architecture, open a change here — `start change: [HOTFIX] <summary>` — and **specify the affected sprint**. The change pack records the affected anchored items (`## Updated` / `## Removed`); they re-enter Living Truth at that sprint's seal.
3. **Sealed-sprint rule** (per `core/version-manager.md` Immutable Rule 5): a change pack cannot open in an already-sealed sprint. If the latest sprint is sealed, run `new sprint` first and open the change there. The hotfix change pack must be APPROVED before that sprint seals.
4. If the hotfix affects architecture or API, flag it for Architect review.

## Status Expectations

`status` must follow `core/status-format.md`.

Change-pack-specific requirements:
- list all DRAFT change packs, grouped by sprint,
- for each pack show `earliest`, `downstream`, `phases`, `files`, and `blockers` in the canonical field order,
- `phases` must list the impacted phases from earliest through current downstream in forward order,
- `files` must list `change-request.md`, `impact-matrix.md`, and every currently generated delta file in stable phase order,
- if a pack is already in conversational focus, show `selected: yes`,
- if unresolved DRAFT packs block `approve implement`, surface that through the relevant sprint block or the final `next:` suggestion.

`status` remains read-only and must stay available even when multiple DRAFT packs exist.

## Relationship To `new sprint`

`new sprint` is the sprint creation command. Same-sprint corrections use change packs inside their sprint. New-sprint work lives in a separate sprint folder.

## Cross-Sprint Impact Scan

When `approve changes` succeeds for a change pack in sprint-v{X} and one or more newer unsealed sprints exist, the orchestrator invokes:

```text
core/tools/scan_drift.py --trigger change-pack --pack docs/sprint-v{X}/changes/v{X}.{Y}.{Z}-{slug}
```

The scanner:

1. Reads the pack's `{phase}-delta-*.md` files, collecting `## Updated` + `## Removed` anchor IDs.
2. For each subsequent unsealed sprint v{N} (N > X), scans all mergeable split proposals in that sprint under `docs/sprint-v{N}/{phase}/proposals/`.
3. Writes a drift warning entry to `docs/sprint-v{N}/.drift-warnings.json` for each overlap. `status` renders these until the user dismisses or reconciles.

Full warning shape, dismissal command, and the sprint-seal twin trigger are documented in `core/sprint-manager.md § Cross-Sprint Drift Warning`.

PRISM does not modify any newer sprint document during this scan.

## Multi-DRAFT Detection

On `status`, `resume`, `feedback:`, `validate changes`, or `approve changes`, scan `/docs/sprint-v*/changes/*/change-request.md` for `status: DRAFT`.

Rules:

1. If none exist, continue normal routing.
2. If exactly one exists in scope, use it automatically.
3. If multiple exist, `status` lists them all and change-related write actions ask the user to choose one target pack.
4. PRISM must not rename, delete, or auto-merge packs to resolve ambiguity.

## No Global Change-Pack Lock

There is no `active_change_pack` field in `prism-config.md`.

PRISM discovers open packs by scanning change-pack folders and reading `change-request.md` frontmatter. This keeps branch-based PR workflows safe, avoids config-file merge conflicts, and lets multiple packs coexist until the user explicitly chooses which one to continue.
