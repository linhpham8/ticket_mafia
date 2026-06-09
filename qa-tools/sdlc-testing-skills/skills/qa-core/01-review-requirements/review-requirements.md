---
name: 01-review-requirements
description: >
  Review tài liệu yêu cầu từ 3 góc nhìn: QC Expert, End User, BA/Senior Dev.
  Phát hiện vấn đề cản trở development và testing trước khi viết test case.
  Trigger: review requirements, review AC, review BR, đánh giá yêu cầu, kiểm tra yêu cầu, phân tích requirements.
  Output: TSV issues list (copy vào Google Sheet) + tổng kết.
---

# Review Requirements

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/01-review-requirements.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L1`.

## Inputs

- Requirement documents: AC, BR, PRD, user story, API spec, or synced Confluence/Jira content

## Core Workflow

1. Identify requirement scope and source documents.
2. Extract actors, business rules, acceptance criteria, flows, NFRs, dependencies, and constraints.
3. Check testability, consistency, completeness, edge cases, negative flows, permission rules, data rules, and observability.
4. Classify each finding by impact and owner; do not invent missing requirements.
5. Return a concise review report with `[C?n b? sung]` for missing mandatory information.

## Outputs

- Requirement review report with gaps, risks, ambiguities, missing AC, and clarification questions

## References

- references/bug-severity.md only when classifying requirement defects

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
