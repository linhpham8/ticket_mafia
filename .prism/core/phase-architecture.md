# Phase Engine: Architecture

## Trigger

`start arch` — requires: product phase APPROVED.

**Runs PARALLEL with Design phase.** Implementation only begins when BOTH Design and Architecture are approved.

## Behavior

1. Read the approved Product package thoroughly.

2. **Search Before Building**: Before designing any component, check if proven solutions exist. Three knowledge layers:
   - Tried & true — proven patterns, battle-tested
   - New & popular — current best practices (scrutinize before adopting)
   - First principles — reason from the problem base when existing solutions don't fit

3. **Ask supplementary questions** — with probes and suggestions for vague answers. Batch related architecture questions into a clear grouped round, but do **not** assume one round is enough. After each answer batch, analyze whether the answers reveal follow-up questions, contradictions, or missing architecture context; ask another grouped follow-up round when needed. Continue until no material blocker questions remain. Before designing, ask one final open question: "Bạn muốn bổ sung gì về kiến trúc, hạ tầng, tích hợp, vận hành không?"

   **Industry lens (inherit from Product per Principle 17 — Domain-Informed Inquiry)**: Architecture starts AFTER Product APPROVED, so the vertical is already locked in `docs/sprint-v{X}/product/sprint-brief-v{X}.md § Industry Lens Applied (PROD-5)`. Read it; do NOT re-detect when the section exists. State the vertical explicitly: *"Industry vertical = {vertical from sprint-brief}. Applying senior architect lens for this domain alongside Martin Fowler craft (#8)."* Then surface **industry-typical architecture concerns** for that vertical as confirm/reject questions BEFORE the tech-stack questions — examples by vertical: banking → audit trail, ledger invariants, idempotent transactions, reconciliation, and whether service split / event sourcing is warranted; ticketing → queueing, cache strategy, anti-bot controls, idempotent payment, inventory holds; healthcare → audit log, PHI segregation, role-based PII access; logistics → workflow orchestration, geospatial indexing, eventual-consistency risk; edtech → CDN, offline-first, low-bandwidth fallback. Tag each with confidence `[industry-standard]` / `[common]` / `[niche]`. NEVER assert specific compliance numbers, SLA targets, or data-residency rules as fact — verify current authoritative sources when those obligations matter, then phrase as confirm/reject questions. Confirmed → architecture decisions / NFR / ADR; unconfirmed → `## Open Questions`. **Fallback**: if vertical = "none — baseline", skip the industry layer and proceed with baseline tech-stack questions. If the sprint-brief Industry Lens section is missing, stop and ask to backfill Product's Industry Lens before Architecture; do not silently invent or skip the vertical.
   - Tech stack preferences or constraints? *(If no preference → ask: "Team có kinh nghiệm gì? Có hạ tầng existing nào không?")*
   - Existing systems to integrate with? *(If "yes, some systems" → probe: "Tên cụ thể, protocol, có API doc chưa?")*
   - Are external integrations acting as `provider`, `listener`, or `bi-directional` flows? If a listener uses HTTP push, is there a webhook / callback contract? Is multi-partner abstraction needed?
   - Infrastructure: cloud provider, containerization, CI/CD? *(If "chưa quyết" → suggest: "AWS/GCP/Azure với Kubernetes là baseline phổ biến — dùng tạm không?")*
   - Performance targets: latency, throughput, concurrent users? *(If vague → suggest: "p95 ≤ 500ms, 200 concurrent users là baseline web SaaS — dùng tạm không? Hoặc muốn skip và flag TBD?")*
   - Security requirements: auth model, encryption, compliance?
   - Data residency or regulatory constraints?
   - Architecture style preference (Modular Monolith / Service-based / Microservices / EDA)? *(If unsure → recommend based on team size + scale: explain trade-offs, ask to confirm)*
   - Deployment context: internal-only or public-facing services? single or multi-instance?
   - Does this project include AI/ML or Agentic AI components?
   - Does this project include IoT components?
   - **Test frameworks** (chọn theo language stack): unit / integration / e2e / contract / mocking. Default suggestions:
     - Java/Kotlin → JUnit 5 + Mockito + Testcontainers
     - JS/TS backend → Jest hoặc Vitest + Supertest
     - JS/TS frontend → Jest/Vitest + Playwright (e2e) + Testing Library
     - Python → Pytest + pytest-mock
     - Dart/Flutter → flutter_test + mocktail
     - Swift native → Swift Testing / XCTest
     - Kotlin native (Android) → JUnit + MockK + Espresso
   - **Frontend error tracking** (web / mobile / mobile web): Sentry / Rollbar / Bugsnag — chọn 1 cho project. Source maps / dSYM / mapping.txt strategy? Mobile crash reporting?

   **Vague answer handling**: If any answer lacks specifics → re-ask with a concrete example OR offer a reasonable default. Accept "skip" or "not sure" gracefully — record as TBD with risk note. Do NOT block on missing answers.

   **Cross-validation after questions**: Before designing, check for obvious conflicts between the Product package NFRs and the supplementary answers:
   - NFR says 99.99% uptime → but deployment is single-instance? Flag: "Single-instance contradicts 99.99% uptime — needs HA design."
   - NFR says p95 < 200ms → but tech stack includes heavy ORM + no caching? Flag: "This latency target will be hard to meet without caching layer."
   - Security says PCI-DSS → but no dedicated infra? Flag: "PCI-DSS requires isolated cardholder data environment."
   - Present conflicts and ask user to confirm approach before designing.

