# Change Propagation — Forward-Only Downstream Rule

## Purpose

This file defines how a selected DRAFT change pack propagates across existing artifacts in the current sprint.

The rule is generic. It applies to Product, Design, Architecture, Plan, Test, and Implement without special-casing one specific end state.

## Core Rule

Start from the **earliest affected phase** and move **forward only**.

Never propagate backward.

Examples:
- if Product is affected, propagation may continue to Design, Architecture, Plan, Test, and Implement depending on what already exists
- if Architecture is affected and Product is not, do not pull the change backward to Product
- if Plan is affected, do not reopen Product / Design / Architecture unless they are actually impacted by the changed requirement set

## Current Downstream Phase

For each active branch, the **current downstream phase** is the latest phase on that branch that already exists in the current sprint and must absorb the new change now.

Branch rules:
- Product flows into two parallel branches: Design and Architecture
- Design + Architecture converge into Plan and Test
- Plan opens Implement
- Test closes the sprint together with Implement

## Per-Phase Handling

When propagation reaches a phase:

### If the phase has not started

- stop propagation on that branch
- do not create a delta yet
- later, when that phase starts, it reads effective truth

### If the phase exists as `DRAFT`

- do not create a delta
- merge the upstream change into that DRAFT via `feedback:`
- that DRAFT cannot be approved until it includes the change

### If the phase exists as `APPROVED`

- create a delta file inside the selected change pack if the phase is impacted
- the phase must absorb that delta before any further closure on that branch
- creating the delta opens a new validate cycle for that phase: subsequent `validate <command>` runs on the impacted phase write to `tempo/in-progress/validate-<command>-pack-<slug>.md`. The previously sealed `<command>-base.md` (or earlier pack file) in `tempo/completed/` is NOT modified. See `core/orchestrator.md § Validate Active Files` for the full naming and lifecycle rules.

## Impact Matrix

Use this matrix to decide whether a downstream phase is **impacted** by a given upstream change. The matrix is the source of truth for the "if impacted" condition used in `Per-Phase Handling` and `Propagation Algorithm`. If a row applies, the listed downstream artifacts must be reviewed and (per per-phase handling) absorb the change via `feedback:` (DRAFT) or delta (APPROVED). If no row applies and no listed artifact references the changed item, the downstream phase is not impacted.

| Upstream change (Product / Design / Architecture) | Design impact | Architecture impact | Plan impact | Test impact | Implement impact |
|---|---|---|---|---|---|
| FR added / removed / scope or AC changed | flows, wireframes, all 4 states + error copy for that FR | API spec, sequence, ERD entities, event contract, NFR mapping for that FR | task groups for that FR, DOD, traceability index | TC for that FR, Coverage Traceability Index | code, repo test delta, traceability markers scoped to that FR |
| User story added / removed / AC changed | flows / wireframes for that US | API / sequence supporting that US | task group US mapping, DOD | TC mapped to that US | code + repo test delta for that US, traceability marker |
| Persona added / removed / role or capability changed | flows referencing that persona, wireframe persona labels, accessibility notes | auth / authorization rules, role-based API access, RBAC model | task groups touching auth / RBAC / role provisioning | TC referencing that persona / role | auth code, role mapping, RBAC enforcement |
| NFR target changed (latency, throughput, uptime, capacity) | only if it affects loading / error UX patterns | nfr.md §8 config mapping, deployment matrix, capacity assumptions, ADR if trade-off shifts | task groups for capacity / perf work, sequencing | NFR TC, performance test cases, observability TC | config values, perf-sensitive code paths, instrumentation |
| KPI baseline / target / timeframe updated | only if it changes instrumentation surfaces visible in UI | observability / metrics emission contract, event schema if metric-bearing | task groups for metric instrumentation | TC for metric emission / observability assertion | metric / event emission code |
| Constraint added / changed (compliance, deadline, tech stack, region) | accessibility / compliance UI patterns, locale / consent flows | security model, deployment matrix, integration boundaries, ADRs | scope, sequencing, capacity, vendor task groups | compliance / security TC, regional environment TC | compliance-sensitive code, region-specific config |
| Glossary term renamed / canonicalized | screen copy, error copy, label tokens referencing the term | API field names, event names, entity names if drifted | task descriptions, US references, code surfaces | TC step copy, expected result copy | code identifiers if drifted from canonical name |
| Integration added / removed / direction or SLA changed | UI states for sync / async behavior (loading, retry, offline) | api-specs, sequence, events, integration deployment matrix, ADR | task groups for integration work, sequencing | integration TC, contract TC, environment / data setup | integration client code, retry / circuit-breaker config |
| Entity lifecycle / state transition changed | wireframes for each new / removed state, transition copy | ERD state column, sequence with `[TX BEGIN/COMMIT/ROLLBACK]`, events for transitions | task groups for state machine work | TC per state + invalid transition + timeout | state machine code, transition handlers, repo test delta |
| Architecture component / API contract changed (downstream of approved Architecture) | only if API contract change surfaces a new error / state in UI | api-specs, sequence, project-reference module map | task groups touching that component / API, allowed_diff_boundary | TC referencing that API / component | code in that module, repo test delta, traceability marker |
| Architecture data ownership / module boundary changed | n/a (unless UI module owner shifts) | erd, project-reference module map, ADR, bounded contexts | task groups for migration / boundary work | TC for ownership invariants | code move, dependency direction enforcement |
| Design state / error copy / validation rule changed | n/a (this IS Design) | only if API error catalog must add / change codes | task group acceptance criteria touching that screen | TC expected result, error TC | UI code, validation code, error handling, repo test delta |

