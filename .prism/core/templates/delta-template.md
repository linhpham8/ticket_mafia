---
status: DRAFT
version: v{X}
sprint: {X}
phase: {{PHASE}}
sprint_id: sprint-v{X}
change_pack: v{X}.{Y}.{Z}-{slug}
base_artifact: {{BASE_ARTIFACT}}
applied_to_living: false
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# {{PHASE_TITLE}} Delta — v{X}.{Y}.{Z}-{slug}

<!-- Phase 2+ change-pack delta artifact. seal_sprint.py merges APPROVED deltas
     into the corresponding living-truth file AFTER the sprint's main proposals,
     in change-pack version order.

     Delta files MUST use the same merge structure as proposal-template.md:
     `## New` / `## Updated` / `## Removed` sections with anchored H3 items.
     Approach A applies: each item is a `<!-- ID: PREFIX-NNN -->` anchor on its own line
     followed by its `### Title` (or bold-name) line; the content under that heading IS the new
     state that goes into living truth verbatim. Rationale and downstream impact are preamble
     metadata — not merged.

     Filename convention: `{phase}-delta-v{X}.{Y}.{Z}-{slug}.md` where phase ∈
     {product, design, architecture, testing}. Validator + applier both recognize this
     name regardless of which `### Phase` H1 title the file uses.

     Atomic ID: `python .prism/core/tools/get_next_id.py --type FR` (or appropriate
     prefix for the change). -->

---

### 1. Rationale

<!-- WHY this delta exists — short narrative. Cite incident, audit finding,
     bug ticket, compliance change, or PO directive that prompted the same-sprint
     correction. -->

{{RATIONALE}}

### 2. Downstream Impact

<!-- Phases the delta affects: design? architecture? plan? test? -->
<!-- For each affected phase, name the rule / file / acceptance criterion that
     must be reconciled before this pack can be approved. -->

{{DOWNSTREAM_IMPACT}}

### 3. Acceptance Notes

<!-- Pass / fail signal for absorbing this delta. What does QA observe to confirm
     the pack landed cleanly? -->

{{ACCEPTANCE_NOTES}}

---

## New

<!-- Items to ADD to living truth. Same anchor convention as proposal-template.md.
     NOTE: AC items are NOT inline inside the FR block — each AC is its OWN anchored block
     `<!-- ID: AC-NNN --> <!-- US: US-XXX -->` (see proposal-template.md `## New`), so it routes
     into the US block of the epic file and is independently routable / drift-trackable. -->

<!-- ID: FR-NNN -->
<!-- EPIC: EP-XXX -->
### FR-NNN: {{Short title}}
**Description**: <!-- final post-merge description -->
**Trace**: <!-- US-NNN, NFR-NNN -->

---

## Updated

<!-- Items to REPLACE in living truth. Content under each heading IS the new state.
     NOT a Before/After diff — that lives in §1 Rationale above. AC is a SEPARATE anchored item
     (its own `<!-- ID: AC-NNN --> <!-- US: US-XXX -->` block per proposal-template.md), never
     inline inside FR. -->

<!-- ID: FR-NNN -->
<!-- EPIC: EP-XXX -->
### FR-NNN: {{Title}}
**Description**: <!-- updated description -->
**Trace**: <!-- ... -->

---

## Removed

<!-- Items to DELETE from living truth. Body here is human-review metadata only
     (Reason / Cleanup / Migration) — seal_sprint uses only the anchor ID. -->

<!-- ID: FR-NNN -->
<!-- EPIC: EP-XXX -->
### FR-NNN: {{Title of removed item}}
**Reason**: <!-- why the same-sprint correction removes this -->
**Cleanup**: <!-- orphan downstream artifacts -->
**Migration**: <!-- data/state transition -->

---

### Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ORB-2`
- [ ] Filename matches `{phase}-delta-v{X}.{Y}.{Z}-{slug}.md` where phase ∈ {product, design, architecture, testing}
- [ ] Frontmatter `status` is one of DRAFT / APPROVED; required keys (status, version, sprint, phase, sprint_id, created, updated, approved_by, applied_to_living) all present
- [ ] Every `## New` / `## Updated` / `## Removed` item starts with `<!-- ID: PREFIX-NNN -->` anchor on its own line directly above the H3 heading
- [ ] FR / US items include `<!-- EPIC: EP-NNN -->`; AC items include `<!-- US: US-NNN -->`; TC items include `<!-- VERIFIES: ID-NNN -->`
- [ ] Strict ID format `[A-Z]+(?:-[A-Z]+)*-\d{3,}` (multi-segment, zero-padded ≥3 digits — supports `DS-COMP-NNN` / `ARCH-COMP-NNN`) — atomic IDs via `get_next_id.py`
- [ ] No `**Before**` / `**After**` narrative inside `## Updated` items — content under H3 IS the new state (Approach A)
- [ ] Rationale, Downstream Impact, Acceptance Notes filled — these are not merged but are review-mandatory
- [ ] `validate_proposal.py --file <this-file>` returns 0 blockers. Add `--against-living <target-living>` only when that target exists and trace-resolution warnings are useful.
