---
name: 03-accessibility-testing
description: >
  Kiểm tra accessibility theo chuẩn WCAG 2.1 AA: keyboard navigation, screen reader,
  color contrast, form labels, ARIA, focus management. Trigger: accessibility test,
  a11y, WCAG, kiểm tra trợ năng, screen reader, keyboard navigation, contrast.
  Output: Accessibility Test Report với danh sách lỗi phân loại theo WCAG criteria.
---

# Accessibility Testing

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/03-accessibility-testing.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L2`.

## Inputs

- Accessibility scope, pages/components, target WCAG level, browsers/devices, assistive tech constraints

## Core Workflow

1. Confirm target WCAG level and tested surfaces.
2. Check keyboard navigation, focus order, semantics, labels, contrast, forms, errors, screen reader behavior, and responsive states.
3. Separate blocker issues from advisory improvements.
4. Map findings to WCAG criteria and affected user impact.
5. Emit L2 review request.

## Outputs

- Accessibility test report with WCAG mapping and remediation guidance

## References

- references/accessibility-checklist.md
- references/exploratory-checklist.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
