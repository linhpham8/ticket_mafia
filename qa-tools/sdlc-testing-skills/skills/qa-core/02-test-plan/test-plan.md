---
name: 02-test-plan
description: >
  Tạo Master Test Plan & Strategy toàn diện cho project hoặc milestone lớn (MVP, launch, kickoff).
  Bao gồm: Entry/Exit Criteria, Strategy matrix, NFT breakdown, KPI metrics, Approval section.
  Trigger: master test plan, kế hoạch kiểm thử tổng thể, QA strategy, test plan MVP, project test plan.
  Output: file .md hoàn chỉnh 11 mục theo chuẩn IEEE 829 / ISTQB.
---

# Master Test Plan

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/02-test-plan.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L1`.

## Inputs

- Project/milestone scope, timeline, team, environments, tools, target release, risks, and requirement source

## Core Workflow

1. Read existing qa-config only if present; otherwise collect required planning fields.
2. Define scope, test levels, strategy, environments, entry/exit/suspension criteria, roles, schedule, risks, and artifacts.
3. Use the test plan template only for exact section structure.
4. Generate qa-config from the plan using the schema; keep secrets as env references only.
5. Save artifacts using project folder convention and update governance state.

## Outputs

- Master Test Plan markdown
- project/qa-config.yaml or project-local equivalent

## References

- references/test-plan-template.md
- references/qa-config-schema.yaml
- references/project-folder-convention.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