Notes:
- "n/a" means the matrix expects no propagation in that column under normal cases. If a real change does cross that boundary, treat it as a separate upstream change (e.g., a Design change that forces a new API error code triggers the Architecture row, not this one).
- A change pack may match multiple rows; apply all matching rows, then per-phase handling decides feedback vs delta per impacted artifact.
- Impact judgment is matrix-first. A downstream phase is exempt from absorbing the change only if no row applies AND no existing artifact in that phase references the changed item by ID, name, or contract field.

## Removal Cleanup Rule

When a change pack removes an item (FR, US, persona, integration, entity, component, API contract, event), downstream cleanup must be **scope-strict** — no orphans, no collateral.

- Identify all artifacts that reference the removed item by ID, name, or contract field.
- Mark those artifacts for removal or archival inside the corresponding delta. Do NOT silently delete; the delta records the removal so it is auditable.
- Do NOT touch any artifact that does not reference the removed item, even if it sits in the same file or shares utility code.
- For code with mixed feature markers (e.g. `// Feature: FR-018 | FR-022`), remove only the marker for the removed feature and keep markers for surviving features. The underlying code stays unless every owning feature is removed.
- Shared utility code, helpers, schemas, or DB columns added originally for the removed item but now consumed by surviving items MUST stay. Verify by grepping for usage references before any deletion.
- Tests, TCs, and repo test delta uniquely scoped to the removed item are removed; tests covering shared behavior with surviving items are kept.
- Traceability indexes (Coverage Traceability Index, Delivery Traceability Index, Architecture Traceability Map) must drop rows for the removed item rather than leave stale references.
- If a removal cannot be cleanly scoped because business logic, schema, or contract is tightly coupled across the removed item and surviving items, surface the conflict to the user inside the change pack DRAFT before `approve changes`. Do not auto-decide which side wins.

## Propagation Algorithm

1. Identify the earliest affected phase.
2. Apply the change at that phase:
   - `DRAFT` → feedback
   - `APPROVED` → delta
3. Move forward one step along each downstream branch. At each step, consult the Impact Matrix to decide whether the downstream phase is impacted and which specific artifacts in that phase must absorb the change.
4. Repeat until the current downstream phase on that branch has absorbed the change.
5. Stop when:
   - the next downstream phase has not started, or
   - the Impact Matrix shows no row applies AND no existing artifact on that branch references the changed item by ID, name, or contract field.

## Examples

### Example B — Product approved, Design draft, Architecture not started

Result:
- Product delta
- Design absorbs change through `feedback:`
- Architecture branch stops because it has not started

### Example C — Product approved, Design approved, Architecture approved, Plan approved, Test not started

Result:
- Product delta
- Design delta if impacted
- Architecture delta if impacted
- Plan delta if impacted
- Test stops because it has not started

