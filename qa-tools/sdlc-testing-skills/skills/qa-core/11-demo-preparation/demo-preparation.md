---
name: 11-demo-preparation
description: >
  Chuẩn bị kịch bản demo Sprint Review đầy đủ: tổng hợp user story hoàn thành,
  thiết kế luồng demo, chuẩn bị data, phân công presenter, checklist môi trường.
  Trigger: demo, chuẩn bị demo, kịch bản demo, demo sprint, sprint review.
  Output: Demo Script Markdown + Checklist trước demo.
---

# Demo Preparation

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/11-demo-preparation.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L1`.

## Inputs

- Completed stories/features, demo audience, environment URL, demo data, known limitations

## Core Workflow

1. Select stable demo flows that match sprint goals.
2. Prepare story order, presenter ownership, data, environment checks, and fallback plan.
3. Call out known issues and excluded flows.
4. Create checklist for account, data, service, browser/device, and evidence readiness.
5. Save under `output_paths.demo` or default demo folder.

## Outputs

- Demo script markdown
- Demo readiness checklist

## References

- references/project-folder-convention.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
