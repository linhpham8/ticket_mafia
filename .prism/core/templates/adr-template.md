---
status: DRAFT
version: v1
sprint: 1
phase: architecture
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# Architecture Decision Records — {{PROJECT_NAME}}

<!-- Living Truth root for ADRs. Each decision is a mergeable anchored block. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each ADR-NNN block MUST be preceded by `<!-- ID: ADR-NNN -->` on its own line.
     ADR IDs are immutable — even Superseded ADRs keep their ID for audit.
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type ADR`
     Strict format: `ADR-\d{3,}` (zero-padded ≥3 digits). -->

<!-- PRISM:LT-SKELETON-END -->

<!-- AUTHORING NOTE: At sprint seal, `seal_sprint.inject_indexes` regenerates this file's
`## Index` as `ID | Title` from the anchored ADR blocks — do NOT hand-maintain an index here.
The decision is deliberate: `ID | Title` is the subset reliably derivable from any anchored
block; richer fields (Status / Date / Related requirement) are NOT auto-extracted — they live
inside each ADR block (the `**Status**` / `**Date**` fields below). The table below is an
OPTIONAL author-facing summary, not the auto-generated index. -->

## ADR Index (optional author summary — not the auto `## Index`)

| ADR | Title | Status | Date | Related requirement |
|---|---|---|---|---|
| ADR-NNN | | Proposed / Accepted / Superseded | | |

<!-- ID: ADR-NNN -->
### ADR-NNN — {{DECISION_TITLE}}

#### Context

<!-- Vấn đề gì buộc phải đưa ra quyết định này? Mô tả context kỹ thuật và business constraints. -->

#### Options Considered

| Option | Pros | Cons |
|---|---|---|
| | | |

#### Decision

<!-- Lựa chọn gì và tại sao? -->

#### Consequences

| Tích cực | Tiêu cực |
|---|---|
| | |

#### Reversibility

- **Chi phí đảo ngược**: <!-- Cao / Trung bình / Thấp — và lý do. VD: Thay đổi database sau khi có data production là rất tốn kém -->
- **Điều kiện để xem xét lại**: <!-- Trigger nào sẽ buộc mở lại quyết định này. VD: Khi số service vượt 10 hoặc đội ngũ vượt 30 người -->

#### Follow-up

- **Artifacts bị ảnh hưởng**: <!-- architecture, api, nfr, events, implementation plan -->
- **Revisit trigger**: <!-- điều kiện cụ thể -->

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ARCH-1`
- [ ] Mọi trade-off quan trọng đều có ADR
- [ ] Lý do lựa chọn được giải thích rõ ràng, không phải chỉ liệt kê lựa chọn
- [ ] Consequences (tích cực và tiêu cực) đã được ghi nhận
- [ ] Chi phí đảo ngược và trigger xem xét lại đã được xác định
- [ ] Artifacts bị ảnh hưởng đã được liệt kê
