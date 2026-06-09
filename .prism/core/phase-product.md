# Phase Engine: Product

## Trigger

`start product` — entry point, no prerequisites.

If the user wants to revise an already APPROVED Product package inside the current open sprint, do **not** use `start product`. Use `start change:` instead.

## Behavior

1. **Proactive Interrogation**: Ask ALL necessary questions BEFORE writing the Product package. Batch related questions into a clear grouped round, but do **not** assume one round is enough. After each answer batch, analyze whether the answers reveal follow-up questions, contradictions, or missing context; ask another grouped follow-up round when needed. Continue until no material blocker questions remain. Before drafting, ask one final open question: "Bạn muốn bổ sung gì nữa không?"

   **Industry detection (run FIRST per Principle 17 — Domain-Informed Inquiry)**: Before formulating the question categories below, scan the user's description for **industry vertical** signals (keywords, target users, regulatory hints, payment patterns, integration mentions). If detected (e.g., banking, ticketing, healthcare, e-commerce, logistics, edtech, fintech, gaming), state the detected vertical explicitly: *"Tôi nhận diện đây thuộc ngành {vertical} — sẽ áp dụng lăng kính senior practitioner ngành đó bên cạnh PRD craft (Cagan-style)."* Then surface 5–10 **industry-common checklist items** as confirm/reject questions BEFORE the general categories — covering features, lifecycle states, compliance categories, peak-load patterns, common failure modes, integration patterns typical to that vertical. Tag each surfaced item with confidence: `[industry-standard]` / `[common]` / `[niche]`. NEVER assert specific regulation numbers, standard codes, or domain rules as fact from memory/training data. For volatile legal/regulatory/domain-rule candidates, consult current authoritative sources when available; if not verified this turn, label the item `unverified-current-source` and ask the user to confirm with their compliance/domain owner only if needed. Confirmed items become FR / BR / NFR / Open Risk; rejected go away; unconfirmed-but-noted go to `## Open Questions`. If detection ambiguous (cross-domain product, no clear signal): ask "Đây thuộc ngành/vertical nào? Để áp dụng đúng lăng kính practitioner ngành đó."

