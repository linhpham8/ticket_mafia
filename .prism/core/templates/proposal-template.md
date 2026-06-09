---
status: DRAFT
version: v{X}
sprint: {X}
phase: {{PHASE}}
sprint_id: sprint-v{X}
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
applied_to_living: false
---

# {{TARGET_TITLE}} Proposal — Sprint v{X}

<!-- Phase 9+ production proposal artifact. `apply_proposal.py` merges this file into the
     corresponding Living Truth file(s) at sprint seal via anchor-based merge.

     CANONICAL SPLIT PROPOSALS: guided 2-tier mode writes one delta file per Living
     Truth target under the concrete phase `proposals/` folder, for example:
       - product/proposals/prd-v{X}.md
       - product/proposals/glossary-v{X}.md
       - product/proposals/epics/EP-XXX-{slug}-v{X}.md
       - architecture/proposals/api-specs-v{X}.md
       - testing/proposals/test-cases-v{X}.md

     Phase-root mixed proposal files are not canonical inputs; use the split proposal files.
     Each split file should contain only prefixes for its target; validate_proposal.py
     enforces this from the path.

     Filling rules (per Phase 9 plan §4, Approach A — confirmed Phase 1 spike):

     • Each item below an H3 heading IS the final content that goes into Living Truth
       verbatim. Do NOT write Before/After narrative here — the "Before" state is
       recoverable via git history + snapshots; "Reason / Impact / Migration" narrative
       belongs in the PR description or change-pack `change-request.md`.

     • Anchor format: `<!-- ID: PREFIX-NNN -->` on its own line, immediately above the
       H3 heading. ID prefix uses multi-segment format where applicable
       (`DS-COMP-NNN`, `ARCH-COMP-NNN`). Strict regex: `[A-Z]+(?:-[A-Z]+)*-\d{3,}`
       (≥3-digit zero-padded number).

     • Get next ID atomically:
         python .prism/core/tools/get_next_id.py --type {EP|FR|US|AC|BR|NFR|TC|SCREEN|DS-COMP|ARCH-COMP|ARCH|GLOSS|PERSONA|MR|SEQ|ENT|ADR|FLOW|API|EVT|PR}

     • Validate every proposal file before approve:
         python .prism/core/tools/validate_proposal.py --file <this-file>

     • Empty section? Leave the H2 heading and remove the example placeholder, but
       each approved proposal file must contain at least one anchored item overall.
-->

<!-- ## Canonical split proposal file → allowed prefixes → Living Truth target

  Proposal file                                      | Allowed prefixes              | Target Living Truth file
  ---------------------------------------------------+-------------------------------+-------------------------------
  product/proposals/prd-v{X}.md                      | BR, PRD-OVERVIEW              | /docs/product/prd.md
  product/proposals/glossary-v{X}.md                 | GLOSS                         | /docs/product/glossary.md
  product/proposals/personas-v{X}.md                 | PERSONA                       | /docs/product/personas.md
  product/proposals/market-research-v{X}.md          | MR                            | /docs/product/market-research.md
  product/proposals/epics/EP-XXX-{slug}-v{X}.md      | EP, FR, US, AC                | /docs/product/epics/EP-XXX-{slug}.md
  design/proposals/design-system-v{X}.md             | SCREEN, DS-COMP, DESIGN-OVERVIEW | /docs/design/design-system.md
  architecture/proposals/architecture-v{X}.md        | ARCH, ARCH-COMP, ARCH-OVERVIEW | /docs/architecture/architecture.md
  architecture/proposals/nfr-v{X}.md                 | NFR                           | /docs/architecture/nfr.md
  architecture/proposals/sequence-v{X}.md            | SEQ                           | /docs/architecture/sequence.md
  architecture/proposals/erd-v{X}.md                 | ENT                           | /docs/architecture/erd.md
  architecture/proposals/adr-v{X}.md                 | ADR                           | /docs/architecture/adr.md
  architecture/proposals/data-flow-v{X}.md           | FLOW                          | /docs/architecture/data-flow.md
  architecture/proposals/api-specs-v{X}.md           | API                           | /docs/architecture/api-specs.md
  architecture/proposals/events-v{X}.md              | EVT                           | /docs/architecture/events.md
  architecture/proposals/project-reference-v{X}.md   | PR                            | /docs/architecture/project-reference.md
  testing/proposals/test-cases-v{X}.md               | TC                            | /docs/testing/test-cases.md