4. **Load applicable company standards** via the standards INDEX before designing:
   - Resolve standards location: read `prism.json` → `paths.standards` (default `.prism/core/standards`).
   - Read `<paths.standards>/INDEX.md` first. If missing, halt and instruct the user to run `setup.sh` or check `prism.json`.
   - Load every "Always load" standard listed in INDEX (architecture principles, architecture solution, security, devsecops).
   - Load conditional standards per INDEX scope rules: backend coding when scope touches backend/API/DB/service contracts; frontend coding when project includes Web/Mobile; AI coding when project has AI/ML/Agentic; IoT only when confirmed by user.
   - Never bypass INDEX or load standards from web / training data.

5. **Artifact depth requirements — non-negotiable**:

   - **api-specs**: EVERY endpoint MUST have:
     - Request field schema table: field name / type / required / validation rule / default / example — not just a JSON blob
     - Response body schema table: field / type / always present / description — not "returns order object"
     - All standard HTTP error codes (400/401/403/404/409/422/429/500) with conditions
     - Error Code Catalog section: centralized list of all `error_code` values with status code + trigger condition
     - Inline `> Assumption:` block for any API contract decision not confirmed by PRD

   - **erd**: EVERY entity MUST have:
     - Full DDL: `CREATE TABLE` with column names, data types, constraints (NOT NULL / UNIQUE / CHECK), FK references — not just "key fields"
     - Naming conventions table (snake_case, UUID PK convention, FK naming, audit fields)
     - Indexing section: each index justified by a specific access pattern (not just "add index on FK")
     - Inline `> Assumption:` block for schema decisions where business rules are ambiguous

   - **sequence**: EVERY flow with multi-step DB writes MUST have:
     - `[TX BEGIN]` and `[TX COMMIT/ROLLBACK]` annotations marking transaction boundaries
     - `[TO: Xms]` for every external service call
     - `[RETRY: n, strategy]` for calls with retry intent
     - `[IDEMPOTENT: key=...]` for idempotent endpoints
     - `[ASYNC]` for fire-and-forget operations
     - Missing any of these on a qualifying flow → sequence is INCOMPLETE

   - **nfr**: EVERY NFR target must have:
     - A concrete number (no "system must be fast")
     - §8 Implementation Configuration Mapping: config key → recommended value → who sets it in application.yml / IaC
     - Architecturally Significant Scenario for each prioritized quality attribute

   - **events**: EVERY event must have:
     - Payload Schema table with field-level types (not `"data": {}` placeholder)
     - Kafka Contract (or equivalent messaging contract) with topic name, partition key, consumer group
     - DLQ Contract: DLQ topic name, alert owner, alert threshold

   - **project-reference**: `/docs/architecture/project-reference.md` MUST define:
     - source-of-truth document index for downstream teams
     - module / bounded-context map in code-facing terms
     - source-tree / package / namespace organization contract
     - public entrypoints and stable code surfaces
     - dependency / import boundaries
     - active naming conventions and update triggers
     - If a code-facing boundary exists in architecture but not in `/docs/architecture/project-reference.md`, the architecture package is incomplete

   - **C4 model**: `architecture-v{X}.md` MUST include a reviewer-readable C4 section with at least 3 C4 levels plus a Draw.io/XML source asset reference. Mermaid is not required for C4.
     - System Context: text-readable table + Draw.io/XML source reference
     - Container View: text-readable table + Draw.io/XML source reference
     - Component View: text-readable table + Draw.io/XML source reference
     - The Draw.io/XML source must describe the same actors, containers, components, and key relationships as the text-readable C4 summary.
     - Draw.io connector routing must follow the C4 example style: connectors may not cut across or run through containers / boundaries; avoid crossings where possible; when crossings are unavoidable, use arc line jumps (`jumpStyle=arc`) and keep labels readable.

   - **Data Flow Diagram (`ARCH-2`)**: `data-flow-v{X}.md` MUST include at least one DFD and cover meaningful data movement. Use the standard DFD notation from the architecture example:
     - external actor / system = rectangle
     - process = circle
     - data store = open-ended rectangle
     - data flow = labeled arrow
     - Draw.io/XML is the editable source of truth for DFD; Mermaid is not required.
     - Draw.io connector routing must be clear: data-flow arrows may not cut across or run through actors, processes, data stores, or containers / boundaries; avoid crossings where possible; when crossings are unavoidable, use arc line jumps (`jumpStyle=arc`).
     - When multiple user groups / personas have materially different actors, permissions, or data paths, split DFD coverage by user group instead of forcing one diagram.