2. **Question categories** (ask comprehensively):

   - **Business context**: What specific problem are users experiencing today — with a measurable impact (hours lost, error rate, revenue drop)? Who is the customer segment (company size, industry, role)? What is the market context (existing solution, switching trigger)?
     - *Depth probe*: "Describe one day in the user's life WITHOUT your product. What specifically goes wrong, and how often?"
     - *Reject vague*: "Cần hệ thống tốt hơn" / "Cải thiện quy trình" → ask: "Hiện tại user mất bao nhiêu thời gian/bước/lần lỗi để làm việc này?"

   - **Users**: How many users? What is their tech level (High/Medium/Low with criteria)? What do they do today without the product? Who are secondary personas and what is their relationship to primary?
     - *Depth probe*: "Describe your primary persona in 3 sentences: role + company size + what they do manually today that your product will replace."
     - *Reject vague*: "Người dùng là manager và employee" → ask: "Bao nhiêu manager? Bao nhiêu employee per manager? Tech level của họ như thế nào?"

   - **Features**: Name each Must Have feature as a single user action with an expected outcome. Apply MoSCoW per feature. No categories or groups — each feature is one actionable capability.
     - *Depth probe*: "Give me the top 3 Must Have features. Format each as: 'As [user], when I [action], I expect [specific outcome within X seconds].'"
     - *Reject vague*: "Quản lý đơn hàng" / "Hệ thống báo cáo" → ask: "Đây là nhóm chức năng — liệt kê từng tính năng cụ thể: user làm gì, hệ thống phản hồi gì?"

   - **Entity lifecycle & state transitions**: Which business entities have meaningful lifecycle states (order, subscription, refund, approval item, invoice, support ticket, etc.)? What states exist, what triggers each transition, which transitions are invalid, and are there timeout / expiry / cancel / retry / escalation rules?
     - *Depth probe*: "List 1–3 key entities. For each entity: current states, transition trigger, invalid transitions, and any timeout / expiry rule."
     - *Reject vague*: "Đơn hàng có nhiều trạng thái" → ask: "Cụ thể là gì? Ví dụ `PENDING -> CONFIRMED -> SHIPPED -> DELIVERED`; transition nào bị cấm, và timeout / cancel sau bao lâu?"

   - **Non-Functional Requirements**: p95/p99 latency target? How many concurrent users at peak? Uptime target (99%, 99.9%, 99.99%)? Any compliance (GDPR, PCI-DSS, ISO 27001, SOC 2)? Mobile/accessibility requirements?
     - *Depth probe*: "Fill in this sentence: 'At peak load of ___ concurrent users, p95 API response must be ≤ ___ ms, with uptime ≥ ___%.'"
     - *Probe vague*: "Performance cần tốt" / "Phải bảo mật" / "Cần ổn định" → re-ask with suggestion: "Những mô tả này chưa có số — tôi không thể thiết kế từ đó. Nếu chưa rõ, baseline phổ biến cho web SaaS: p95 ≤ 500ms, 99.9% uptime, 200 concurrent users. Dùng tạm không, hay có target khác? Nếu muốn skip, tôi sẽ ghi TBD và flag là open risk."

   - **Constraints**: Hard launch date? Fixed team size and composition? Regional/regulatory requirements? Mandatory tech stack (existing infrastructure, vendor lock-in)? Budget ceiling?
     - *Depth probe*: "What is the hard deadline? Is it negotiable? What happens if we miss it?"
     - *Reject vague*: "Budget flexible, timeline roughly 6 months" → ask: "Ngày ra mắt cứng là ngày nào? Số lượng engineer? Có ràng buộc tech stack từ hạ tầng hiện tại không?"

   - **Integrations**: Hệ thống nào cần tích hợp? Hướng dữ liệu (đẩy ra / nhận vào / hai chiều)? Realtime hay batch? Owner của hệ thống bên kia? Có SLA cam kết? *(Chi tiết kĩ thuật — protocol cụ thể, field-level mapping, mã lỗi, retry — thuộc phase Architecture; mã / dữ liệu test thuộc phase Test.)*
     - *Depth probe*: "For each integration: (1) Tên hệ thống? (2) Hướng dữ liệu? (3) Realtime hay batch? (4) Owner & SLA?"
     - *Reject vague*: "Tích hợp với hệ thống HR hiện tại" → ask: "Hệ thống HR cụ thể là gì? Ai sở hữu? Hướng dữ liệu nào? Realtime hay batch?"

   - **KPIs**: What is the current baseline metric? What is the target? By when? Who owns measurement? What is the minimum acceptable outcome (vs. stretch goal)?
     - *Depth probe*: "Fill in: 'Currently [metric] is [baseline]. We want it to be [target] within [timeframe], measured by [who/tool].'"
     - *Probe vague*: "Cải thiện hiệu quả" / "Tăng user satisfaction" → re-ask with suggestion: "Đây chưa phải KPI đo được. Thử format này: 'Hiện tại [process X] mất [Y phút/bước]. Chúng ta muốn giảm xuống [Z] trong [N tháng].' Nếu chưa có baseline, hãy liệt kê 1 metric bạn đang theo dõi — dù thô. Nếu muốn skip KPIs bây giờ, tôi sẽ ghi TBD."

