# Reference Index

Read only the reference needed for the routed task. Treat `assets/` as files to
copy or execute, not as context to load.

| Task / skill | Read when needed |
|---|---|
| Any output path or naming decision | `references/project-folder-convention.md` |
| Master or sprint test plan | `references/test-plan-template.md`, `references/qa-config-schema.yaml` |
| High-level test design | `references/test-design-mindmap-template.md` |
| Functional testcase generation | `references/tc-template.tsv`, `shared-schema/testcase.schema.yaml` |
| SIT testcase generation | `references/sit-template.tsv`, `shared-schema/testcase.schema.yaml` |
| Testcase review / gap analysis | `references/tc-template.tsv`, `references/sit-template.tsv`, `references/bug-severity.md` |
| Test data generation | `references/project-folder-convention.md`, routed TC files |
| Daily or sprint report | `references/report-template.md`, `shared-schema/report.schema.yaml`, `references/bug-severity.md` |
| Improvement trend / lessons learned | `feedback/improvement-log.md`, `references/qa-improvement-log.md` |
| Demo, UAT, go/no-go, smoke | `references/report-template.md`, `governance/GOVERNANCE.md` |
| Security testing | `references/owasp-checklist.md`, `references/bug-severity.md` |
| Performance testing | `references/performance-baseline.md` |
| Accessibility testing | `references/accessibility-checklist.md`, `references/exploratory-checklist.md` |
| Automation setup | `assets/automation-template/`, `references/automation-framework-policy.md` |
| Automation script generation — UI (Browser/Playwright) | `references/ai-execution-spec.md`, `references/automation-framework-policy.md`, `references/rf-keyword-convention.md`, `references/rf-ui-rule.md` |
| Automation script generation — API (RESTinstance/Swagger) | `references/ai-execution-spec.md`, `references/automation-framework-policy.md`, `references/rf-api-rule.md` |
| Detailed legacy procedure for a sub-skill | `references/skill-details/<skill-name>.md` |

## Loading Rules

- Prefer the compact sub-skill workflow first.
- Open a detail file only for exact output format, checklist, or legacy edge case.
- Do not open `assets/automation-template/` unless copying files or editing the template.
- Do not open runtime data in `project/` or `testing-output/` unless the user task depends on it.