6. **Batch output**: Before presenting the draft, run the shared self-check in `core/phase-quality-standards.md`, then produce the ENTIRE architecture package in one go — the overall architecture document plus all required supporting artifacts.

7. **Overall vs companion files**: `proposals/architecture-v{X}.md` is the overall architecture proposal that merges into `/docs/architecture/architecture.md` at sprint seal. It MUST summarize the system-wide shape and cross-reference the dedicated target proposal files. It MUST NOT absorb the detailed sequence, ERD, ADR, data-flow, API, event, or NFR content as a substitute for generating those files.

8. **Planning-ready architecture rule (`ARCH-1`, hard rule)**: The architecture package MUST be explicit enough that Plan can split task groups and Test can write cases without re-asking the architect. That means, before declaring DRAFT review-ready:
  - every Must Have FR appears in the traceability map **inside the `ARCH-OVERVIEW-001` block** (re-created via `## Updated ARCH-OVERVIEW-001` in sprint v>1 — never as preamble prose or a deferred TODO; content outside an anchored New/Updated block is dropped at seal) and can be traced to at least one component, API, sequence flow, and data ownership entry
  - integrations are classified (`provider` / `listener` / `bi-directional`) and have an explicit contract reference
  - NFR §8 Implementation Configuration Mapping is filled for each prioritized NFR target
  - bounded contexts and data ownership matrix are present when the architecture style requires them
  - text-readable C4 summary and Draw.io/XML C4 source references exist and agree for all 3 required levels: System Context, Container, and Component
  - at least one DFD Draw.io/XML source exists, every meaningful data flow is covered, materially different user-group flows are split by user group, and the source matches the text-readable data-flow inventory (`ARCH-2`)
  - `/docs/architecture/project-reference.md` exists and captures the code-facing project engineering contract downstream phases must consume
  - companion proposal files (`api-specs`, `erd`, `sequence`, `events`, `nfr`, `data-flow`, `adr`) cross-link back to `architecture-v{X}.md` and to each other; orphan artifacts are not allowed

   Failing the planning-ready rule blocks `approve arch`.

