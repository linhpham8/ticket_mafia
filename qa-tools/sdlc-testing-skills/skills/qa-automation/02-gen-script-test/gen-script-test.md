---
name: 02-gen-script-test
description: >
  Tạo automation test script từ test case: Robot Framework sử dụng thư viện Playwright. Trigger: automation script, gen script,
  viết code test, Robot Framework, tự động
  hoá kiểm thử.
  Output: code file chạy được ngay, CI-ready.
---

# Generate Automation Script

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/02-gen-script-test.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L2`.

## Inputs

- Approved TC file or selected TC rows, test data, target framework/tool, environment/auth details

## Core Workflow

1. Select only TC rows marked automation-ready or explicitly requested.
2. Map TC steps to existing keywords before creating new keywords.
3. Generate scripts using the configured framework; default Robot Framework only when no framework is specified.
4. Keep data and credentials externalized; never hard-code secrets or environment URLs.
5. Emit L2 Dev/QA review request before publishing or marking done.

## Outputs

- Automation script files, keyword/resource files, data files, and mapping matrix

## References

- references/ai-execution-spec.md — bắt buộc mọi framework
- references/automation-framework-policy.md — policy tổ chức project
- references/rf-keyword-convention.md — overview kiến trúc 3-layer Robot Framework
- references/rf-ui-rule.md — quy tắc chi tiết khi sinh UI keyword (Browser/Playwright)
- references/rf-api-rule.md — quy tắc chi tiết khi sinh API keyword (RESTinstance/Swagger)

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
