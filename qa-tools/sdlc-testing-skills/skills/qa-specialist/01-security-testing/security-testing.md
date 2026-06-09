---
name: 01-security-testing
description: >
  Thực hiện security testing theo OWASP Top 10 2021: kiểm tra broken access control,
  injection, auth failures, misconfiguration và các lỗ hổng phổ biến. Trigger: security
  test, OWASP, pentest, bảo mật, vulnerability, kiểm tra bảo mật. Output: Security
  Test Report với danh sách lỗ hổng phân loại theo severity.
---

# Security Testing

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/01-security-testing.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L2`.

## Inputs

- Security scope, target environment, roles/accounts, API/UI surfaces, allowed testing depth

## Core Workflow

1. Confirm authorized scope and stop if permission is unclear.
2. Select OWASP categories relevant to the feature and architecture.
3. Design or analyze tests for auth, access control, injection, data exposure, config, logging, and dependency risks.
4. Classify findings by severity, exploitability, impact, and remediation owner.
5. Emit L2 review request.

## Outputs

- Security test plan/report with findings and severity

## References

- references/owasp-checklist.md
- references/bug-severity.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
