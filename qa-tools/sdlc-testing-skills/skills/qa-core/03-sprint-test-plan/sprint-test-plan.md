---
name: 03-sprint-test-plan
description: >
  Tạo Sprint Test Plan ngắn gọn — cấu trúc 5 mục thực tế như team đang dùng.
  Nội dung sprint-specific: objectives, ticket scope + risk, schedule, resources + capacity,
  exit criteria, references. Chiến lược, test technique, KPI tham chiếu Master Test Plan.
  Trigger: sprint test plan, test plan sprint, kế hoạch test sprint, QA plan sprint N.
  Điều kiện sử dụng: đã có Master Test Plan. Nếu chưa có → dùng skill 02 (qa-core/02-test-plan) trước.
  Output: file .md 5 mục.
---

# Sprint Test Plan

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/03-sprint-test-plan.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L1`.

## Inputs

- Sprint scope, selected stories/features, Master Test Plan or qa-config.yaml, team capacity, environment availability

## Core Workflow

1. Read qa-config if present and reuse project strategy/criteria.
2. Identify sprint-specific scope, exclusions, risk changes, target artifacts, ownership, and schedule.
3. Reuse Master Test Plan sections by reference instead of duplicating unchanged content.
4. Call out dependencies, blockers, and deviations from the master plan.
5. Save the sprint plan and update audit/session state.

## Outputs

- Sprint Test Plan markdown

## References

- references/test-plan-template.md
- references/project-folder-convention.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
