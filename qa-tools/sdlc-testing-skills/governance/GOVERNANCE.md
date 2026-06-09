# Governance

Apply this for every skill execution.

## Gates

| Level | Meaning | Action |
|---|---|---|
| L1 | Auto-complete | Save artifacts, update audit/session state, report completion. |
| L2 | QA/Dev review | Save artifacts, emit sign-off request, wait for explicit approval before publishing or proceeding. |
| L3 | Stakeholder/Ops approval | Save artifacts, emit blocking approval request, stop until explicit approval. |

Use `governance/sign-off-gates.md` only when the exact reviewer, SLA, or request
format is needed.

## Required State Updates

- Append one execution record to `governance/audit-log.md` or the project-local audit log.
- Update `project/session-state.yaml` when it exists.
- Use reviewer names and escalation chain from `project/qa-config.yaml` when present.

## External Tools

Do not push to Confluence, update Jira, import QMetry, or publish reports before
the required L2/L3 approval. Dry-run and local export are allowed.

## Runtime Isolation

For shared/team use, keep runtime files project-local: `project/`,
`testing-output/`, `.env*`, and real tool configs. Shared skill files should stay
stable across teams.
