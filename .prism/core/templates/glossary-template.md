---
status: DRAFT
version: v1
sprint: 1
phase: product
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# Glossary — {{PROJECT_NAME}}

<!-- This file is the Living Truth root for project glossary. Each term is a mergeable anchored block. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each GLOSS-NNN block in §1 MUST be preceded by `<!-- ID: GLOSS-NNN -->` on its own line.
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type GLOSS`
     Strict format: `GLOSS-\d{3,}` (zero-padded ≥3 digits).
     (Guided seal only) The anchor also lets `apply_proposal.py` merge this block at sprint seal — Freedom has no seal but still issues the ID above and keeps the anchor. -->

<!-- PRISM:LT-SKELETON-END -->

## 1. Core Terms

<!-- One anchored block per term. -->

<!-- ID: GLOSS-NNN -->
### GLOSS-NNN: {{Term}}

- **Definition**: <!-- VD: Service-Level Agreement — cam kết về thời gian phản hồi và uptime tối thiểu giữa các bên. -->
- **Why it matters**: <!-- Vai trò trong domain — engineering, ops, compliance. -->
- **Source / Related**: <!-- PRD §X / ADR-NNN / external standard ref. -->

<!-- ID: GLOSS-NNN -->
### GLOSS-NNN: {{Another term}}

<!-- Lặp lại block ở trên cho mỗi term. -->

### 1.1 Summary View

| Term | Definition (one-liner) |
|---|---|
| GLOSS-NNN | |
| GLOSS-NNN | |

## 2. Acronyms And Abbreviations

| Acronym | Expansion | Notes |
|---------|-----------|-------|
| | | |

## 3. Language Guardrails

- Preferred terms:
- Terms to avoid or clarify:
- Notes for downstream design / architecture / QA wording:

## 4. Pending Terminology Decisions

| Term / Phrase | Open Issue | Owner | Status |
|---------------|------------|-------|--------|
| | | | Open |

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `ORB-1`
- [ ] Core domain terms are defined once and used consistently
- [ ] Acronyms are expanded at least once
- [ ] Ambiguous or overloaded terms are flagged explicitly
- [ ] Terminology aligns with `/docs/product/prd.md` and the relevant `/docs/product/epics/EP-NNN-{slug}.md` files
