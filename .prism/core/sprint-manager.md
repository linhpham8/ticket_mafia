# Sprint Manager

Rules for multi-sprint parallel preparation. Applies in guided mode. Freedom mode ignores sprint gates entirely.

## Concept

A single sprint is one versioned working cycle: product → design → architecture → plan → test → implement. Each sprint has exactly one implementation pass: `approve plan` opens it, and `approve implement` closes it and seals the sprint. When product and design for the next cycle are ready before the current implementation closes, `new sprint` can open a new sprint early — but plan, test, and implement in the new sprint stay gated until the previous sprint seals.

Change packs remain same-sprint corrections. They are branch-friendly, live inside `changes/`, and may exist in more than one DRAFT state at the same time. PRISM resolves ambiguity by asking the user which pack to continue.

## Sprint Sealed Flag

Each sprint carries a `sealed` flag, tracked in `prism-config.md`:

```yaml
sprints:
  - id: v1
    sealed: false    # becomes true when approve implement succeeds
  - id: v2
    sealed: false
```

`sealed: true` means the sprint is fully closed — `approve implement` was approved and no further changes are possible in that sprint.

If `sprints` is absent from `prism-config.md`, treat all existing sprints whose highest phase is `APPROVED` (`implement`) as sealed.

## New Sprint Guard (relaxed)

`new sprint` is allowed when the **latest open sprint** satisfies **all** of:

1. `product` → `APPROVED`
2. `design` → `APPROVED`
3. No DRAFT change pack remains open in that latest sprint

Plan, test, and implement do **not** need to be approved.

**Block message when not satisfied:**

```text
⚠ Cannot create new sprint.
→ Conditions not yet met in sprint-v{X}:
  [list only the unsatisfied ones, e.g.:]
  - design: DRAFT (not yet approved)
  [or]
  - DRAFT change pack v{X}.{Y}.{Z}-{slug} is still open — approve it first
→ New sprint opens when product + design are APPROVED and no DRAFT change pack remains open in the latest sprint.
```

## Plan Gate

`start plan`, `start test`, and `start implement` in sprint-v{X+1} require **all previous sprints** to be `sealed: true`.

**Block message:**

```text
⚠ Cannot start [plan|test|implement] in sprint-v{X+1}.
→ sprint-v{X} is not yet sealed: [implement|test] is still DRAFT.
→ [plan|test|implement] unlocks when sprint-v{X} approves implement.
→ sprint-v{X} current state: test [status]  implement [status]
```

**Auto-unlock on seal:**

When `approve implement` succeeds in sprint-v{X}, the orchestrator invokes `core/tools/seal_sprint.py --sprint v{X}` which performs the full seal pipeline (per discussion doc §9.E):

1. Pre-flight validate all APPROVED proposals + APPROVED same-sprint change-pack deltas via `validate_proposal.py`. Any blocker aborts seal.
2. Atomic merge proposals + deltas into the Living Truth tree (`/docs/product/**`, `/docs/design/design-system.md`, `/docs/architecture/**`, `/docs/testing/test-cases.md`) via `seal_sprint.py` → `apply_proposal.py` / `apply_proposal.apply_multi_target`. All merges computed in-memory first; failure leaves living truth untouched.
3. Regenerate each merged Living Truth file's `## Index` from its anchored items via `inject_indexes` (operates on the in-memory merged text before snapshot/write, so IDs are preserved and re-sorted ascending; prd also gets its Epic Index).
4. Write byte-for-byte snapshots `docs/sprint-v{X}/snapshots/{phase}/.../{name}-at-v{X}-sealed.md` (chmod 444), mirroring every Living Truth file.
5. Sync the sprint's phase assets into the Living Truth tree `docs/<phase>/assets/**`. **Copy** `docs/sprint-v{X}/<phase>/assets/**` (override on filename collision — the sprint folder keeps the historical copy), so the `assets/...` diagram/image references that merged into Living Truth (C4 / DFD Draw.io sources, wireframe PNGs, PDFs) resolve against the live tree. **Remove** every path listed in that phase's `docs/sprint-v{X}/<phase>/assets/.removed` manifest (one path per line, relative to `docs/<phase>/assets/`, `#` comments + blank lines ignored). Copy is additive across sprints — earlier sprints' assets carry over untouched; the manifest is the only way to delete one. Removal is idempotent (an already-absent path is reported, not an error); listing a path that is also present in the sprint (add+remove the same asset) is a seal blocker; the `.removed` manifest itself is never copied into Living Truth. Binary assets are not re-snapshotted — each sprint's `assets/` folder already preserves that sprint's contribution. After the sync, the post-seal validator (`LTV-ASSET` in `validate_living_truth.py`) blocks the seal if any `assets/...` reference in a Living Truth file resolves to a missing file — so a removal (or a typo) that would leave a dangling diagram/image link is caught and rolled back.
6. Set `sprints[v{X}].sealed = true` and `sprints[v{X}].sealed_at` in `prism-config.md`.
7. Stamp `applied_to_living: true <commit-hash> (sealed <ts>)` on every merged source file's frontmatter (falls back to `true <ts>` when not in a git repo).
8. Invoke `scan_drift.py --trigger seal --sprint v{X}` → emit drift warnings to newer unsealed sprints' `.drift-warnings.json` (see § Cross-Sprint Drift Warning below).

Report after seal:

