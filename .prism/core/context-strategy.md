# Context Size Strategy

Rules for handling projects of different sizes within AI context windows.

This file works together with the phase-specific context loading rules in `core/orchestrator.md` and `core/freedom-router.md`.

Apply them in this order:
1. Use the active phase rules to decide **which documents are eligible to load**.
2. Use this file to decide **how much of those eligible documents to load** based on project size and context pressure.

In short: phase rules choose the sources; context strategy chooses the loading shape.

## Size Categories

| Category | Indicator | Strategy |
|----------|----------|---------|
| Small | Product package < 3,000 tokens combined | Load full documents, normal batch output |
| Medium | Product package 3,000–8,000 tokens combined | Summarize + load relevant sections |
| Large | Product package > 8,000 tokens combined | Domain-based splitting |

## Small Project

- Load full documents as-is
- Single-batch output for each phase
- No special handling needed

## Medium Project

- **Architecture phase**: AI summarizes the Product package (key points only) + loads relevant sections in full
- **Complete architecture package in one pass when feasible**. If context pressure is high, explain the split explicitly and group supporting artifacts coherently (for example core architecture first, then ERD / API specs / events / NFR supplements).
- AI explicitly states what was summarized vs loaded in full

## Large Project

- Break the Product package into modules/domains
- Run Architecture **separately per domain**
- After all domains: AI reads all arch outputs → creates **integration architecture** document
- Each domain gets its own sub-folder in the sprint:
  ```
  /docs/sprint-v1/architecture/
  ├── proposals/architecture-v1.md (integration overview proposal)
  ├── domain-auth/
  │   ├── notes.md
  │   ├── assets/
  │   └── ...
  └── domain-orders/
      └── ...
  ```
- Domain sub-folders are supporting working context only. Mergeable architecture proposals MUST remain in the canonical phase-root `architecture/proposals/*-v{X}.md` files so `seal_sprint.py`, `effective_truth.py`, and `scan_drift.py` can discover them deterministically.

## Warning Rules

1. AI **MUST warn** when context usage exceeds 60% of the window
2. Propose the appropriate fitting strategy from above
3. **User decides** — AI does not auto-apply strategies
4. **NEVER cut information** without explicitly asking user what to omit
5. If user agrees to summarize: AI produces summary, shows it, asks "Is this summary accurate?"

## Resume After Compaction

When conversation context is compacted (long sessions):

1. AI detects compaction (missing prior context)
2. Re-reads files from the File Layer (`/docs/sprint-v{X}/`)
3. Re-reads `prism-config.md` for project state
4. Informs user: "Context was compacted. I've re-loaded project state from files. Current sprint: v{X}, phase: {phase}."

## Multi-Sprint Context Loading

When multiple sprints exist, AI loads the *effective truth* for the active phase per the 2-tier model in `core/version-manager.md § Effective Truth`. The composition is:

```
Living Truth (15 root LT files under docs/{product,design,architecture,testing}/ + product/epics/EP-*.md)
  + APPROVED split proposals from every earlier UNSEALED sprint Y < X
  + APPROVED change-pack deltas in those earlier unsealed sprints
  + own sprint vX's APPROVED proposals + APPROVED change-pack deltas
```

Compose on demand:

```bash
python .prism/core/tools/effective_truth.py --phase {product|design|architecture|testing|all} --up-to-sprint v{X}
```

**Working sprint detection**: sprint with `sealed: false` AND the most recently updated DRAFT file (by `updated` frontmatter). If multiple unsealed sprints tie, prefer the higher sprint number. User can be explicit: `resume design in sprint-v2`.

### ALWAYS load for sprint-v{X} active

- Effective truth via `effective_truth.py` for the needed phase(s), not raw folder enumeration
- Own sprint vX's APPROVED mergeable split proposals up to the current phase under concrete phase `proposals/` folders
- Earlier UNSEALED sprints' APPROVED split proposals (Y < X, `sealed: false`, frontmatter `status: APPROVED`)
- Earlier UNSEALED sprints' APPROVED change-pack `{phase}-delta-*.md` files
- Own sprint's APPROVED change-pack deltas (if any)

### NEVER load routinely

- Sealed sprints' files (`sprints[].sealed = true` in prism-config.md) — their content already lives in Living Truth
- Other sprints' DRAFT proposals or DRAFT change packs
- Later sprints (Y > X) — these are not yet effective truth for sprint vX
- `docs/sprint-v*/snapshots/` — audit-only, not editing material

### CONDITIONAL (only on explicit user request)

- Sealed sprint snapshots — for audit / forensic comparison
- Older sprint implementation plans (`docs/sprint-v{Y}/planning/implementation-plan-v{Y}.md`) — for debugging (the implement phase itself emits code, not a docs folder)
