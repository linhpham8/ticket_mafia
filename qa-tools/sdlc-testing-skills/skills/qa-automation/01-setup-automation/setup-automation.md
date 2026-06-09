---
name: 01-setup-automation
description: >
  Khởi tạo folder automation cho project mới: clone template từ assets/automation-template/
  vào testing-output/automation/, tạo cấu trúc 3-layer RF, scaffold General resource, ENV files.
  Trigger: khởi tạo automation, setup project mới, clone template, tạo folder automation.
---

# Setup Automation Project

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/01-setup-automation.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L1`.

## Inputs

- Project code/name, module, automation type: ui/api/mobile/mixed, target output path

## Core Workflow

1. Use `assets/automation-template/` as a copy source; do not read the whole asset into context.
2. Resolve project/module/env names from qa-config or ask for missing fields.
3. Copy common libraries/resources only when absent; avoid overwriting existing project files.
4. Scaffold module-specific high-level, low-level, verification, data, variables, and test suite files.
5. Record generated paths and update governance state.

## Outputs

- Automation scaffold under `output_paths.automation` or default `testing-output/automation/`

## References

- assets/automation-template/
- references/automation-framework-policy.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
