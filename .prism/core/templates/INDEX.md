# PRISM Templates Index

This folder hosts the canonical templates for every PRISM artifact. This INDEX is the single source of truth for "which template, which phase". When a template is added, renamed, or removed in this folder, update this INDEX in the same change.

Path to this folder is resolved through `prism.json` → `paths.templates` (default `.prism/core/templates`). Filenames below are relative to that resolved folder.

## Templates by phase

| Phase | Artifact | Filename | LT path (Phase 9) | Anchor prefix |
|-------|----------|----------|-------------------|---------------|
| Product | PRD root | `prd-template.md` | `/docs/product/prd.md` | `BR-NNN`, `PRD-OVERVIEW-001` |
| Product | Epic (1 file per epic) | `epic-template.md` | `/docs/product/epics/EP-NNN-{slug}.md` | `EP / FR / US / AC` |
| Product | Glossary | `glossary-template.md` | `/docs/product/glossary.md` | `GLOSS-NNN` |
| Product | Personas | `personas-template.md` | `/docs/product/personas.md` | `PERSONA-NNN` |
| Product | Market Research | `market-research-template.md` | `/docs/product/market-research.md` | `MR-NNN` |
| Design | Design System | `design-template.md` | `/docs/design/design-system.md` | `SCREEN / DS-COMP`, `DESIGN-OVERVIEW-001` |
| Architecture | Architecture Overview | `architecture-template.md` | `/docs/architecture/architecture.md` | `ARCH / ARCH-COMP`, `ARCH-OVERVIEW-001` |
| Architecture | NFR | `nfr-template.md` | `/docs/architecture/nfr.md` | `NFR-NNN` |
| Architecture | Sequence Diagrams | `sequence-template.md` | `/docs/architecture/sequence.md` | `SEQ-NNN` |
| Architecture | ERD | `erd-template.md` | `/docs/architecture/erd.md` | `ENT-NNN` |
| Architecture | ADR | `adr-template.md` | `/docs/architecture/adr.md` | `ADR-NNN` |
| Architecture | Data Flow | `data-flow-template.md` | `/docs/architecture/data-flow.md` | `FLOW-NNN` |
| Architecture | API Specs | `api-specs-template.md` | `/docs/architecture/api-specs.md` | `API-NNN` |
| Architecture | Events / Message Contracts | `events-template.md` | `/docs/architecture/events.md` | `EVT-NNN` |
| Architecture | Project Reference (code contract) | `project-reference-template.md` | `/docs/architecture/project-reference.md` | `PR-NNN` |
| Testing | Test Cases | `test-cases-template.md` | `/docs/testing/test-cases.md` | `TC-NNN` |
| Plan | Implementation Plan | `implementation-plan-template.md` | _(sprint-only, không promote)_ | _(no anchor)_ |
| Test | Test Plan | `test-plan-template.md` | _(sprint-only, không promote)_ | _(no anchor)_ |
| Change | Change Request | `change-request-template.md` | _(change pack, không promote)_ | _(no anchor)_ |
| Change | Impact Matrix | `impact-matrix-template.md` | _(change pack, không promote)_ | _(no anchor)_ |
| Change | Delta (per-phase) | `delta-template.md` | _(change pack, merges via apply_proposal at seal)_ | uses sibling proposal prefixes |
| Sprint | Split target proposal | `proposal-template.md` | _(sprint output under `{phase}/proposals/`; routes by anchor prefix to LT)_ | target-specific prefixes |

**Total**: 22 templates. **15 root Living Truth files** + N dynamic epic files (1 per epic under `/docs/product/epics/`).

## Phase 9 changes (vs 1.x sprint-scoped layout)

- **Restructured to per-phase nested folders**: `/docs/{product,design,architecture,testing}/...`
- **Per-epic files**: `/docs/product/epics/EP-NNN-{slug}.md` (one file per epic, anchored EP + FR + US + AC). Replaces single `/docs/user-stories.md` LT.
- **Companions promoted to LT**: `glossary`, `personas`, `market-research` (product); `nfr`, `sequence`, `erd`, `adr`, `data-flow`, `api-specs`, `events`, `project-reference` (architecture); `test-cases` (testing). All anchored.
- **NFR moved** from product to architecture phase (`/docs/architecture/nfr.md`).
- **ID prefix rename + split**: `EPIC` → `EP`; `COMP` → `DS-COMP` (design) + `ARCH-COMP` (architecture).
- **13 new ID prefixes**: `BR, NFR, TC, GLOSS, PERSONA, MR, SEQ, ENT, ADR, FLOW, API, EVT, PR`.
- **Test cases**: ID format `TC-{AREA}-{NNN}` → flat `TC-NNN`; feature area moves to `**Area**:` body field.
- **Templates deleted**: `epics-template.md`, `user-stories-template.md`, `sprint-stories-template.md` (gộp vào `epic-template.md` + `proposal-template.md`).

## Usage

- Each phase always uses the templates listed under its row above. There is no conditional / scope-based filtering for templates.
- Phase prompts may reference template files by name; this INDEX is the authoritative mapping for verifying or adding those references.
- Generated outputs follow the artifact naming defined in `prism/core/version-manager.md § Canonical Artifact Naming`. The 15 root Living Truth files are scaffolded once at first sprint seal from the corresponding templates (`seal_sprint.py bootstrap_living_from_template`). Each sprint then writes split proposal files under concrete phase `proposals/` folders by Living Truth target; `apply_proposal.py` routes each anchored item by ID prefix to the correct LT file at sprint seal.
- Epic files (`epics/EP-NNN-{slug}.md`) are created on-demand: when proposal `## New` contains `<!-- ID: EP-NNN -->` + heading `### EP-NNN: {title}`, `apply_proposal.py` creates the new epic file from `epic-template.md` (slug derived from title).
- Generated outputs must preserve the compact Quality Contract from `prism/core/phase-quality-standards.md`: numbered review-ready structure (`DOC-1`), stable item IDs (`DOC-2`), required template section coverage (`DOC-3`), concrete cross-links (`LINK-1`), explicit dependency context (`LINK-2`), and sprint/effective-truth evidence (`ORB-1`) where applicable.

## Maintenance

When adding, renaming, or removing a template:
1. Update this INDEX (rows + phase mapping + anchor prefix column).
2. Update the affected phase prompt if it references the template by name.
3. Update `prism/core/import-validator.md` mapping table if the artifact is part of import flow.
4. Update `prism/core/tools/seal_sprint.py` `LIVING_TO_TEMPLATE` mapping if the template scaffolds a Living Truth file.
5. Update `prism/core/tools/apply_proposal.py` prefix routing table if a new anchored prefix is introduced.
6. Update `prism/core/tools/get_next_id.py` accepted `--type` list if a new ID counter is introduced.
7. Add or update the template Self-Review Checklist rule refs, so validation can cite the rule ID instead of relying on reviewer taste.
