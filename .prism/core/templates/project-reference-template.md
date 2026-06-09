---
status: DRAFT
version: v1
sprint: 1
phase: architecture
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# Project Reference — {{PROJECT_NAME}}

<!-- Living Truth root for project engineering contract. Each item (module, surface, naming
     convention, dependency rule) is a mergeable anchored block tagged PR-NNN. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each PR-NNN block (module entry, public surface, naming convention rule, dependency rule)
     MUST be preceded by `<!-- ID: PR-NNN -->` on its own line above the H3 heading.
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type PR`
     Strict format: `PR-\d{3,}` (zero-padded ≥3 digits). -->

<!-- PRISM:LT-SKELETON-END -->

File này là **project engineering contract** của architecture package. Nó gom lại code-facing structure mà Plan, Test, và Implement phải cùng đọc như một nguồn sự thật chung.

File này không thay cho `/docs/architecture/architecture.md`. `architecture.md` vẫn là package entrypoint tổng quan; file này tập trung vào module map, source tree contract, public entrypoints, dependency boundaries, naming, và stable code surfaces.

## 1. Ownership And Update Rules

| Field | Value |
|---|---|
| Owner | Architecture |
| Primary consumers | Plan, Test, Implement |
| Update while draft | `feedback architecture: ...` |
| Update after approval | same-sprint change pack / architecture delta |

**Update this file when:**

- module / bounded context boundaries change
- package / namespace / folder organization changes
- public entrypoints or stable code surfaces change
- dependency / import boundaries change
- active naming conventions change

## 2. Source-Of-Truth Index

### 2.1 Current Architecture Inputs And Companions

| Artifact | Path | Why It Matters |
|---|---|---|
| Product package | `/docs/product/prd.md`, `/docs/product/epics/EP-NNN-*.md`, `/docs/product/glossary.md`, `/docs/product/personas.md`, `/docs/product/market-research.md` | Requirement source of truth |
| Design | `/docs/design/design-system.md` | UI / state / interaction source of truth |
| Architecture overview | `/docs/architecture/architecture.md` | Overall system design entrypoint |
| API contracts | `/docs/architecture/api-specs.md` | HTTP / RPC contract surface |
| Data model | `/docs/architecture/erd.md` | Schema + ownership baseline |
| Runtime flows | `/docs/architecture/sequence.md` | Transaction / retry / async instructions |
| Events | `/docs/architecture/events.md` | Publisher / subscriber contract |
| NFRs | `/docs/architecture/nfr.md` | Measurable runtime / operations targets |
| ADRs | `/docs/architecture/adr.md` | Decision rationale and exceptions |

### 2.2 Downstream Consumers / Future Links

These files may not exist yet when Architecture is first drafted. Add exact paths when the downstream phase starts or imports usable material.

| Consumer | Expected Path | How It Uses This File |
|---|---|---|
| Test package | `/docs/testing/test-cases.md` (LT) + sprint-only `docs/sprint-v{X}/testing/test-plan-v{X}.md` | QA test intent, coverage, public entrypoint risk, and boundary-aware test scope |
| Plan | `docs/sprint-v{X}/planning/implementation-plan-v{X}.md` (sprint-only) | Execution breakdown, task-group module/package scope, allowed diff boundaries, and code-facing handoff |

## 3. Module And Context Map (anchored, mergeable)

<!-- Mỗi module / context = 1 anchored PR-NNN block. Bảng tổng quan ở §3.1 là VIEW. -->

<!-- ID: PR-NNN -->
### PR-NNN: {{Module / Context name}}

- **Purpose**: <!-- VD: Order placement, payment processing, inventory updates -->
- **Owns**: <!-- VD: Order aggregate, OrderEvent stream -->
- **Public Entrypoints**: <!-- API endpoints, event topics, UI surfaces consumed by other modules -->
- **Allowed dependencies**: <!-- VD: Catalog read API; Payment domain via Saga -->
- **Companion Refs**: <!-- ADR-NNN, SEQ-NNN, API-NNN refs from `/docs/architecture/*.md` -->

### 3.1 Module Map Summary

| Module / Context | Purpose | Owns | Public Entrypoints | Companion Refs |
|---|---|---|---|---|
| | | | | |

## 4. Source Tree And Package Organization

| Area | Path / Package | Purpose | Owner | Import / Dependency Rule |
|---|---|---|---|---|
| | | | | |

## 5. Public Entrypoints And Stable Code Surfaces

| Module | Surface | Type | Stability | References |
|---|---|---|---|---|
| | | API / Event / Job / UI / Migration | Public / Internal / Transitional | |

## 6. Dependency And Import Boundaries

| Consumer | Allowed Dependencies | Forbidden Shortcuts | Notes |
|---|---|---|---|
| | | | |

## 7. Active Naming And Structural Conventions

| Surface | Convention | Source |
|---|---|---|
| Module / context names | <!-- VD: Orders Context, Payment Module --> | `/docs/architecture/architecture.md` |
| Package / namespace names | <!-- VD: com.company.orders, apps/web/src/features/orders --> | repo convention / ADR |
| APIs | <!-- VD: `/api/v1/...`, kebab-case path --> | `coding-standards-backend.md` |
| JSON fields | <!-- VD: camelCase --> | `coding-standards-backend.md` |
| DB tables / columns | <!-- VD: snake_case + UUID PK --> | `/docs/architecture/erd.md` |
| Frontend folders | <!-- VD: feature-based structure --> | `coding-standards-frontend.md` |
| Events | <!-- VD: lowercase dot-separated topic names --> | `/docs/architecture/events.md` |
| Markdown artifacts | lowercase kebab-case + `-v{X}.md` suffix | `core/version-manager.md § Canonical Artifact Naming` |

## 8. Stable Change Triggers

| Trigger | Must Update Here? | Why |
|---|---|---|
| Add / remove module or bounded context | Yes | Module map and ownership changed |
| New public API / event / job | Yes | Public surface changed |
| Move code across package / folder boundary | Yes | Source tree contract changed |
| Rename internal helper only | Usually No | Not a contract change unless public surface moved |
| Change import / dependency rule | Yes | Boundary contract changed |

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ARCH-1`
- [ ] File này được link từ `/docs/architecture/architecture.md`
- [ ] Module / Context names khớp với `/docs/architecture/architecture.md`
- [ ] Public entrypoints khớp với `/docs/architecture/api-specs.md`, `/docs/architecture/events.md`, `/docs/architecture/sequence.md` khi áp dụng
- [ ] Source tree / package contract đủ rõ để Plan chọn `target modules / packages`
- [ ] Import / dependency boundaries đủ rõ để Implement bị audit drift
- [ ] Naming conventions chỉ ra đúng source standard / ADR đang active
- [ ] Module / package / namespace names không mâu thuẫn với repo-local naming conventions hoặc approved ADRs
- [ ] Markdown artifact naming follows `core/version-manager.md § Canonical Artifact Naming`
- [ ] Stable code surfaces không mâu thuẫn với architecture companion files