ID prefix → Living Truth file routing

  Anchor ID prefix             | Target Living Truth file                                 | Anchored unit
  -----------------------------+----------------------------------------------------------+-------------------
  BR-NNN                       | /docs/product/prd.md                                     | Business rule
  PRD-OVERVIEW-001             | /docs/product/prd.md                                     | PRD narrative (singleton; New in v1, Updated later — ID fixed)
  EP-NNN                       | /docs/product/epics/EP-NNN-{slug}.md  (file-level)       | Epic file (root)
  FR-NNN  + <!-- EPIC: EP-XXX --> | /docs/product/epics/EP-XXX-{slug}.md  (section)       | Functional requirement
  US-NNN  + <!-- EPIC: EP-XXX --> | /docs/product/epics/EP-XXX-{slug}.md  (section)       | User story
  AC-NNN  + <!-- US:   US-XXX --> | inside the US-XXX block of the relevant epic file     | Acceptance criterion
  GLOSS-NNN                    | /docs/product/glossary.md                                | Term
  PERSONA-NNN                  | /docs/product/personas.md                                | Persona
  MR-NNN                       | /docs/product/market-research.md                         | Research finding / segment
  SCREEN-NNN, DS-COMP-NNN      | /docs/design/design-system.md                            | Screen / UI component
  DESIGN-OVERVIEW-001          | /docs/design/design-system.md                            | Design narrative (singleton; New in v1, Updated later — ID fixed)
  ARCH-NNN, ARCH-COMP-NNN      | /docs/architecture/architecture.md                       | Architecture module / boundary
  ARCH-OVERVIEW-001            | /docs/architecture/architecture.md                       | Architecture narrative (singleton; New in v1, Updated later — ID fixed)
  NFR-NNN                      | /docs/architecture/nfr.md                                | Non-functional requirement
  SEQ-NNN                      | /docs/architecture/sequence.md                           | Sequence diagram
  ENT-NNN                      | /docs/architecture/erd.md                                | Entity / table
  ADR-NNN                      | /docs/architecture/adr.md                                | Architecture decision
  FLOW-NNN                     | /docs/architecture/data-flow.md                          | Data flow
  API-NNN                      | /docs/architecture/api-specs.md                          | API endpoint
  EVT-NNN                      | /docs/architecture/events.md                             | Event contract
  PR-NNN                       | /docs/architecture/project-reference.md                  | Module / surface / convention
  TC-NNN  + <!-- VERIFIES: ID-XXX --> | /docs/testing/test-cases.md                        | Test case (VERIFIES is trace tag, not routing)

  New epic creation: anchor `<!-- ID: EP-NNN -->` + heading `### EP-NNN: {title}` in `## New` triggers
  file creation `/docs/product/epics/EP-NNN-{slug-from-title}.md` from `epic-template.md`.
-->

---

## New

<!-- Items to ADD to the routed Living Truth file at sprint seal. apply_proposal appends
     each anchored block to the end of the target LT file (or creates a new epic file
     when an EP-NNN anchor is in this section). -->

<!-- Example: a new business rule (use product/proposals/prd-v{X}.md) -->
<!-- ID: BR-NNN -->
### BR-NNN: {{Short rule title}}
<!-- body of the new BR item (final state) -->

<!-- Example: a new epic (use product/proposals/epics/EP-NNN-{slug}-v{X}.md) -->
<!-- ID: EP-NNN -->
### EP-NNN: {{Epic title — slug derives from this}}
<!-- Epic Overview body plus required `Product Traceability Map` table (`EP -> FR -> related US`) — see epic-template.md -->

<!-- Example: a new FR (use the owning product/proposals/epics/EP-XXX-{slug}-v{X}.md) -->
<!-- ID: FR-NNN -->
<!-- EPIC: EP-XXX -->
**FR-NNN — {{Capability name}}**
<!-- description of the new FR (final state) -->

<!-- Example: a new user story (use the owning product/proposals/epics/EP-XXX-{slug}-v{X}.md) -->
<!-- ID: US-NNN -->
<!-- EPIC: EP-XXX -->
### US-NNN: {{Story title}}
<!-- Story body matching epic-template.md US block: persona, covers FR, AC list, etc. -->

<!-- When FR / US changes alter coverage for an existing epic, also include an Updated EP-XXX block
     with the refreshed Product Traceability Map. -->

<!-- Example: a new acceptance criterion (use the owning product/proposals/epics/EP-XXX-{slug}-v{X}.md) -->
<!-- ID: AC-NNN -->
<!-- US: US-XXX -->
**AC-NNN ({{Happy Path|Error|Edge}})**
<!-- observable behaviour -->

---

## Updated

<!-- Items to REPLACE in the routed Living Truth file at sprint seal. apply_proposal locates
     the existing anchor in the target LT file and swaps the entire section content.

     IMPORTANT (Approach A): the content under each `### TITLE` (or bold-name label line)
     IS the NEW state. Do NOT write Before/After here. -->

<!-- ID: FR-NNN -->
<!-- EPIC: EP-XXX -->
**FR-NNN — {{Possibly-updated capability name}}**
<!-- the NEW description (final, post-merge state) -->

