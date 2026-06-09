---
status: DRAFT
version: v1
sprint: 1
phase: product
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# Market Research And Competitive Context — {{PROJECT_NAME}}

<!-- This file is the Living Truth root for market research. Each finding / segment is a mergeable anchored block. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each MR-NNN block (findings, evidence, competitor analyses, positioning hypotheses) MUST be
     preceded by `<!-- ID: MR-NNN -->` on its own line.
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type MR`
     Strict format: `MR-\d{3,}` (zero-padded ≥3 digits). -->

<!-- PRISM:LT-SKELETON-END -->

## 1. Market Snapshot

- Category / segment:
- Why now:
- Key market forces:

## 2. Research Findings (anchored, mergeable)

<!-- One anchored block per finding / segment / competitor / hypothesis. -->

<!-- ID: MR-NNN -->
### MR-NNN: {{Finding title}}

- **Type**: Problem Evidence | Competitor | Positioning Hypothesis | Segment | Market Trend
- **Signal / Evidence**: <!-- VD: User survey N=120 cho thấy 78% bỏ giỏ hàng vì checkout phức tạp -->
- **Implication for product**: <!-- Quyết định product nào dựa trên finding này -->
- **Confidence**: High | Medium | Low
- **Source / Asset**: <!-- Link đến raw data, report, interview transcript -->

<!-- ID: MR-NNN -->
### MR-NNN: {{Another finding}}

### 2.1 Summary Tables (overview views)

<!-- Tables ở dưới là VIEW của §2 catalog, không mergeable. Re-derive khi cần. -->

| Signal | Evidence | Implication For Product | Confidence |
|--------|----------|-------------------------|------------|
| | | | High / Med / Low |

## 3. Competitor Landscape

| Competitor / Alternative | Strengths | Weaknesses / Gaps | Implication For {{PROJECT_NAME}} |
|--------------------------|-----------|-------------------|----------------------------------|
| | | | |

## 4. Positioning Hypotheses

| Hypothesis | Supporting Evidence | Risk If Wrong | How To Validate |
|------------|---------------------|---------------|-----------------|
| | | | |

## 5. Sources And Asset References

| Source / Asset | Type | Date | Notes |
|----------------|------|------|-------|
| | | | |

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-3`, `LINK-1`, `ORB-1`
- [ ] Claims are backed by evidence or explicitly marked as assumptions
- [ ] Competitor comparisons are relevant to the product scope
- [ ] Positioning hypotheses connect back to product goals
- [ ] Sources or assets are referenced clearly for human review