## Input Context

- Required: **Effective Truth** for the product phase (per `core/version-manager.md § Effective Truth`). Compose via `python .prism/core/tools/effective_truth.py --phase product --up-to-sprint v{X}`. The composed view contains the product Living Truth files merged in memory with active sprint's approved proposals + change-pack deltas.
- Optional: Design effective truth or current same-sprint Design working package if Design already exists. Architecture runs in parallel with Design, so missing or still-DRAFT Design must not block `start arch`; any UI / screen assumptions derived from non-approved Design are provisional and must be rechecked before `approve arch` if Design changes materially.
- Optional: architecture effective truth if revising an existing architecture proposal in the same sprint
- Optional (via inbox): `architecture.md`, `sad.md`, `project-reference.md`, `sequence.md`, `erd.md`, `adr.md`, `data-flow.md`, `api-specs.md`, `events.md`, `nfr.md`, `c4.md`, `arch-assets/`
- Prohibited inputs: sealed sprints' files (their content already lives in Living Truth — load Living Truth instead), other sprints' DRAFT proposals, snapshots folder (audit-only), implementation / test docs

## Output

Written to `/docs/sprint-v{X}/architecture/`:

| File | Template | Content | Lifecycle |
|------|----------|---------|-----------|
| `sprint-brief-v{X}.md` | N/A | Architecture rationale, decisions summary, reviewer notes. Not merged into Living Truth. | Sprint-only |
| `proposals/architecture-v{X}.md` | `core/templates/proposal-template.md` | `ARCH/ARCH-COMP` items + the singleton `ARCH-OVERVIEW-001` narrative block (Executive Summary: style, runtime, key trade-offs, system-wide shape). Authored `## New` in sprint 1, `## Updated` (replace in place, ID unchanged) later. | Routes to `/docs/architecture/architecture.md` |
| `proposals/project-reference-v{X}.md` | `core/templates/proposal-template.md` | `PR-NNN` project engineering contract items. | Routes to `/docs/architecture/project-reference.md` |
| `proposals/sequence-v{X}.md` | `core/templates/proposal-template.md` | `SEQ-NNN` sequence items. | Routes to `/docs/architecture/sequence.md` |
| `proposals/erd-v{X}.md` | `core/templates/proposal-template.md` | `ENT-NNN` entity items. | Routes to `/docs/architecture/erd.md` |
| `proposals/adr-v{X}.md` | `core/templates/proposal-template.md` | `ADR-NNN` decision items. | Routes to `/docs/architecture/adr.md` |
| `proposals/data-flow-v{X}.md` | `core/templates/proposal-template.md` | `FLOW-NNN` data-flow items. | Routes to `/docs/architecture/data-flow.md` |
| `proposals/api-specs-v{X}.md` | `core/templates/proposal-template.md` | `API-NNN` endpoint items. | Routes to `/docs/architecture/api-specs.md` |
| `proposals/events-v{X}.md` | `core/templates/proposal-template.md` | `EVT-NNN` event items. | Routes to `/docs/architecture/events.md` |
| `proposals/nfr-v{X}.md` | `core/templates/proposal-template.md` | `NFR-NNN` measurable requirement items. | Routes to `/docs/architecture/nfr.md` |

Sprint v1 bootstrap: when root architecture LT files do not yet exist, `seal_sprint.py` creates all architecture LT files from their templates as preamble + merges architecture split proposal `## New` items by ID prefix.

For sprint-v{X>1}, AI NEVER writes `/docs/architecture/*.md` directly — the pre-commit hook (`core/tools/precommit_living_truth.py`) blocks it.

