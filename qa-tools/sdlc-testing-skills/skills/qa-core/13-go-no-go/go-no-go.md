---
name: 13-go-no-go
description: >
  Thực hiện Go/No-Go decision: tổng hợp toàn bộ chỉ số chất lượng, so sánh với exit
  criteria, đánh giá rủi ro, đưa ra khuyến nghị deploy. Trigger: go/no-go, deploy
  decision, thẩm định, xác nhận deploy, release gate, có thể release không.
  Output: Go/No-Go Report với khuyến nghị rõ ràng.
---

# Go/No-Go Decision

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/13-go-no-go.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L3`.

## Inputs

- Sprint report, UAT result if required, open bugs, security/performance/accessibility results, release readiness evidence

## Core Workflow

1. Collect quality, UAT, security, performance, accessibility, deployment, rollback, and monitoring evidence.
2. Evaluate gates against configured criteria and document source of each threshold.
3. State GO, CONDITIONAL GO, NO-GO, or BLOCKED with reasons and residual risks.
4. List required actions, owners, and deadlines.
5. Emit blocking L3 approval request; do not publish/update systems before approval.

## Outputs

- Go/No-Go report and recommendation

## References

- references/report-template.md
- references/bug-severity.md
- references/performance-baseline.md
- governance/GOVERNANCE.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
