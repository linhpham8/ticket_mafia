# Freedom Router

Routing engine for **Freedom mode** — intent detection, phase activation, session management. No gates, no approval, no immutable versioning. Documents editable in-place. Phase engines (`core/phase-*.md`) are reused for questions, templates, and quality standards — gate and approval sections are ignored.

---

## F1 — Intent Detection

Detect which PRISM phase the user wants to work on from natural language. No explicit commands required.

### Signal Table

| Detected Phase | Signal Keywords (any 3+ = high confidence) |
|---|---|
| product | requirement, feature, user story, KPI, problem, market, persona, MVP, business goal, epic, PRD, stakeholder, value proposition, pain point |
| design | UI, UX, wireframe, user flow, component, layout, responsive, accessibility, WCAG, design system, Figma, screen, interaction, visual |
| architecture | database, API, tech stack, system design, microservice, infrastructure, schema, ERD, sequence diagram, ADR, scalability, cloud, service |
| plan | task, sprint, estimate, breakdown, milestone, implementation, sequencing, delivery, team capacity, rollout, dependency |
| test | test, QA, coverage, regression, edge case, acceptance criteria, TC-xxx, bug, test plan, test case, validation |
| implement | code, build, fix, develop, refactor, deploy, write code, implement, engineer, PR |

### Confidence Rules

- **High confidence (3+ signals)**: Activate phase directly. State detected phase in one line before asking questions.
- **Low confidence (1–2 signals)**: State interpretation and ask for confirmation in ONE message.
- **No match**: Engage conversationally using general principles. Guide toward structured output when ready.
- **Cross-phase**: Identify primary (most signals), note secondary.
- **Explicit commands**: `start product`, `import arch`, etc. still work — execute directly.
- **Command normalization applies**: Treat `arch` and `architecture` as the same phase name for command-style requests, and auto-correct obvious one-edit typos when the intended command is unambiguous.

---

## F2 — Phase Activation

Once intent is detected:

1. **State phase** — one line, e.g., "Working on: Product phase."
2. **No gate check** — any phase can be activated at any time regardless of other phases' state.
3. **Load context** per `core/context-strategy.md`. **Override**: load all matching documents regardless of any status field. Freedom mode has no status — do not filter by APPROVED or any other status value.
4. **Execute** `core/phase-{name}.md` — use questions, templates, quality standards. **Ignore** gate prerequisites and approval steps.
5. **Guided-only pending markers do not gate freedom mode** — `dependencies_pending: [product]`, `Pending Validation Checklist`, and `<!-- PENDING: validate against product -->` are guided-mode gating constructs. Do not treat them as workflow blockers in freedom mode. Omit them when writing freedom artifacts, or rewrite the underlying uncertainty as a normal assumption / open-question note with no gate semantics.
6. **Produce artifact(s)** using the phase templates in `core/templates/`. Replace each template's YAML frontmatter with freedom frontmatter — strip `status` and `approved_by`:
   ```yaml
   ---
   version: v{X}
   sprint: {X}
   phase: {phase}
   created: YYYY-MM-DD
  updated: YYYY-MM-DD HH:MM
   ---
   ```
  Refresh `updated` on every write, revision, import save, and auto-save. If one action writes multiple files in the same lane, stamp that file set with the same `updated` value.
  **Stable IDs still apply in Freedom (DOC-2).** Freedom skips only the seal / proposal / merge pipeline — NOT ID issuance. Issue every mergeable item's stable ID atomically with `python .prism/core/tools/get_next_id.py --type {EP|FR|US|AC|BR|NFR|TC|SCREEN|DS-COMP|ARCH-COMP|ARCH|GLOSS|PERSONA|MR|SEQ|ENT|ADR|FLOW|API|EVT|PR}` and keep the `<!-- ID: X-NNN -->` anchor on its own line above each item (strict format `[A-Z]+(?:-[A-Z]+)*-\d{3,}`). If the source template's frontmatter carries an `id:` field (e.g. epic `id: EP-NNN`), keep it and fill it with the issued ID — `id:` is NOT one of the stripped fields (only `status` / `approved_by` are stripped). The `id_counters` block in `prism-config.md` exists in Freedom projects too, so `get_next_id.py` works unchanged.
  Also remove or rewrite guided-only template body / checklist language that refers to `approve *`, approval gates, `DRAFT` status, `approved_by`, or pending validation markers — and also strip the `<!-- PRISM:LT-SKELETON-END -->` sentinel, any `<!-- AUTHORING NOTE … -->` block, and anchored-merge / "sprint seal" / `*-OVERVIEW-001` / `TEST-COVERAGE-001` singleton wording (these are guided LT-bootstrap scaffolding; freedom mode has no seal, no versioned proposals, and no auto-index — author the Rule / Branch Inventory as a plain section, not a `TEST-COVERAGE-001` anchored block). **Carve-out — do NOT strip ID issuance:** keep the `get_next_id.py` command, the `<!-- ID: X-NNN -->` anchors, and the strict-ID-format note. These are mode-agnostic (DOC-2). Strip only the *merge / seal / auto-index semantics* worded around them (e.g. "so `apply_proposal.py` can merge at sprint seal"), not the ID mechanism itself. Keep the substantive quality check as a normal assumption, open question, or self-review item without gate semantics.
7. **Post-output**:

```
→ [artifact file(s)] written to [path].
  • feedback: [changes]  — revise the active target (PRISM asks if multiple plausible targets are active)
  • Or describe what you'd like to work on next
```

No approval option. No gate suggestions.

---

## F3 — No Gates

There are no prerequisites between phases. User can work on architecture before product, test before plan, or any combination. AI outputs to the correct folder using the correct template regardless of what other phases have been completed.

---

## F4 — No Approval Flow

No `approve [phase]` command. No guided-style status transitions. Documents exist as living files. The `feedback:` command revises the resolved active target in-place. If more than one plausible target is active, ask the user to choose and do not guess.

---

## F4.5 — Feedback Target Resolution

`feedback:` must resolve to exactly one active target.

1. Explicit target wins (`feedback design: ...`, `feedback architecture: ...`, `feedback implement: ...`)
2. If the session already has one active target and no unrelated plausible target competes with it, reuse it
3. If exactly one plausible target exists in scope, apply feedback directly
4. If more than one unrelated plausible target exists — including an implementation lane vs. a recent document draft — ask the user to choose and do not guess
5. Accept clarification by phase name, sprint + phase, change-pack id / slug, `implement`, or numbered reply

---

## F5 — Editable Documents

All documents can be modified at any time. When AI produces output for a phase that already has a file, it overwrites the existing file. No confirmation needed.

---

## F6 — Phase Switch Mid-Session

If user shifts to a different phase mid-conversation:

1. **Auto-save**: Ensure current work is written to file and refresh its `updated` timestamp
2. **Inform**: One line — "Saved [current phase] at `[path]`. Moving to [new phase]."
3. **Proceed**: Activate new phase via F2

---

## F7 — Auto-scaffolding

On first artifact output:

1. Check if `/docs/sprint-v1/` exists
2. If not → create sprint directory structure (product, design, architecture, planning, testing; plus `tempo/` as needed). Freedom mode does not use the guided-only `changes/` or `snapshots/` folders (no seal).
3. Save artifact in correct subfolder with YAML frontmatter
4. Inform: "Created sprint-v1 structure. [Artifact] saved at `[path]`."

---

## F8 — Resume Detection

At session start, or when user says "continue / resume / pick up where we left off":

1. Find highest sprint number in `/docs/sprint-v{X}/`
2. Scan documents for `updated` frontmatter field
3. Use `updated` as the primary recency field. If it is missing or invalid, fall back to the file's modified timestamp for this turn and tell the user it will be normalized on the next write
4. Find the most recently updated file → that's the active work
5. If multiple files tie across different phase folders, or a current implementation lane competes with the latest document work, present a compact resume-choice block with target, file(s) when applicable, updated timestamp, and exact reply options (`resume design`, `continue architecture`, `resume implement`, etc.)
6. On resume after target resolution, load the file or implementation lane and continue without re-asking completed sections

When step 5 applies, use this format:
```
Multiple active targets found in sprint-v{X}:

1. design
  files: design-system.md
  updated: YYYY-MM-DD HH:MM

2. architecture
  files: architecture.md, sequence.md
  updated: YYYY-MM-DD HH:MM

Reply with:
- resume design
- continue design
- resume architecture
- continue architecture
- or describe another task
```

---

## F9 — New Sprint

Trigger: "new sprint", "start v2", "begin a new version":

1. Create `/docs/sprint-v{N+1}/` folder structure
2. Optionally preview composed cross-sprint state via `python .prism/core/tools/effective_truth.py --phase all --up-to-sprint v{N+1}` (informational only; freedom mode does not enforce the 2-tier proposal merge structure)
3. Inform: "Created sprint-v{N+1}. Previous sprint remains editable."
4. **No locking** — previous sprint's documents stay fully editable

---

## F10 — Import

`import [phase]` works identically to other modes, with these freedom overrides:

1. Read inbox files per orchestrator.md naming table
2. Run the full import audit via `core/import-validator.md`. **Freedom override**: ignore the "save as DRAFT" rule and any review / approval suggestion tied to unresolved import issues — they do not apply in freedom mode.
3. Save with freedom frontmatter — no `status` field, no `approved_by` — and refresh `updated` to the current write time.
4. Move inbox files to `docs/inbox/processed/`

---

## F11 — Token Efficiency

1. Batch related questions into grouped rounds; Product and Architecture may need follow-up grouped rounds until material gaps are resolved
2. Complete phase output in one pass after no material blocker questions remain
3. High-confidence detection → activate without confirmation
4. No approval round needed → save one round trip vs other modes

---

## F12 — Mode Permanence

Freedom mode is permanent. Cannot switch to guided. If user requests: "Freedom mode is permanent. To use guided, start a new project with `./setup.sh`."

---

## F13 — Commands Not Applicable in Freedom Mode

Freedom mode has no status model, no approval flow, and no immutability. Documents are living files — users edit them directly at any time. The following commands from guided mode do not exist in freedom mode:

| Command | Why not applicable | Freedom equivalent |
|---|---|---|
| `start change:` | No immutability — documents are always editable in-place | Use `feedback:` to edit any document directly |
| `approve [phase]` | No approval flow | — |
| `approve changes` | No change pack model | — |

If the user types any of these commands, respond with one line explaining it is not applicable in freedom mode and suggest the direct equivalent action.
