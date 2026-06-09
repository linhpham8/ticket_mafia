# Phase Engine: Design

## Trigger

`start design` — requires: Product work already exists in the current sprint.

If Product is still `DRAFT`, Design may still start, but Design must remain `DRAFT` with `dependencies_pending: [product]` until Product is `APPROVED` and Product-validation markers are cleared.

**Runs PARALLEL with Architecture phase.** Architecture still waits for Product approval. Implementation only begins when BOTH Design and Architecture are approved.

## Behavior

1. Read the latest Product package thoroughly.
   - If Product is `APPROVED`, use Product's effective truth.
   - If Product is `DRAFT`, use the current working Product package and treat scope-sensitive design decisions as provisional.

2. **Ask before designing — with probes for vague answers**:

   **Industry lens (inherit from Product per Principle 17 — Domain-Informed Inquiry)**: Do NOT re-detect the vertical when Product has an `Industry Lens Applied (PROD-5)` section. Read `docs/sprint-v{X}/product/sprint-brief-v{X}.md § Industry Lens Applied (PROD-5)` for the detected vertical + confidence. State it: *"Industry vertical = {vertical from sprint-brief}. Applying senior-UX-lead lens for this domain alongside complete-flow + a11y craft (#8)."* Then surface **industry-typical UX patterns** for that vertical as confirm/reject questions BEFORE the general questions — examples by vertical: banking → 2FA flow, transaction confirmation with amount + recipient re-state + biometric, error states for failed payments / insufficient funds; ticketing → seat selector with concurrent-hold expiry countdown, queue waiting screen at peak demand, refund flow; healthcare → consent screen for PHI sharing, audit-visible action UI; e-commerce mobile-first VN → low-bandwidth image strategy, COD vs prepayment UX. Tag each with confidence `[industry-standard]` / `[common]` / `[niche]`. NEVER assert specific design-system / brand-guideline / regulation as fact — phrase as confirm/reject questions; verify current authoritative sources first when legal/regulatory UX obligations matter. Confirmed → design spec; unconfirmed → `## Open Questions`. **Fallback**: if Product is still DRAFT, do a provisional detection from the available Product DRAFT and flag it as `Provisional — supersede when Product approved`. If Product is APPROVED but the sprint-brief lacks `PROD-5`, stop and ask to backfill Product's Industry Lens before final Design.

   - Brand guidelines: colors, typography, logo usage, tone? *(If "chưa có brand" → ask whether to use a neutral baseline and record tone/copy as TBD.)*
   - Target platforms: web, mobile (iOS/Android), desktop? *(If mobile is in scope → probe: offline support? gesture navigation? notification pattern: push / in-app / email?)*
   - Accessibility requirements: WCAG level (A/AA/AAA/other)? *(If vague like "standard" → suggest WCAG AA baseline; probe for keyboard-only, screen reader, reduced motion, high-contrast needs.)*
   - Existing design system: Material, custom, none, or other? *(If custom → ask for the source of truth: Figma, Storybook, docs?)*
   - User research: any existing personas, journey maps, usability studies? *(If none → ask for best-known assumptions or highest-risk unknowns.)*

   **Vague answer handling**: Re-ask with a concrete example or offer a reasonable default. Accept `skip` / `not sure` gracefully — record as `TBD` with a risk note. Do not block unless the missing answer prevents a Must Have flow from being specified.

   **Cross-validation before writing**: If PRD / persona context conflicts with the design answers (e.g., mobile users in weak connectivity but no offline/fallback posture, or accessibility target vs animation-heavy interaction) → flag the contradiction and ask before writing.

3. **If Figma/design files available**: User imports them, AI validates consistency with PRD.

4. **Minimum coverage requirement — hard rule**: For EVERY Must Have FR from the current Product package:
   - ≥ 1 user flow showing the complete action path (from entry point to success/error state)
   - ≥ 1 wireframe description covering all 4 states: **Empty**, **Loading**, **Populated**, **Error**
   - ≥ 1 error state with exact copy (not "show error message" — the actual message text)
   - Missing any of these for a Must Have FR → design is INCOMPLETE, do not mark as ready for approval

5. **Depth requirements per artifact**:
   - **User flows**: Every decision point must document edge cases (What if user cancels? What if session expires mid-flow? What if the API call fails?)
   - **Wireframe descriptions**: Each state must specify heading text, subtext, primary CTA label, and how the state visually differs from adjacent states — not just "show loading spinner"
   - **Error messages**: Each error must have: trigger condition, exact message text, message type (toast/inline/modal), and recovery action
   - **Form validation**: Each input field must specify: validation rule, trigger (on blur / on submit), error message text, and any cross-field dependencies

6. **Assumption blocks**: For any design decision where the PRD is ambiguous or silent (e.g., session timeout behavior, empty state copy, redirect destination after action), insert an inline assumption block:
   ```
   > Assumption: [what was assumed]
   > Validate: [who should confirm, by when]
   > Change trigger: [what would change this design decision]
   ```

   If Product is still `DRAFT`, also add an inline Product-validation marker where the design depends on scope, personas, acceptance criteria, or priorities that may still move:
   ```
   <!-- PENDING: validate against product -->
   ```

