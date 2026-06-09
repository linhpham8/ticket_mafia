---
name: 12-uat-support
description: >
  Hỗ trợ User Acceptance Testing: chuẩn bị tài liệu hướng dẫn UAT, tổng hợp feedback
  từ người dùng thực, phân loại issue UAT, theo dõi sign-off. Trigger: UAT, user
  acceptance, nghiệm thu, end user test, kiểm thử người dùng. Output: UAT Test Guide
  + UAT Feedback Summary + Sign-off Tracker.
---

# UAT Support

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/12-uat-support.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L3`.

## Inputs

- UAT scope, stakeholder list, UAT environment, UAT scenarios, feedback/issue list

## Core Workflow

1. Prepare UAT scope, roles, entry criteria, and execution guide.
2. Map UAT scenarios to business requirements and acceptance criteria.
3. Collect feedback, classify UAT issues, and separate defect/change request/question.
4. Summarize sign-off status and open risks.
5. Emit blocking L3 approval request.

## Outputs

- UAT guide
- Feedback summary
- Sign-off tracker

## References

- references/report-template.md
- governance/GOVERNANCE.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
