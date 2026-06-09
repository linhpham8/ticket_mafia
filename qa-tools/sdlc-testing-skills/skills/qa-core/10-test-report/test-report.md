---
name: 10-test-report
description: >
  Tổng hợp Sprint Test Report hoàn chỉnh: aggregate kết quả từ daily reports,
  tính Health Score cuối sprint, phân tích bug theo severity và category,
  đánh giá Ship Readiness, phân tích defect pattern và coverage delta theo module.
  Trigger: test report, sprint report, test summary,
  báo cáo kiểm thử, tổng kết sprint. Output: báo cáo Markdown theo
  references/report-template.md và bản HTML theo cùng format.
---

# Sprint Test Report

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/10-test-report.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L2`.

## Inputs

- Daily report snapshots or aggregate TC result, bug list, coverage delta, exit criteria

## Core Workflow

1. Aggregate sprint metrics and validate totals.
2. Calculate health score and compare against exit criteria.
3. Summarize defect trends, coverage delta, residual risks, and ship readiness.
4. Append improvement snapshot for the next sprint.
5. Emit L2 sign-off request before external publishing.

## Outputs

- Sprint test report markdown/html/docx as needed
- Improvement snapshot

## References

- references/report-template.md
- shared-schema/report.schema.yaml
- references/bug-severity.md
- feedback/improvement-log.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
