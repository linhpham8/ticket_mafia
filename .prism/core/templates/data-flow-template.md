---
status: DRAFT
version: v1
sprint: 1
phase: architecture
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# Data Flow Diagram — {{PROJECT_NAME}}

<!-- Living Truth root for data flows. Each flow is a mergeable anchored block. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each FLOW-NNN block in §3 MUST be preceded by `<!-- ID: FLOW-NNN -->` on its own line
     above the `### FLOW-NNN: {Name}` heading.
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type FLOW`
     Strict format: `FLOW-\d{3,}` (zero-padded ≥3 digits). -->

<!-- PRISM:LT-SKELETON-END -->

## 1. DFD Notation And Source

DFD dùng notation như tài liệu architecture example:

| Element | Shape | Usage |
|---|---|---|
| External actor / system | Rectangle | Người dùng, vai trò, hệ thống ngoài biên |
| Process | Circle | Business/data processing step, named by verb-noun phrase |
| Data store | Open-ended rectangle | Repository, database, document store, model store, queue/log when used as storage |
| Data flow | Labeled arrow | Data/action payload moving between actor, process, or store |

- **Draw.io/XML asset path**: `assets/dfd-{{FLOW_SLUG}}.drawio` hoặc `assets/dfd-{{FLOW_SLUG}}.drawio.xml`
- **Status**: <!-- present / generated / blocker: missing source asset -->
- **Minimum coverage**: At least one DFD is required. When multiple user groups / personas have materially different actors, permissions, or data paths, split DFD coverage by user group.
- **Style**: black/white, lean, no decorative colors, every data flow uses a labeled arrow, layout optimized for architecture document readability.
- **Connector routing**: arrows must not cut across or run through actors, processes, data stores, containers, or boundaries. Avoid crossings where possible; if a crossing is unavoidable, use arc line jumps (`jumpStyle=arc`) and keep labels readable.
- **Mermaid**: not required for DFD. Use Draw.io/XML as the editable source of truth.

## 2. Data Flow Inventory

<!-- Bảng index — mỗi row đối ứng 1 FLOW-NNN block ở §3. Phải có ít nhất 1 row / 1 hình DFD. -->

| Flow ID | Business flow | External actors | Processes | Data stores | Draw.io/XML source | Notes |
|---|---|---|---|---|---|---|
| FLOW-NNN | | | | | `assets/dfd-...drawio` | |

## 3. DFD Flows (anchored, mergeable)

<!-- ID: FLOW-NNN -->
### FLOW-NNN: {{FLOW_NAME}}

#### 3.N.1 External Actors / Systems

| Actor / System | Boundary | Role in flow |
|---|---|---|
| | internal / external | |

#### 3.N.2 Processes

| Process | Responsibility | Owner / bounded context | Related FR / US / API |
|---|---|---|---|
| | | | |

#### 3.N.3 Data Stores

| Data store | Stored data | Source of truth? | Owner / consistency model |
|---|---|---|---|
| | | yes / no | |

#### 3.N.4 Data Flows

| # | From | To | Data / action label | Mode | Notes |
|---|---|---|---|---|---|
| 1 | | | | sync / async / manual / batch | |

#### 3.N.5 Draw.io/XML Source

- **Asset path**: `assets/dfd-{{FLOW_SLUG}}.drawio`
- **Required notation check**: external actors are rectangles; processes are circles; data stores use open-ended rectangle data-store shape; every arrow has a data/action label; connector routing does not run through shapes, and unavoidable crossings use arc line jumps (`jumpStyle=arc`).
- **Trace**: <!-- FR / NFR / US / API / entity refs -->
- **User group split**: <!-- user group/persona covered by this DFD, or `shared flow` when one DFD genuinely covers all groups -->

## 4. Data Ownership And Source Of Truth

| Data domain | Source of truth | Replicas / caches | Consistency model |
|---|---|---|---|
| | | | |

## 5. Failure And Recovery Notes

| Failure mode | Expected behavior | Recovery strategy |
|---|---|---|
| | | |

## 6. Compliance / Retention Notes

| Data class | Constraint | Notes |
|---|---|---|
| | | |

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ARCH-1`, `ARCH-2`
- [ ] At least one DFD exists with Draw.io/XML source
- [ ] Every meaningful data movement has a DFD
- [ ] Multiple user groups with materially different actors, permissions, or data paths are split into separate DFD coverage
- [ ] Draw.io/XML source exists for each required DFD and uses DFD notation matching the architecture example
- [ ] External actors, processes, data stores, and labeled data flows are all present and cross-checked against the text inventory
- [ ] DFD connector routing is clear: arrows do not run through shapes / containers, and unavoidable crossings use arc line jumps (`jumpStyle=arc`)
- [ ] All critical business flows are described
- [ ] Source of truth is explicit
- [ ] Consistency and recovery behavior are documented
- [ ] Sensitive data handling is visible