```text
✅ sprint-v{X} sealed.
→ Merged {N} source(s) into {M} Living Truth file(s).
→ Snapshots written under docs/sprint-v{X}/snapshots/ (chmod 444).
→ Assets copied into Living Truth docs/<phase>/assets/ (if any).
→ sprint-v{X+1} plan and test are now open.
→ Drift warnings (if any): see status output.
→ To continue: start plan  or  start test
```

## Parallel Sprint Chain

Multiple in-progress sprints are allowed. No hard limit.

`new sprint` always checks the **most recent sprint** (highest v-number) for the trigger conditions. Example:

```text
sprint-v1: plan ✅, test 🔄, implement 🔄
sprint-v2: product ✅, design ✅, arch 🔄, no DRAFT change pack
→ new sprint → allowed → creates sprint-v3
→ sprint-v3 plan/test/implement blocked until v2 seals (which is blocked until v1 seals first)
```

## Cross-Sprint Drift Warning

Drift warnings fire on **two triggers** (per discussion doc §7.2 / §7.3). Both are implemented by `core/tools/scan_drift.py` — same code path, two CLI flags:

### Trigger A — Change pack approval

When a change pack is approved in sprint-v{X} and one or more newer unsealed sprints exist, `scan_drift.py --trigger change-pack --pack docs/sprint-v{X}/changes/v{X}.{Y}.{Z}-{slug}` runs and:

1. Reads the pack's `{phase}-delta-*.md` files, collecting `## Updated` + `## Removed` anchor IDs.
2. For each newer unsealed sprint v{N} (N > X), scans all mergeable split proposals in that sprint under `docs/sprint-v{N}/{phase}/proposals/`.
3. Writes a drift warning entry to `docs/sprint-v{N}/.drift-warnings.json` for each overlap.

### Trigger B — Sprint seal

When `approve implement` succeeds in sprint-v{X}, `seal_sprint.py` invokes `scan_drift.py --trigger seal --sprint v{X}` automatically after merging proposals into Living Truth. The scanner:

1. Reads all APPROVED proposals in sprint-v{X} (across product / design / architecture phases).
2. Collects `## Updated` + `## Removed` anchor IDs — these are the IDs the seal just merged into Living Truth.
3. For each newer unsealed sprint v{N} (N > X), scans the proposals there for matching anchor IDs.
4. Writes drift warning entries to `docs/sprint-v{N}/.drift-warnings.json`.

### Warning shape

Each entry in `.drift-warnings.json`:

```json
{
  "emitted_at": "YYYY-MM-DD HH:MM",
  "source_sprint": "v{X}",
  "source_event": "seal" | "change-pack v{X}.{Y}.{Z}-{slug}",
  "affected_items": ["FR-014", "FR-007"],
  "dismissed": false
}
```

User-facing rendering in `status` output:

```text
⚠ Drift warning on sprint-v{N} from source_event in sprint-v{X}:
  affected IDs: FR-014, FR-007
→ PRISM does not modify any newer sprint automatically.
→ To handle: validate [phase]  /  feedback: [changes]  /  ignore if unrelated
```

**Rule**: PRISM never auto-modifies any newer sprint document as a result of an older sprint's change or seal. The user reconciles manually (`start change:`) or dismisses.

Dismissal flips `dismissed: true` in the JSON entry:

```text
dismiss sprint-v{N} drift warning
```

## Multi-DRAFT Packs (Branch-Based Collaboration)

Change packs are intentionally branch-friendly. It is valid for different feature branches — and even different sprints — to each carry their own DRAFT change pack.

**Detection:** scan `/docs/sprint-v*/changes/*/change-request.md` for `status: DRAFT`.

Behavior:

1. `status` always works and lists all DRAFT change packs.
2. `resume`, `feedback:`, `validate changes`, and `approve changes` must resolve to exactly one target pack.
3. If a command is ambiguous, PRISM asks the user to choose rather than blocking the workflow or requiring deletion.
4. The user may answer with a sprint, pack id, id prefix, or slug.

**Standard prompt:**

```text
⚠ I found multiple DRAFT change packs:
  sprint-v1 / v1.3.8-fix-payment
  sprint-v2 / v2.7.2-new-auth
→ Which one should I use?
→ Reply with: v1.3.8 / sprint-v1 / fix-payment / v2.7.2 / new-auth
```

PRISM does not rename, merge, or delete packs automatically.

## Status Display With Multiple Sprints

`status` MUST use `core/status-format.md` as the canonical shape.

Multi-sprint specifics:

1. Render sprint blocks oldest to newest.
2. Use only these sprint labels: `[running]`, `[prep — plan/test/implement blocked until v{X} seals]`, `[sealed]`.
3. When a lane is blocked by an earlier sprint that is not sealed, render `⛔ blocked (sprint-v{X} not sealed)`.
4. For every started phase / lane, include the canonical `files:` line defined in `core/status-format.md`.
5. Place any drift warning directly under the affected sprint block.
6. End with one canonical `next:` line, not a list of suggestions.

## Working Sprint Detection

When a user runs a phase command without specifying a sprint, PRISM uses the sprint with the most recently updated DRAFT file (by `updated` frontmatter). User can be explicit: `resume design in sprint-v1` or `resume design in sprint-v2`.

If exactly one active target exists in scope, PRISM may use it automatically.

If a single DRAFT change pack exists and no unrelated active draft or current implementation scope competes with it in the current session, prefer that pack over ordinary phase drafts.

If multiple plausible targets exist and the command or current chat does not clearly identify one, ask the user to choose one. Do not guess.

If both sprints have DRAFT work with the same timestamp, prefer the higher sprint number.
