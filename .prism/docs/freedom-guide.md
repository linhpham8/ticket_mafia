# Freedom Guide

How to use PRISM Freedom mode — natural language interactions with maximum flexibility, no gates, and editable documents.

---

## What Freedom Mode Does

In Freedom mode, PRISM detects your intent from natural language, but removes the approval flow and hard version freeze. You can start with any phase, move between phases at any time, and revise existing documents in place. If more than one draft or lane is a plausible feedback target, PRISM asks which one you mean instead of guessing.

**The tradeoff is explicit:** you gain speed and flexibility, but you lose immutable approval checkpoints.

Freedom mode still keeps PRISM's quality bar: numbered artifacts, stable IDs, cross-links, dependency context, sprint evidence, template coverage, implementation traceability, and repo-test expectations still apply. What changes is enforcement style: quality gaps become assumptions, open questions, self-review items, or fixes in place — not phase gates.

---

## Example 1 — Start With Design First

**User input:**
> "I want to sketch the dashboard UX first before we finish the Product package."

**What AI does:**
1. Detects: Design phase
2. Does not block on missing product approval
3. Asks all design questions in one batch
4. Writes the design document directly

**After user answers:**
```
→ docs/sprint-v1/design/design-v1.md written
  • feedback: [changes]  — revise the active target
  • Or describe what you'd like to work on next
```

If assumptions depend on a future Product package, AI should flag them inline and continue.

---

## Example 2 — Revise The Same Document In Place

**User input:**
> "Update the dashboard design so the left nav becomes collapsible and add dark mode tokens."

**What AI does:**
1. Re-loads the existing design document
2. Applies the requested changes in place
3. Writes back to the same sprint document path

**Result:**
```
→ docs/sprint-v1/design/design-v1.md updated
  • feedback: [changes]  — revise the active target again
  • Or describe what you'd like to work on next
```

Every in-place save refreshes the document's `updated` frontmatter. Freedom `resume / continue` uses that field as the primary recency signal, and falls back to the file's modified time only if `updated` is missing or malformed.

There is no `approve design` step in Freedom mode.

---

## Feedback Targeting In Freedom

Freedom still requires `feedback:` to resolve to exactly one active target.

- If you name the target explicitly, PRISM uses it.
- If only one plausible active draft or lane exists, PRISM revises it directly.
- If multiple unrelated targets are plausible, PRISM asks which one you mean and does not guess.

**Example:**

**User input:**
> "feedback: simplify the auth flow"

**What AI does:**
```
I found more than one plausible target for that feedback:

1. design
  file: docs/sprint-v1/design/design-v1.md

2. architecture
  file: docs/sprint-v1/architecture/api-specs-v1.md

Reply with:
- feedback design: simplify the auth flow
- feedback architecture: simplify the auth flow
- or 1 / 2
```

If the current chat is clearly mid-implementation, `implement` can also appear as one of the choices.

---

## Example 3 — Switch Phases Mid-Session

**User input:**
> "Pause the UI for a minute and define the notification API."

**What AI does:**
1. Auto-saves the current design draft
2. Informs the user that it is switching phases
3. Activates Architecture phase immediately
4. Asks all architecture questions in one batch

**Expected flow:**
```
Switching to Architecture phase.
Current design draft saved.

Before I write the API specs and supporting architecture artifacts, here are my questions:
...
```

---

## Example 4 — Jump Straight Into Planning Or Implementation

**User input:**
> "Give me an implementation plan for auth and billing, then start with the API layer."

**What AI does:**
1. Detects planning intent first
2. Uses any existing docs for context, regardless of status
3. Writes `implementation-plan-v1.md`
4. If the user then asks to implement, it moves directly into execution

**Important:** if implementation reveals a real planning gap, AI should stop, flag it clearly, and ask whether to amend the plan or architecture before continuing.

---

## Example 5 — New Sprint Without Locking

**User input:**
> "Start v2 for the enterprise version, but keep v1 editable because we still need tweaks."

**What AI does:**
```
Creating sprint-v2...

✓ sprint-v2/ created
✓ previous sprint remains editable
✓ no seal pipeline runs in freedom mode
```

Freedom mode uses sprints for organization, not freezing.

---

## When Freedom Mode Fits Best

- You are iterating quickly and do not want approval prompts between phases.
- One person or a small team owns the workflow end-to-end.
- You are comfortable revising documents in place instead of preserving strict approved baselines.

## When Freedom Mode Is A Bad Fit

- You need formal sign-off between product, design, architecture, and implementation.
- Multiple teams depend on immutable approved artifacts.
- You need strict auditability of each phase handoff.

In those cases, use Guided mode.