3. **Probe vague answers — Suggest, don't just reject**: If a user answer is vague (no numbers for NFR/KPI, no specific feature action, no concrete constraint), do NOT simply reject. Instead:
   - Re-ask with a specific probe AND offer concrete defaults/examples as suggestions.
   - Example for vague NFR: "Performance cần tốt thôi" → respond: "Tôi cần con số cụ thể để thiết kế. Nếu bạn chưa biết, đây là baseline phổ biến cho hệ thống web B2B: p95 API response ≤ 500ms, 99.9% uptime, 200 concurrent users. Dùng tạm những con số này không, hay bạn có target khác?"
   - Example for vague KPI: "Tăng hiệu quả" → respond: "KPI cần có baseline và target. Nếu chưa rõ, bạn có thể cung cấp một metric bất kỳ đang đo được hiện tại không? Ví dụ: thời gian xử lý đơn hàng, tỷ lệ lỗi, số lần phải can thiệp thủ công?"
   - **User says "skip" or "không biết" — NFR / KPI / non-functional constraint scope only**: Accept it gracefully. Record as `TBD — [topic]` with an open risk note: "Chưa có NFR/KPI này → sẽ flag là open risk trong PRD, cần xác nhận trước Architecture phase." Do NOT block or repeat the probe.
   - **User says "skip" or "không biết" — FR / AC / persona / scope / testability / traceability scope**: do NOT write `TBD`. Treat it as "FR/AC chưa có" and capture the idea in `## Open Questions` (or PRD's pending discussion section) with: what was raised, why it cannot be resolved now, who needs to weigh in. Do not invent a placeholder FR-xxx or AC for it. The corresponding user story (if any) does NOT satisfy the Story Readiness Rule and cannot be Must Have until the FR / AC are concrete.
   - **User confirms a default**: Accept it, note "Provisional target — needs validation" in the artifact.

4. **Cross-validation after interrogation round** (run before writing): After collecting all answers, scan for internal contradictions before starting to write. Flag and ask about any obvious conflict:
   - Very low user count (< 100 DAU) + very high availability (99.99%) → cost contradiction, flag it.
   - "Timeline: 1 month" + "Must Have features": more than 5–6 complex features → scope contradiction, flag it.
   - "No budget" + "Compliance: PCI-DSS" → budget contradiction (compliance has mandatory cost), flag it.
   - "No integrations" in questionnaire but Product involves existing users/data → flag to confirm.
   - If conflict found: present it clearly and ask user to resolve before writing. Don't silently proceed.

5. **Enterprise standards**: NEVER **assert** compliance requirements, naming conventions, or domain-specific rules as fact. But DO apply Principle 17 (Domain-Informed Inquiry): once industry vertical is detected, surface industry-common compliance / naming / domain-rule candidates as confirm/reject questions with confidence tags `[industry-standard]` / `[common]` / `[niche]`. For rules that may change by date, region, regulator, league, or standards body, check current authoritative sources when available before naming the rule. Example: instead of writing "Project requires Regulation-XYZ KYC" as a FR, ask: *"Banking products often have KYC / AML / customer-due-diligence obligations. I can verify the current VN-specific rule set from authoritative sources before drafting; should this project include KYC/AML scope, or is it out of scope?"* Confirmed answers become FR / NFR; unconfirmed go to `## Open Questions`. If detection unclear → ask specifically.

6. **After sufficient info**: Run the shared self-check in `core/phase-quality-standards.md` plus the completeness / consistency checks in step 4 → output the complete Product package in one pass.

7. **Mid-way discovery**: If discovering missing info while writing → STOP → ask user for the specific missing pieces before continuing.

8. **Story readiness rule (`PROD-1`, hard rule)**: Every Must Have user story in product split proposals under `product/proposals/` (the active sprint's slice) plus carried-over Must stories from `/docs/product/epics/EP-NNN-{slug}.md` MUST have:
   - explicit `persona` reference (matching `/docs/product/personas.md`)
   - acceptance criteria (`AC`) written in Given / When / Then or equivalent testable form
   - clear `scope` boundary (in / out)
   - `testability` note: how this AC can be verified (manual or automated, observable signal)
   - `traceability` to one or more `FR-xxx` IDs and any `NFR-xxx` IDs the story depends on

   A Must Have story missing any of these blocks `approve product`. Should-Have / Could-Have stories should follow the same rule but missing fields are recorded as open risk instead of hard block.

9. **Open risk rule for vague KPI / NFR / TBD (`PROD-2`)**: Whenever a KPI, NFR, or constraint cannot be made measurable in this phase, do not silently leave `TBD`. Add an explicit row to the Product package's `## Open Risks` section (or PRD risks section) with:
   - what is missing
   - why it matters downstream (Architecture / Test / Implement impact)
   - who validates it and by when
   - what default was used (if any) as a placeholder

   Vague KPI / NFR / important constraint left without an open risk entry blocks `approve product`.

10. **Entity lifecycle state rule (`PROD-3`, hard rule)**: Product does not need a separate state diagram, but every business entity with meaningful lifecycle state MUST have a concrete state-machine / lifecycle-state definition in the Product package. For each lifecycle entity, define:
   - state names
   - valid transitions (`FROM -> TO`)
   - trigger / actor / condition for each transition
   - invalid transitions that must be blocked
   - timeout / expiry / cancel / retry / escalation rules where applicable
   - affected `BR-xxx`, `FR-xxx`, and `US-xxx` references where known

   In guided 2-tier output, lifecycle-state definitions that belong in the Product PRD MUST be emitted as anchored `BR-NNN` items in `product/proposals/prd-v{X}.md`, because `BR-NNN` is the mergeable PRD route. Do not leave lifecycle state machines as unanchored prose that cannot be sealed into Living Truth.

   If the product has no meaningful lifecycle entities, state `N/A — stateless / no meaningful lifecycle` with a short reason. Vague lifecycle statements such as "has many statuses" or missing triggers / invalid transitions block `approve product`.

11. **Product traceability map rule (`PROD-4`, hard rule)**: Every `EP-NNN` epic block in the Product package MUST include a `Product Traceability Map` table that makes `EP -> FR -> related US` visible at a glance. The table MUST include:
   - one row per `FR-xxx` owned by that epic
   - the owning `EP-xxx`
   - related `US-xxx` IDs that cover the FR
   - priority / coverage status
   - notes for non-Must / deferred accepted gaps, with reason and owner

   Every Must Have FR must map to at least one Must Have user story in this table. Accepted gaps are allowed only for non-Must or explicitly deferred FRs. Missing table, missing FR row, stale FR/US references, or a Must Have FR without Must Have US coverage blocks `approve product`.

## Input Context

- Required: `prism-config.md`
- Effective Truth (composed at read time, per `core/version-manager.md § Effective Truth`): product Living Truth tree + earlier UNSEALED sprints' APPROVED split proposals + their APPROVED change-pack deltas. Compose via `python .prism/core/tools/effective_truth.py --phase product --up-to-sprint v{X}`.
- Optional (via inbox): `product.md`, `epics.md`, `user-stories.md`, `glossary.md`, `personas.md`, `market-research.md`, `product-assets/` — mapped into the standard Product package per `import-validator.md`
- NEVER load: design, architecture, implementation, test docs

## Output

Written to `/docs/sprint-v{X}/product/`:

| File | Template | Content | Lifecycle |
|------|----------|---------|-----------|
| `sprint-brief-v{X}.md` | N/A | PO rationale, scope summary, reviewer notes, **AND** mandatory `## Industry Lens Applied (PROD-5)` section in guided mode (see structure below). Not merged into Living Truth. | Sprint-only |
| `proposals/prd-v{X}.md` | `core/templates/proposal-template.md` | `BR-NNN` items + the singleton `PRD-OVERVIEW-001` narrative block (including lifecycle-state business rules required by `PROD-3`). | Routes to `/docs/product/prd.md` at sprint seal |
| `proposals/glossary-v{X}.md` | `core/templates/proposal-template.md` | `GLOSS-NNN` items only. | Routes to `/docs/product/glossary.md` |
| `proposals/personas-v{X}.md` | `core/templates/proposal-template.md` | `PERSONA-NNN` items only. | Routes to `/docs/product/personas.md` |
| `proposals/market-research-v{X}.md` | `core/templates/proposal-template.md` | `MR-NNN` items only. | Routes to `/docs/product/market-research.md` |
| `proposals/epics/EP-NNN-{slug}-v{X}.md` | `core/templates/proposal-template.md` | `EP/FR/US/AC` items for one epic. EP block includes the `PROD-4` Product Traceability Map. FR/US require `<!-- EPIC: EP-XXX -->`; AC requires `<!-- US: US-XXX -->`. | Routes to `/docs/product/epics/EP-NNN-{slug}.md` |

**PRD narrative (`PRD-OVERVIEW-001`).** The PRD's overview prose — Executive Summary, vision, problem statement, goals/success metrics, scope, assumptions, dependencies, risks — is NOT left as template scaffolding and is NOT the (never-merged) sprint brief. It is authored as ONE singleton anchored block in `proposals/prd-v{X}.md`:

```md
## New
<!-- ID: PRD-OVERVIEW-001 -->
### Product Overview
#### Executive Summary
...
#### Problem Statement
...
```

In sprint 1 it is a `## New` item; in later sprints it is a `## Updated` item that replaces the block in place. The ID is ALWAYS `PRD-OVERVIEW-001` (singleton — never increment, never renumber) so links from other docs/code stay stable. This is what makes the PRD overview live in `/docs/product/prd.md` instead of being stranded in the brief. Architecture and Design have the parallel singletons `ARCH-OVERVIEW-001` (→ `architecture.md`) and `DESIGN-OVERVIEW-001` (→ `design-system.md`).

If product assets are provided, copy them to `/docs/sprint-v{X}/product/assets/` and reference them from the relevant proposal or sprint brief.

Sprint v1 bootstrap: when root product LT files do not yet exist, `seal_sprint.py` creates `/docs/product/prd.md`, `glossary.md`, `personas.md`, and `market-research.md` from their templates as the initial preamble + merges split proposal `## New` items by ID prefix. New `/docs/product/epics/EP-NNN-{slug}.md` files are bootstrapped on demand from the EP block in an epic proposal.

For sprint-v{X>1}, AI NEVER writes `/docs/product/*.md` or `/docs/product/epics/EP-NNN-{slug}.md` directly. All updates flow through product split proposals. The pre-commit hook (`core/tools/precommit_living_truth.py`) blocks accidental direct edits.

### Product Proposal Routing Self-Check

Before writing or approving product output, the AI MUST verify these numbered rules:

1. `PROD-RT-1`: product mergeable sprint output is split under `product/proposals/` by LT target.
2. `PROD-RT-2`: BR items + the singleton `PRD-OVERVIEW-001` narrative block route to `/docs/product/prd.md`; GLOSS / PERSONA / MR items route to their matching product LT files.
3. `PROD-RT-3`: every EP item uses `EP-NNN` and creates/updates `/docs/product/epics/EP-NNN-{slug}.md`.
4. `PROD-RT-4`: every FR / US item has `<!-- EPIC: EP-NNN -->`.
5. `PROD-RT-5`: every AC item has `<!-- US: US-NNN -->`; new AC items append at the end of that US block, not at the end of the epic file.
6. `PROD-RT-6`: `python .prism/core/tools/validate_proposal.py --file <each product proposal>` must return 0 blockers before product approval, for example `--file docs/sprint-v{X}/product/proposals/prd-v{X}.md`.
7. `PROD-RT-7`: any proposal that adds, updates, or removes FR / US items for an existing epic must also update that epic's `EP-NNN` block when the `PROD-4` Product Traceability Map rows change; otherwise the epic proposal is stale.

Product artifacts must also satisfy the compact Quality Contract where applicable: `DOC-1` numbered review-ready structure, `DOC-2` stable item IDs, `DOC-3` required template section coverage, `LINK-1` concrete cross-links, `LINK-2` explicit dependency / open-risk context, `ORB-1` sprint context, `PROD-1` story readiness, `PROD-2` explicit open risks for vague KPI / NFR / important constraints, `PROD-3` lifecycle-state coverage where lifecycle entities exist, `PROD-4` Product Traceability Map coverage for every epic, and `PROD-5` Industry Lens Evidence (guided: sprint-brief; freedom: in-chat / artifact-local note).

### Sprint-Brief Industry Lens Section (`PROD-5`)

In guided mode, every `sprint-brief-v{X}.md` MUST contain this section verbatim (header + all five fields), populated by the AI when Principle 17 (Domain-Informed Inquiry) fires at the start of the Product phase. In freedom mode, record the same fields in-chat or in the local product artifact; no sprint-brief gate exists. Fields capture the self-check declaration so it becomes reviewable evidence, not just transient reasoning.

```markdown
## Industry Lens Applied (PROD-5)

- Detected vertical: <vertical name, e.g., "banking" / "ticketing" / "healthcare"; or "none — baseline" if no clear signal>
- Detection confidence: <high | medium | low>
- Items surfaced: <N> [industry-standard] / <M> [common] / <K> [niche]
- Region-specific items global-only: <count> — <brief list, or "none">
- Cross-domain tension: <"yes" + 1-sentence describe, or "no">
```

Rules:
- All five fields are MANDATORY. `TBD`, `?`, blank, or missing-line blocks `approve product`.
- When `Detected vertical = none — baseline`: counts default to `0 / 0 / 0`, region-only = `0 — none`, cross-domain = `no`. The section is still required — it documents that the principle fired and explicitly chose to fall back. Silent omission is not allowed.
- Items reported under `[industry-standard]` / `[common]` / `[niche]` in the section count MUST appear with matching tags somewhere in the PRD body (BR / FR / US items, or `## Open Questions` for unconfirmed surfaces). Inconsistency (e.g., declares 3 [industry-standard] but PRD has 0) is a `PROD-5` blocker.
- Region-only / volatile-rule items must include either a current-source verification note or the marker `unverified-current-source` when no authoritative source was verified this turn.
- See Principle 17 (`adapters/shared/guided.md` § Core Principles) and the `PROD-5` rule in `core/phase-quality-standards.md § Product Standard § Must Be True` for the full rule contract.

### Cross-sprint deltas (sprint-v{X} with `X > 1`)

There is no separate `changelog-v{X}.md` file. Cross-sprint differences live inside product split proposals (`## New` / `## Updated` / `## Removed` sections) per the 2-tier model in `core/version-manager.md § Living Truth`. `sprint-brief-v{X}.md` captures PO rationale / why for the sprint.

At sprint seal (`approve implement`), `seal_sprint.py` merges these proposals into the Living Truth files (`/docs/product/prd.md`, `/docs/product/epics/EP-NNN-{slug}.md`). Per `core/tools/precommit_living_truth.py`, AI must NEVER touch the Living Truth files directly — all updates flow through proposals.

## Gate

PO / Stakeholder reviews → `validate user story` → `approve product` or `feedback: [...]`

`approve product` is blocked if any of the following are true:

- a Must Have user story violates `PROD-1` (missing `persona`, `AC`, `scope`, `testability`, or `traceability` to FR / NFR)
- a Must Have FR cannot be mapped to at least one Must Have user story
- an epic lacks the `PROD-4` Product Traceability Map, or the map is missing / stale for any FR / US relationship
- a KPI / NFR / important constraint is vague or `TBD` and has not been recorded as an explicit open risk per `PROD-2`
- a business entity has meaningful lifecycle states but the Product package lacks a concrete lifecycle-state definition per `PROD-3`
- the active `validate user story` file is missing, stale, or its latest explicit result still contains `blocker`-level findings (see `core/orchestrator.md § Validate Active Files`)
- `python .prism/core/tools/validate_proposal.py --file <each product proposal>` returns any blocker (e.g., duplicate IDs, malformed frontmatter, missing anchor on an item, or wrong prefix for the split target)

## Validate User Story Command

`validate user story` is a user-invoked audit command. It runs read-only against product artifacts, produces a structured report, and writes or updates the active validate file for this command (named per `core/orchestrator.md § Validate Active Files`). It must be run on the current DRAFT before `approve product` and re-run after any `feedback:` that materially changes user stories, FR mapping, Product Traceability Map rows, AC, persona links, lifecycle-state rules, or KPI / NFR fields.

During normal Product generation, the engine must already self-apply the same readiness logic (story completeness, cross-package consistency, KPI/NFR clarity) before outputting the draft.

`approve product` requires that active validate file to already be present and clean, then re-runs `validate user story` in console-only mode as a final full confirmation pass. If that approval-time run finds any blocker or material gap, do not approve; show the findings to the user first and ask whether they want to update the active validate file into a follow-up checklist.

### Scope

Product split proposals under `docs/sprint-v{X}/product/proposals/` are the primary subject, but the command MUST cross-check against the **effective truth** for the product phase — composed at read time via `effective_truth.py --phase product --up-to-sprint v{X}`. The composed view includes:

- `/docs/product/prd.md` (Living Truth, plus active sprint's product split proposals merged in-memory) — KPIs, business rules, constraints, scope, and MoSCoW priorities (anchored mainly as `BR-NNN`)
- `/docs/product/glossary.md` — terminology and domain language consistency
- `/docs/product/personas.md` — persona references match real persona definitions
- `/docs/product/market-research.md` — target segment, evidence behind Must Have priorities

### Checks (per Must Have user story)

1. `persona` field is present and matches a persona defined in `/docs/product/personas.md`
2. `AC` section is present and uses Given / When / Then or equivalent testable form
3. `scope` is explicit (in / out boundaries)
4. `testability` field describes how the AC can be observed (manual / automated, visible signal, data condition)
5. `traceability` lists at least one `FR-xxx` (anchored item in `/docs/product/epics/EP-NNN-{slug}.md` effective truth or NEW in this sprint's epic proposal) and any `NFR-xxx` it depends on
6. terminology used in story matches `/docs/product/glossary.md`; flag drift
7. story does not contradict KPI / persona / market evidence in the Product package

### Cross-package checks

- `DOC-3`: required sections / fields from every Product template are present or explicitly marked N/A with reason.
- `VAL-1`: the active validate file records structural coverage and rule coverage for `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `PROD-1`, `PROD-2`, `PROD-3`, and `PROD-4`.
- `PROD-3`: every lifecycle entity in the Product package has concrete states, valid transitions, triggers, invalid transitions, timeout / expiry / cancel / retry / escalation rules where applicable, or the package explicitly states `N/A — stateless / no meaningful lifecycle` with reason.
- `PROD-4`: every epic has a `Product Traceability Map` table with one row per FR, valid EP / FR / US IDs, and every Must Have FR maps to at least one Must Have US.
- **Proposal structure check**: run `python .prism/core/tools/validate_proposal.py --file <each product proposal>`. Any blocker (malformed anchors, duplicate IDs, missing required frontmatter keys, missing routing tags, wrong split-target prefix) blocks `approve product`; Updated/Removed target existence is confirmed by `seal_sprint.py` against routed LT files.
- every Must Have FR (anchored in product effective truth or NEW in this sprint's epic proposal) is referenced by at least one Must Have user story
- every story persona reference resolves in `/docs/product/personas.md`
- KPIs / NFRs that stories depend on exist in the product effective truth (`/docs/product/prd.md` Living Truth or NEW in this sprint's PRD proposal), or are flagged as open risk
- glossary terms used across stories / PRD / epics are consistent

### Output

Produce a structured report ordered from `blocker` to `info`:

```text
validate user story: product split proposals + effective truth (/docs/product/epics/EP-NNN-{slug}.md + active sprint slice)
━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ PROD-1 Story Readiness Rule: passed for N / M Must Have stories
✓ PROD-4 Product Traceability Map: passed for N / N epics
✓ Proposal structure: product proposal anchors valid, no duplicate IDs, all Updated/Removed targets resolve in /docs/product/prd.md
✗ blocker [PROD-1]: US-014 missing persona reference
✗ blocker [PROD-1]: FR-022 has no Must Have user story
✗ blocker [PROD-4]: EP-003 Product Traceability Map missing FR-022 row
✗ blocker [VP-3]: epic proposal duplicate ID FR-014 in ## Updated and ## Removed
⚠ warn [PROD-1]: US-019 AC is narrative, not Given / When / Then
ℹ info:    glossary term "approver" used in 3 stories — confirm canonical form

→ Run `feedback: [your changes]` to fix
→ Re-run `validate user story` after feedback
→ Then `approve product`
```

The active validate file is named and lifecycled per `core/orchestrator.md § Validate Active Files` (cycle-scoped: `validate-user-story-<cycle>.md` in `tempo/in-progress/` while running, sealed and moved to `tempo/completed/` on approval success). `approve product` reads that file's latest explicit result, freshness marker, and approval-time re-run outcome to decide whether to allow approval.

## Same-Sprint Change Handling

- If Product is still `DRAFT`, absorb revisions through normal `feedback:`.
- If Product is `APPROVED` and the sprint is still open, Product corrections use `start change:`.
- If downstream phases have not started yet, they will read Product's effective truth when they start.
- If downstream phases already exist, `core/change-propagation.md` decides whether they absorb the change via feedback or delta.

## Quality Standard

Write like **Marty Cagan** — outcome-focused, user-centric, measurable. Produce a coherent Product package, not a loose set of disconnected files. Operational rules:

1. **Problem before solution** — every feature must state the user problem it solves with measurable impact. "Users need X" is not acceptable; "Users currently spend Y hours doing Z manually, causing [consequence]" is.
2. **Numbers, not adjectives** — every NFR and KPI must have a concrete target (latency in ms, concurrent users, uptime %, baseline metric). "Fast", "secure", "reliable" are not NFRs.
3. **Measurable AC** — every user story AC must describe exact observable behavior (redirect destination, exact error text, precise UI state), not "show success message" or "redirect to page".
4. **Explicit prioritization** — MoSCoW per feature. No feature is implicitly "important" — Must / Should / Could / Won't must be stated. If the user hasn't decided → ask, don't assume Must Have.
5. **Assumptions surfaced** — any decision made with incomplete information gets an inline `> Assumption: [...] / Validate: [...] / Change trigger: [...]` block, not a silent assumption baked into the requirement.