Each architecture proposal must additionally pass `python .prism/core/tools/validate_proposal.py --file <each architecture proposal>`, for example `--file docs/sprint-v{X}/architecture/proposals/architecture-v{X}.md`.

The architecture proposal set must cover every applicable architecture LT area.

If an architecture area has no current data or does not apply in this scope (for example no persistent database, no event contract, or no separate data-flow concerns), state that explicitly in the proposal, explain why the area is absent or not applicable, and note any downstream impact or assumption the user accepted.

Store Draw.io / XML C4 and DFD sources under `/docs/sprint-v{X}/architecture/assets/` and reference them from the matching proposal (`proposals/architecture-v{X}.md` for C4, `proposals/data-flow-v{X}.md` for DFD); `sprint-brief-v{X}.md` may summarize the rationale but must not be the only diagram reference. Generated Draw.io files must use clear connector routing: no connector runs through a shape or container, unavoidable crossings use arc line jumps, and layout follows the relevant C4 / DFD example style as closely as possible. If the user does not provide a source asset, generate a minimal Draw.io/XML source or record a blocker-level open issue before approval.

The architecture package must satisfy `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ARCH-1`, and `ARCH-2`. Companion artifacts may use stable item IDs instead of fully numbered subsections when the artifact is a catalog, but orphan artifacts are not allowed.

## Gate

Architect / Tech Lead reviews → `validate architecture` → `approve arch` or `feedback: [...]`

`approve arch` is blocked if any of the following are true:

- Architecture violates `ARCH-1` (Planning-Ready Architecture Rule), including missing / inconsistent C4 text + Draw.io/XML coverage for the 3 required C4 levels
- Architecture violates `ARCH-2` (Data Flow Diagram Rule), including missing the minimum 1 Draw.io/XML DFD source, missing coverage for meaningful data movement, missing split DFD coverage for materially different user groups, or DFD notation that does not match the standard
- `python .prism/core/tools/validate_proposal.py --file <each architecture proposal>` returns any blocker, including missing / malformed anchors, duplicate IDs, wrong split-target prefixes, malformed frontmatter, unknown top-level merge sections, unmergeable H2 structure inside an anchored block, a `## New` `ARCH-COMP` without an accompanying `ARCH-OVERVIEW-001` New/Updated block (`VP-11`), or a table in the proposal preamble (`VP-12`)
- `python .prism/core/tools/validate_living_truth.py --effective --sprint v{X}` returns any blocker — a Must Have FR (product effective truth) missing from the merged `ARCH-OVERVIEW-001` traceability map (`LTV-COV`), or an `## Updated ARCH-OVERVIEW-001` regeneration that silently dropped a still-live traceability row (`LTV-SHRINK`). These run the deterministic `ARCH-1` coverage + no-shrink checks on the pre-seal effective truth, so drift is caught at approve, not deferred to seal.
- the active `validate architecture` file is missing, stale, or its latest explicit result still contains `blocker`-level findings in any of the three layers (`internal consistency`, `product fit`, `standards compliance`) — see `core/orchestrator.md § Validate Active Files`
- a selected or otherwise in-scope DRAFT change pack impacts Architecture and Architecture has not absorbed that change through:
  - `feedback:` if Architecture is still `DRAFT`, or
  - an Architecture delta if Architecture is already `APPROVED`

## Validate Architecture Command

`validate architecture` is a user-invoked audit command. It runs read-only against architecture artifacts, produces a structured report covering three independent layers, and writes or updates the active validate file for this command (named per `core/orchestrator.md § Validate Active Files`). It must be run on the current DRAFT before `approve arch` and re-run after any feedback or change-pack absorption that materially changes the architecture package.

During normal Architecture generation, the engine must already self-apply the same three-layer logic (internal consistency, product fit, standards compliance) before outputting the draft.

`approve arch` requires that active validate file to already be present and clean, then re-runs `validate architecture` in console-only mode as a final full confirmation pass. If that approval-time run finds any blocker or material gap, do not approve; show the findings to the user first and ask whether they want to update the active validate file into a follow-up checklist.

