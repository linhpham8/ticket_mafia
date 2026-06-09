---
name: 14-smoke-production
description: >
  Thực hiện smoke test trên production sau deploy: kiểm tra nhanh các luồng nghiệp vụ
  cốt lõi, xác nhận deploy thành công hoặc trigger rollback. Trigger: smoke test
  production, smoke sau deploy, kiểm tra production, verify deploy, post-deploy check.
  Output: Smoke Test Result + Go/Rollback decision.
---

# Production Smoke

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/14-smoke-production.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L3`.

## Inputs

- Production smoke scope, deployment window, environment URL, critical flows, monitoring/evidence access

## Core Workflow

1. Run only approved production-safe smoke checks.
2. Validate critical login/API/core flows, observability, links, performance sanity, and known-risk areas.
3. Record evidence and compare against smoke exit criteria.
4. If ROLLBACK is required, notify immediately and log status; rollback exception does not need extra approval.
5. Otherwise emit L3/Ops approval request before final publishing.

## Outputs

- Production smoke report and STABLE/ROLLBACK/MONITOR verdict

## References

- references/report-template.md
- references/performance-baseline.md
- governance/GOVERNANCE.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
