# Status Format

Canonical output contract for `status` in guided mode.

`status` is read-only and must never block, even when multiple DRAFT change packs or multiple active targets exist.

## Canonical Section Order

Render sections in this exact order. Omit a section only when it has no content.

1. `active target: ...`
2. `DRAFT change packs:`
3. sprint blocks from oldest to newest
4. drift warnings directly under the affected sprint block
5. `next: ...`

Do not invent alternate headings such as `Current State`, `Open Work`, or `Suggested Action`.

## Sprint Labels

Use exactly one of these labels per sprint:

- `[running]`
- `[prep — plan/test/implement blocked until v{X} seals]`
- `[sealed]`

## Phase / Lane Line Format

Use one of these shapes:

```text
product       APPROVED   YYYY-MM-DD HH:MM
design        DRAFT      YYYY-MM-DD HH:MM
architecture  — not started
plan          ⛔ blocked (sprint-v1 not sealed)
```

For every started phase or lane (`DRAFT` or `APPROVED`), add a `files:` line immediately after the phase line.

Use canonical file order and list only the outputs that already exist for that lane:

- `product`: `sprint-brief-v{X}.md`, `proposals/prd-v{X}.md`, `proposals/glossary-v{X}.md`, `proposals/personas-v{X}.md`, `proposals/market-research-v{X}.md`, `proposals/epics/EP-NNN-{slug}-v{X}.md`
- `design`: `proposals/design-system-v{X}.md`
- `architecture`: `sprint-brief-v{X}.md`, `proposals/{architecture,nfr,sequence,erd,adr,data-flow,api-specs,events,project-reference}-v{X}.md`
- `plan`: `implementation-plan-v{X}.md`
- `test`: `test-plan-v{X}.md`, `proposals/test-cases-v{X}.md`
- `implement`: explicit changed file list if known; otherwise `target repository code + unit tests (session-scoped)`

Do not list Test generated TSV companions in the main phase `files:` line; validate/test export checks cover `testing/generated/` separately.

Example:

```text
design        DRAFT      YYYY-MM-DD HH:MM
  files: design-system.md
```

If a DRAFT carries follow-up metadata, place it after the `files:` line:

```text
design        DRAFT      YYYY-MM-DD HH:MM
  files: design-system.md
  waiting on: product
```

or:

```text
design        DRAFT      YYYY-MM-DD HH:MM
  files: design-system.md
  follow-up: pending validation checklist required before approve
```

## DRAFT Change Pack Format

Show change packs before sprint blocks. Group by sprint and keep a stable field order.

```text
DRAFT change packs:
  sprint-v1 / v1.3.8-fix-payment
     earliest: product
     downstream: architecture
    phases: product, design, architecture
    files: change-request.md, impact-matrix.md, product-delta-v1.3.8-fix-payment.md, design-delta-v1.3.8-fix-payment.md, architecture-delta-v1.3.8-fix-payment.md
     blockers: none
```

`phases:` lists the impacted phases from `earliest` through the current `downstream` phase in forward order.

`files:` lists the currently existing outputs inside the selected pack in this stable order:

1. `change-request.md`
2. `impact-matrix.md`
3. generated delta files in forward phase order (`product` -> `design` -> `architecture` -> `plan` -> `test`)

If a pack is the sticky active target, add one more line:

```text
     selected: yes
```

## Multi-Sprint Rules

- Sprint blocks always render oldest to newest.
- A blocked lane caused by sprint sealing must use `⛔ blocked (sprint-v{X} not sealed)`.
- A drift warning appears immediately after the affected sprint block, not at the top or bottom of the entire report.
- Started phase / lane `files:` lines and change-pack `phases:` / `files:` lines are part of the canonical block and should not be omitted when data exists.

## Next-Step Suggestion

End with exactly one `next:` line.

Prefer this order:

1. selected or obvious DRAFT change pack needing validation or approval
2. active DRAFT lane in the highest relevant sprint
3. pending validation checklist follow-up
4. `new sprint`
5. `start implement` when all prerequisite approvals already exist

Examples:

```text
next: resume design in sprint-v2
```

```text
next: validate changes v1.3.8-fix-payment
```

## Single-Sprint Example

```text
active target: design in sprint-v1

sprint-v1 [running]
  product       DRAFT      2026-04-20 09:10
    files: proposals/prd-v1.md, proposals/epics/EP-001-auth-v1.md
  design        DRAFT      2026-04-20 09:45
    files: proposals/design-system-v1.md
    waiting on: product
  architecture  — not started
  plan          ⛔ blocked (product + design + architecture not approved)
  test          ⛔ blocked (product + design + architecture not approved)
  implement     ⛔ blocked (plan not approved)

next: resume design
```

## Multi-Sprint Example

```text
active target: v1.3.8-fix-payment

DRAFT change packs:
  sprint-v1 / v1.3.8-fix-payment
     earliest: product
     downstream: architecture
     phases: product, design, architecture
     files: change-request.md, impact-matrix.md, product-delta-v1.3.8-fix-payment.md, design-delta-v1.3.8-fix-payment.md, architecture-delta-v1.3.8-fix-payment.md
     blockers: none
     selected: yes

sprint-v1 [running]
  product       APPROVED   2026-04-18 11:00
    files: proposals/prd-v1.md
  design        APPROVED   2026-04-18 14:20
    files: proposals/design-system-v1.md
  architecture  APPROVED   2026-04-18 16:10
    files: proposals/architecture-v1.md, proposals/api-specs-v1.md
  plan          APPROVED   2026-04-19 09:15
    files: implementation-plan-v1.md
  test          DRAFT      2026-04-20 08:30
    files: test-plan-v1.md, proposals/test-cases-v1.md
  implement     DRAFT      2026-04-20 08:50
    files: target repository code + unit tests (session-scoped)

sprint-v2 [prep — plan/test/implement blocked until v1 seals]
  product       APPROVED   2026-04-20 09:40
    files: proposals/prd-v2.md
  design        DRAFT      2026-04-20 10:05
    files: proposals/design-system-v2.md
  architecture  — not started
  plan          ⛔ blocked (sprint-v1 not sealed)
  test          ⛔ blocked (sprint-v1 not sealed)
  implement     ⛔ blocked (sprint-v1 not sealed)

next: validate changes v1.3.8-fix-payment
```