### Three layers

1. **Internal consistency** — the architecture package is self-consistent
2. **Product fit** — the architecture matches the approved Product package
3. **Standards compliance** — the architecture follows applicable company standards in `prism/core/standards/`

A `blocker`-level finding in any single layer is enough to block `approve arch`.

Fail-fast validation semantics:

- `validate architecture` MUST mark the run as `issues-found` and include at least one `blocker` finding when C4 is missing any required level: System Context, Container, or Component.
- `validate architecture` MUST mark the run as `issues-found` and include at least one `blocker` finding when any required C4 Draw.io/XML source reference is missing or contradicts the text-readable summary.
- `validate architecture` MUST mark the run as `issues-found` and include at least one `blocker [ARCH-2]` finding when `data-flow-v{X}.md` lacks at least one DFD Draw.io/XML source, lacks text-readable DFD inventory, misses a meaningful data movement, omits required DFD notation, has unlabeled arrows, or fails to split materially different user-group flows.
- `validate architecture` MUST NOT report `clean`, `pass`, or approval-ready while any of the above blockers exists.

### Layer 1: Internal consistency

Cross-check the architecture package files for agreement:

- **Proposal structure check**: run `python .prism/core/tools/validate_proposal.py --file <each architecture proposal>`. Any blocker (malformed anchors, duplicate IDs, missing required frontmatter keys, missing routing tags, unknown top-level merge sections, unmergeable H2s inside anchored blocks, or wrong split-target prefix) blocks `approve arch`; Updated/Removed target existence is confirmed by `seal_sprint.py` against routed LT files.
- `DOC-3`: required sections / fields from all Architecture templates are present or explicitly marked N/A with reason.
- `VAL-1`: the active validate file records structural coverage and rule coverage for `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ARCH-1`, and `ARCH-2`.
- C4 coverage: `architecture-v{X}.md` includes text-readable C4 and Draw.io/XML source references for all 3 required levels: System Context, Container, and Component. Draw.io connectors must not cut through containers / boundaries; unavoidable crossings use arc line jumps.
- DFD coverage: `data-flow-v{X}.md` includes a text-readable inventory plus at least one Draw.io/XML source, covers every meaningful data flow, splits materially different user-group flows by user group, and uses rectangles for actors, circles for processes, open-ended rectangles for data stores, and labeled arrows for data flows. Draw.io data-flow arrows must not cut through shapes; unavoidable crossings use arc line jumps.
- `LINK-1`: the architecture split proposal set cross-links every routed architecture area and every in-scope area has either substantive anchored content or an explicit no-current-data / not-applicable note
- `project-reference-v{X}.md` includes `PR-NNN` project-reference content, and those items reflect the same module / context names used in the overview
- entities in `/docs/architecture/erd.md` match entities referenced in `/docs/architecture/api-specs.md`, `/docs/architecture/sequence.md`, `/docs/architecture/data-flow.md`, and `/docs/architecture/events.md`
- endpoints in `/docs/architecture/api-specs.md` match the request / response payloads referenced in `/docs/architecture/sequence.md`
- transaction boundaries in `/docs/architecture/sequence.md` match the consistency expectations in `/docs/architecture/data-flow.md`
- event publishers / subscribers in `/docs/architecture/events.md` match the components in `architecture-v{X}.md`
- public entrypoints and stable code surfaces in `/docs/architecture/project-reference.md` match the APIs / events / jobs / component boundaries declared across the architecture package
- NFR targets in `/docs/architecture/nfr.md` are reflected in `architecture-v{X}.md` deployment / scaling decisions
- ADRs in `/docs/architecture/adr.md` cover every architecturally significant decision marked in `architecture-v{X}.md`

### Layer 2: Product fit

Doi chieu architecture package against the approved Product package:

