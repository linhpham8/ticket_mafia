---
name: 09-check-result
description: >
  Phân tích kết quả kiểm thử: tổng hợp pass/fail/blocked, triage bug theo severity,
  xác định blocker, đề xuất retest scope, gen Daily Report. Trigger: kết quả test,
  pass/fail, bug triage, daily report, phân tích kết quả, retest, kiểm tra tiến độ.
  Output: Daily Report Markdown + HTML + DOCX + danh sách action items +
  improvement snapshot có cấu trúc để tái sử dụng cho Skill 08 và sprint kế tiếp.
---

# Daily Result Check

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/09-check-result.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L2`.

## Inputs

- Run result, TC execution summary, bugs, blockers, evidence links, environment status

## Core Workflow

1. Aggregate pass/fail/blocked/not-run and open bug state.
2. Classify defects by severity, priority, category, owner, and retest action.
3. Compare against exit/suspension criteria from qa-config or plan fallback.
4. Produce daily report, sprint snapshot, action items, and next-day focus.
5. Emit L2 sign-off request before publishing externally.

## Outputs

- Daily report markdown/html/docx as needed
- Run result manifest

## References

- references/report-template.md
- shared-schema/report.schema.yaml
- references/bug-severity.md
- feedback/improvement-log.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