### Example D — Architecture approved, Plan approved, Implement in progress

Result:
- Architecture delta
- Plan delta if impacted
- current implementation pass must absorb effective truth before `approve implement`

### Example E — Worked matrix walkthrough: FR-007 AC changed mid-sprint

State: Product approved · Design approved · Architecture approved · Plan approved · Test approved · Implement in progress (task groups 1–3 already merged, 4–6 in progress).

Change: Product change pack updates `FR-007` acceptance criteria — adds a new error state when payment timeout exceeds 30s.

Matrix row matched: "FR added / removed / scope or AC changed".

Per-phase impact (matrix-derived):
- Product (APPROVED) → author `product-delta-v{X}.{Y}.{Z}-{slug}.md` in the change pack: `## Updated` `FR-007` (with `<!-- EPIC: EP-XXX -->`) plus the new/changed `AC-NNN` (with `<!-- US: US-XXX -->`). The delta is written in the change pack, never edited directly in Living Truth; it routes into the epic file `/docs/product/epics/EP-XXX-{slug}.md` only at sprint seal.
- Design (APPROVED) → delta on flow + wireframe + error copy for FR-007 (4 states), referencing the new timeout error state
- Architecture (APPROVED) → delta if `api-specs`, `sequence`, or `nfr` mapping for FR-007 changes (timeout config likely impacted via `/docs/architecture/nfr.md` §8)
- Plan (APPROVED) → delta on the task group(s) mapped to FR-007 plus the Delivery Traceability Index entry
- Test (APPROVED) → delta on TC for FR-007 plus Coverage Traceability Index entry; new TC for the 30s timeout error path
- Implement (in progress) → task groups 1–3 already merged using the old AC: must absorb effective truth before `approve implement`. Forward-patch tasks for old code go into the upcoming task group; do not retroactively edit closed groups silently.

Validate cycles: each impacted phase opens a new validate cycle named `pack-<slug>`. Previously sealed `validate-<command>-base.md` files in `tempo/completed/` remain untouched.

Closure: run `validate changes <slug>` to audit every impacted phase in the pack cycle. `approve changes` is blocked until every impacted artifact has absorbed its delta and each impacted phase's `pack-<slug>` validate file is present, fresh, and clean.

## Effective Truth Assembly

For each artifact, effective truth is:

`base artifact + every APPROVED delta for that artifact in the current sprint`

There is no implied replay sequence across approved packs. Packs are referenced and approved by pack id or slug. If a selected DRAFT pack touches an artifact already changed by another APPROVED pack in the same sprint, refresh that selected pack against the current effective truth before `approve changes` succeeds.

### Selected-Pack Effective Truth

While a DRAFT change pack is selected, `validate changes [pack-id|slug]` and `approve changes [pack-id|slug]` MUST validate against the selected pack's proposed truth:

`base artifact + every APPROVED delta for that artifact in the current sprint + the selected DRAFT pack's delta for that artifact`

This rule is pack-scoped. Do not include DRAFT deltas from any other pack. Do not validate only the frozen APPROVED base artifact when the selected pack has a delta for that artifact.

Example: if `docs/sprint-v3/product/proposals/prd-v3.md` says `1+2=3` and is APPROVED, and `docs/sprint-v3/changes/change-v3-update-cong-thuc/product-delta-*.md` changes it to `1+2=4`, then `validate changes change-v3-update-cong-thuc` treats `1+2=4` as the Product truth for that pack cycle. Validation passes only if every impacted downstream phase and code scope has absorbed and remains consistent with `1+2=4`; any remaining `1+2=3` reference in impacted Design / Architecture / Plan / Test / Implement scope is a blocker.

Use this when:
- starting a new phase,
- resuming work,
- checking status,
- validating approval,
- implementing code.

## Closure Rule

Any impacted downstream approval or closure is blocked until the nearest required downstream artifact has absorbed the selected change.

Examples:
- impacted Design draft cannot be approved before it absorbs the Product change
- impacted Plan cannot be approved before it absorbs upstream Design / Architecture changes
- impacted Implement cannot be approved before the selected pack is closed

## Non-Rule

This file does **not** decide whether the user should create a new sprint instead. That is a separate sprint-boundary decision managed by the user through `new sprint`.