7. **Output comprehensive design spec** covering all Must Have FRs with full coverage per item 4–5 above. Should-Have FRs must have at least a flow and one wireframe description. Could-Have FRs may be stubbed.

8. **Before presenting the draft**: Run the shared self-check in `core/phase-quality-standards.md` and proactively fix any below-quality item that does not require new human input.

9. **Implementation-ready design rule (`DES-1`, hard rule)**: Every Must Have FR's design block MUST be explicit enough that Plan can scope it and Implement can build it without re-asking UX. That means each Must Have FR has, at minimum:
   - state coverage for `Empty`, `Loading`, `Populated`, `Error` (not just one happy state)
   - exact error copy per error trigger (the actual message text, not a placeholder)
   - validation behavior per input field — rule, trigger (on blur / on submit), error text, cross-field dependencies if any
   - explicit mapping back to `FR-xxx` and the originating `US-xxx` from the Product package

   Missing any of the above for a Must Have FR blocks `approve design`.

10. **Test-observable design rule (`DES-2`, hard rule)**: Every state, error, empty, loading, and validation behavior in a Must Have FR design MUST be observable enough for QA to write test cases without asking UX for clarification. For each state, that means: a stable identifier or label QA can target, the visible signal that distinguishes the state, and the exit condition that ends it. Designs that describe states only as visual mood or animation without an observable signal are below quality and block `approve design`.

11. **Assumption discipline when Product is still DRAFT**: When Design depends on Product fields that are still moving (scope, persona, AC priority, KPI thresholds), every dependent decision MUST be wrapped in both:
   - the inline `> Assumption / Validate / Change trigger` block from Behavior item 6, AND
   - an inline `<!-- PENDING: validate against product -->` marker

   Both must be cleared before `approve design`. A Design DRAFT with `dependencies_pending: [product]` cannot be approved while `PENDING` markers remain in any Must Have FR section.

## Input Context

- Required when Product is `APPROVED`: **Effective Truth** for the product phase (per `core/version-manager.md § Effective Truth`). Compose via `python .prism/core/tools/effective_truth.py --phase product --up-to-sprint v{X}` — the composed view contains the product Living Truth tree merged in-memory with the active sprint's approved split proposals, earlier unsealed sprints' approved proposals, and approved change-pack deltas.
- Required when Product is still `DRAFT`: load the active sprint Product working package directly from `docs/sprint-v{X}/product/`: `sprint-brief-v{X}.md`, `proposals/prd-v{X}.md`, `proposals/glossary-v{X}.md`, `proposals/personas-v{X}.md`, `proposals/market-research-v{X}.md`, and `proposals/epics/*.md` when present. Treat Product-dependent design decisions as provisional and mark them per Behavior item 11.
- Optional: own sprint's earlier `design/proposals/design-system-v{X}.md` if Design is being re-attempted after `feedback:`
- Optional (via inbox): `design.md`, `design-system.md`, `wireframes.md`, `user-flows.md`, `prototype.md`, `design-assets/`
- Prohibited inputs: sealed sprints' files (their content already lives in Living Truth — load Living Truth instead), other sprints' DRAFT proposals, snapshots folder (audit-only), architecture / implementation / test docs

If the active sprint's Product proposal is still `DRAFT`, the resulting Design proposal must carry `dependencies_pending: [product]` in frontmatter until Product is approved and Design is re-validated.

## Output

Written to `/docs/sprint-v{X}/design/`:

| File | Template | Content | Lifecycle |
|------|----------|---------|-----------|
| `proposals/design-system-v{X}.md` | `core/templates/proposal-template.md` | Anchored `## New` / `## Updated` / `## Removed` items targeting `/docs/design/design-system.md` (SCREEN-NNN, DS-COMP-NNN) + the singleton `DESIGN-OVERVIEW-001` narrative block (design principles, brand/system overview). Authored `## New` in sprint 1, `## Updated` (replace in place, ID unchanged) later. | Merges into `/docs/design/design-system.md` at sprint seal via `seal_sprint.py` |

The body of the proposal follows the structural conventions of `core/templates/design-template.md` (design principles, brand, screen inventory, wireframes, message copy, form validation, traceability, components, tokens, accessibility) but emits each mergeable item as an anchored H3 block per the proposal template.

Sprint v1 bootstrap: when `/docs/design/design-system.md` does not yet exist, `seal_sprint.py` creates it from `core/templates/design-template.md` as preamble + merges `design-system-v1.md` `## New` items.

For sprint-v{X>1}, AI NEVER writes `/docs/design/design-system.md` directly — the pre-commit hook (`core/tools/precommit_living_truth.py`) blocks it.

Output must satisfy the compact Quality Contract where applicable: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `DES-1`, and `DES-2`. The proposal must additionally pass `python .prism/core/tools/validate_proposal.py --file docs/sprint-v{X}/design/proposals/design-system-v{X}.md`. Do not require `--against-living` in sprint v1 before seal; `/docs/design/design-system.md` may not exist until the seal bootstrap.

## Gate

UX Lead / PO checks → `validate design` → `approve design` or `feedback: [...]`