- `ARCH-1`: every Must Have FR in `/docs/product/epics/EP-NNN-{slug}.md` appears in the Architecture Traceability Map and is covered by at least one component, API, sequence flow, and data owner
- every Must Have NFR in `/docs/product/prd.md` / `/docs/architecture/nfr.md` has a concrete architectural response (capacity, redundancy, observability, security)
- constraints in `/docs/product/prd.md` (regional, regulatory, infra, vendor) are reflected in deployment, integration, and security decisions
- integrations declared in Product (HR, payment, identity, etc.) appear in the architecture as named external systems with classification and contract references
- compliance requirements (PCI-DSS, GDPR, SOC 2, etc.) drive concrete architectural patterns (encryption, segregation, audit trail), not just narrative text
- key business flows from `/docs/product/epics/EP-NNN-{slug}.md` are realisable end-to-end on the architecture (component → API → DB → event → external as relevant)

### Layer 3: Standards compliance

Cross-check against the standards loaded earlier in step 4 — the always-load files plus the conditional files INDEX maps to the actual project scope (backend / frontend / AI / IoT). INDEX is the source of truth for which file applies when; do not maintain a parallel list here.

For each loaded standard, flag deviations as either:

- `blocker` — deviation from a mandatory rule with no ADR justifying it
- `warn` — deviation with ADR rationale but high downstream cost
- `info` — informational note about a soft preference

### Output

Produce a structured report grouped by layer and ordered from `blocker` to `info`:

```text
validate architecture: architecture split proposals + architecture effective truth (`/docs/architecture/*.md`)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Layer 1 — Internal consistency
✗ blocker [LINK-1]: events-v{X}.md publishes OrderCreated but no service in architecture-v{X}.md owns it
⚠ warn:    api-specs error catalog references error code AUTH-401 not used in any sequence

Layer 2 — Product fit
✗ blocker [ARCH-1]: FR-018 (refund flow) has no component / API / sequence coverage
⚠ warn:    NFR-002 p95 < 200ms — no caching layer in architecture-v{X}.md

Layer 3 — Standards compliance
✗ blocker: no mTLS between services — security-standards.md §4 requires mTLS for sensitive flows
ℹ info:    devsecops-standards.md recommends OpenTelemetry; architecture uses vendor APM

→ Run `feedback: [your changes]` to fix
→ Re-run `validate architecture` after feedback
→ Then `approve arch`
```

The active validate file is named and lifecycled per `core/orchestrator.md § Validate Active Files` (cycle-scoped: `validate-architecture-<cycle>.md` in `tempo/in-progress/` while running, sealed and moved to `tempo/completed/` on approval success). `approve arch` reads that file's latest explicit result, freshness marker, and approval-time re-run outcome to decide whether to allow approval.

## Same-Sprint Change Handling

- Architecture only receives forward propagation from upstream phases or direct architecture-originated changes.
- Do not pull an architecture correction backward into Product unless Product is actually impacted.
- If Architecture has not started, future `start arch` reads effective truth.
- If Architecture is `DRAFT`, merge via `feedback:`.
- If Architecture is `APPROVED`, use an Architecture delta in the selected change pack.

## Quality Standard

Architect like **Martin Fowler** — clear component boundaries, explicit trade-off documentation, text-readable architecture artifacts, diagrams that communicate, and ADRs that capture the "why." Operational rules:

1. **Evolutionary architecture** — design for replaceability. Every component boundary must be explicit enough that you could swap the implementation behind it without cascading changes.
2. **Testability by design** — every component must be individually testable. If you can't describe how to test a component in isolation, the boundary is wrong.
3. **Observability as a first-class requirement** — define the log format, correlation ID header, and key metric names BEFORE implementation starts. Logging, metrics, and alerting are not afterthoughts.
4. **Trade-offs documented, not asserted** — "We chose X" is not an ADR. "We chose X over Y because of [quality attribute], accepting the consequence of [trade-off]" is.

Artifact-depth requirements per file (api-specs / erd / sequence / events / nfr / project-reference / C4 / DFD) are enforced by the templates and Behavior step 5 — not duplicated here.