<!-- ID: NFR-NNN -->
### NFR-NNN: {{NFR title (possibly updated)}}
<!-- the NEW NFR content -->

---

## Removed

<!-- Items to DELETE from the routed Living Truth file at sprint seal. apply_proposal
     locates each anchor in the target LT file and removes the whole section.

     The body below each anchor is human-review metadata only (Reason / Cleanup /
     Migration). apply_proposal does NOT merge this body — it only uses the anchor ID
     (and routing tag if present) to identify what to delete. -->

<!-- Example: removing an FR (must include EPIC tag so router knows which epic file to edit) -->
<!-- ID: FR-NNN -->
<!-- EPIC: EP-XXX -->
**FR-NNN — {{Title of the item being removed}}**
- **Reason**: <!-- why we're removing this -->
- **Cleanup**: <!-- orphan screens, API endpoints, test cases that become dead with this removal -->
- **Migration**: <!-- how do we transition existing usage / data when this disappears -->

<!-- Example: removing an entire epic (tombstones the EP-NNN-{slug}.md file at seal and removes active child anchors) -->
<!-- ID: EP-NNN -->
### EP-NNN: {{Epic title being removed}}
- **Reason**: <!-- why -->
- **Cleanup**: <!-- what FRs / USs / ACs get tombstoned -->
- **Migration**: <!-- how do we transition users who depended on this -->

---

### Self-Review Checklist

- [ ] `PROP-1`: Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`
- [ ] `PROP-2`: Frontmatter required keys all present and well-formed: `status`, `version`, `sprint`, `phase`, `sprint_id`, `created`, `updated`, `approved_by`, `applied_to_living`
- [ ] `PROP-3`: `status` is DRAFT pre-approve, APPROVED post-approve; `applied_to_living: false` until sprint seal stamps it
- [ ] `PROP-4`: `version` matches `v{sprint}` exactly (e.g., sprint: 3 ↔ version: v3)
- [ ] `PROP-5`: Each `## New` / `## Updated` / `## Removed` item starts with `<!-- ID: PREFIX-NNN -->` anchor line directly above the H3 heading or bold-name label line
- [ ] `PROP-6`: FR / US items have `<!-- EPIC: EP-XXX -->` routing tag (so the router knows which epic file to write to)
- [ ] `PROP-7`: AC items have `<!-- US: US-XXX -->` routing tag (so the router knows which US block to write into)
- [ ] `PROP-8`: TC items have `<!-- VERIFIES: ID-XXX -->` trace tag (not for routing — TC always routes to `/docs/testing/test-cases.md`; ID may be US/FR/NFR/etc.)
- [ ] `PROP-9`: All IDs use strict format `[A-Z]+(?:-[A-Z]+)*-\d{3,}` (multi-segment, zero-padded ≥3 digits) — atomic issuance via `python .prism/core/tools/get_next_id.py --type {EP|FR|US|AC|BR|NFR|TC|SCREEN|DS-COMP|ARCH-COMP|ARCH|GLOSS|PERSONA|MR|SEQ|ENT|ADR|FLOW|API|EVT|PR}`
- [ ] `PROP-10`: No `**Before**` / `**After**` / `**Reason**` narrative inside `## Updated` items — content under heading IS the new state (Approach A)
- [ ] `PROP-11`: No duplicate IDs across `## New` / `## Updated` / `## Removed`
- [ ] `PROP-12`: Every `## Updated` and `## Removed` ID exists in the routed Living Truth file before seal
- [ ] `PROP-13`: Every `## New` ID is NOT already present in the routed Living Truth file
- [ ] `PROP-14`: New AC items are added at the end of their owning US block, not outside the US section
- [ ] `PROP-15`: Sprint rationale lives in `sprint-brief-v{X}.md` where applicable; mergeable proposal files contain only target deltas
- [ ] `PROP-16`: `validate_proposal.py --file <this-file>` returns 0 blockers
- [ ] `PROP-17`: Split proposal path matches its content target; e.g. `prd-v{X}.md` has only `BR-*`, `api-specs-v{X}.md` has only `API-*`, and epic proposal files have only `EP/FR/US/AC`
- [ ] `PROP-18`: If this proposal `## New`s catalog items enumerated by a table inside a singleton overview (`ARCH-COMP` → `ARCH-OVERVIEW-001` §3b Traceability Map; `SCREEN` → `DESIGN-OVERVIEW-001` §2 Screen Inventory), that overview block is re-authored in `## Updated` (v>1) / `## New` (v1) so its table covers the new items (`VP-11`)
- [ ] `PROP-19`: No mergeable content (H3–H6 headings, tables) in the preamble before the first `## New`/`## Updated`/`## Removed`; such content is silently dropped at seal — put it in an anchored block (`VP-12`)