`approve design` is blocked if any of the following are true:
- Product is not `APPROVED` in the same sprint
- any `dependencies_pending: [product]` marker remains in frontmatter after Product approval
- any Product-validation `PENDING` marker remains, or any marker has not been validated against the approved Product package
- any Must Have FR fails `DES-1` (4 states, exact error copy, validation behavior, mapping to FR / US)
- any Must Have FR fails `DES-2` (each state has a stable identifier, visible signal, and exit condition)
- `python .prism/core/tools/validate_proposal.py --file docs/sprint-v{X}/design/proposals/design-system-v{X}.md` returns any blocker, including missing / malformed anchors, duplicate IDs, wrong split-target prefixes, malformed frontmatter, unknown top-level merge sections, or unmergeable H2 structure inside an anchored block
- the active `validate design` file is missing, stale, or its latest explicit result still contains `blocker`-level findings (see `core/orchestrator.md § Validate Active Files`)

If Design started from a Product `DRAFT` and Product is now `APPROVED`, PRISM must generate a Pending Validation Checklist before approval. This is an approval-time follow-up block, not a separate artifact. It enumerates each remaining `<!-- PENDING: validate against product -->` marker with section context and the exact approved Product input it must be checked against.

Clear that checklist by:
- resolving each pending item through `feedback design: ...`
- removing the corresponding `PENDING` markers and any no-longer-needed `dependencies_pending: [product]` frontmatter
- re-running `validate design` on the updated DRAFT before `approve design`

## Validate Design Command

`validate design` is a user-invoked audit command. It runs read-only against the current Design DRAFT and supporting Product package, produces a structured `blocker` / `warn` / `info` report, and writes or updates the active validate file for this command (named per `core/orchestrator.md § Validate Active Files`). It must be run on the current DRAFT before `approve design` and re-run after any `feedback:` or change-pack absorption that materially changes the design.

During normal Design generation, the engine must already self-apply the same design-readiness logic before outputting the draft.

`approve design` requires that active validate file to already be present and clean, then re-runs `validate design` in console-only mode as a final full confirmation pass. If that approval-time run finds any blocker or material gap, do not approve; show the findings to the user first and ask whether they want to update the active validate file into a follow-up checklist.

### Scope

Validate Design checks:

- **Proposal structure check**: run `python .prism/core/tools/validate_proposal.py --file docs/sprint-v{X}/design/proposals/design-system-v{X}.md`. Any blocker (malformed anchors, duplicate IDs, missing required frontmatter keys, missing routing tags, unknown top-level merge sections, unmergeable H2s inside anchored blocks, or wrong split-target prefix) blocks `approve design`; Updated/Removed target existence is confirmed by `seal_sprint.py` against routed LT files.
- `DOC-3`: required sections / fields from `core/templates/design-template.md` are present or explicitly marked N/A with reason.
- `VAL-1`: the active validate file records structural coverage and rule coverage for `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `DES-1`, and `DES-2`.
- Product dependency status: if Product was DRAFT when Design started, `dependencies_pending: [product]` and all `<!-- PENDING: validate against product -->` markers are resolved against the approved Product package.
- Product fit: every Must Have FR and related US has corresponding design coverage.
- `DES-1`: each Must Have FR has complete flow coverage, `Empty` / `Loading` / `Populated` / `Error` states, exact error copy, form validation behavior, and FR / US mapping.
- `DES-2`: each state, error, loading, empty, and validation behavior has a stable QA-visible identifier or label, a visible signal, and an exit condition.
- Accessibility and platform fit: WCAG / platform / responsive assumptions are explicit or captured as open risks.
- Open Issues: every `## Open Issues` row is closed before approval.

A `blocker` finding in any area above blocks `approve design`.

### Expected Output

```text
validate design: proposals/design-system-v{X}.md (sprint design output) + effective truth of /docs/design/design-system.md
blocker: 1
warn: 1
info: 0

Findings:
- blocker [DES-1]: FR-014 has no Error state with exact copy, so QA cannot write executable cases.
- warn [DES-2]: Empty state for SCR-003 has copy but no stable QA-visible identifier.

→ Fix blockers with `feedback design: ...`
→ Then `validate design`
→ Then `approve design`
```

The active validate file is named and lifecycled per `core/orchestrator.md § Validate Active Files` (cycle-scoped: `validate-design-<cycle>.md` in `tempo/in-progress/` while running, sealed and moved to `tempo/completed/` on approval success).

If a selected or otherwise in-scope DRAFT change pack impacts Design, `approve design` is blocked until Design absorbs that change through:
- `feedback:` if Design is still `DRAFT`, or
- a Design delta in the selected change pack if Design is already `APPROVED`.

## Same-Sprint Change Handling

- Design never pulls changes backward to Product.
- If upstream change reaches Design and Design has not started, future `start design` reads effective truth.
- If Design is `DRAFT`, merge the change via `feedback:`.
- If Design is `APPROVED`, use a Design delta in the selected change pack.

## Quality Standard

Design with the rigor of a senior UX lead — complete user flows, accessibility-first, consistent design tokens, responsive considerations.
