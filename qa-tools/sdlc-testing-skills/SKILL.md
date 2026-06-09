---
name: qa-skill
description: >
  QA testing skill router for software testing work across requirement review,
  test planning, test design, testcase generation, test data, automation,
  execution reports, UAT, go/no-go, smoke, security, performance, and accessibility.
  Use when the user asks for QA/QC/testing tasks, Jira/Confluence/QMetry QA sync,
  or wants guidance on which QA workflow to run.
---

# QA Skill Router

Use this file as the single source of truth for routing. Read only the routed
sub-skill first; read references on demand using `references/INDEX.md`.

## Startup Flow

1. `01-review-requirements` before planning.
2. `02-test-plan` to create Master Test Plan and `project/qa-config.yaml`.
3. `03-sprint-test-plan` for each sprint after Master Test Plan exists.
4. `qa-automation/01-setup-automation` only when automation work starts.

## Routing Rules

| User intent | Read this sub-skill |
|---|---|
| review requirements, review AC/BR, phân tích yêu cầu | `skills/qa-core/01-review-requirements/review-requirements.md` |
| master test plan, QA strategy, project/MVP test plan | `skills/qa-core/02-test-plan/test-plan.md` |
| sprint test plan, kế hoạch test sprint | `skills/qa-core/03-sprint-test-plan/sprint-test-plan.md` |
| high-level test design, HLTC, mindmap test | `skills/qa-core/04-test-design-high-level/test-design-high-level.md` |
| functional testcase, gen TC từ AC/BR/User Story | `skills/qa-core/05-gen-tc-functional/gen-tc-functional.md` |
| SIT, integration test, API contract, service dependency | `skills/qa-core/06-gen-tc-sit/gen-tc-sit.md` |
| review testcase có sẵn, coverage analysis | `skills/qa-core/07-review-tc/review-tc.md` |
| test data, dữ liệu kiểm thử | `skills/qa-core/08-gen-data-test/gen-data-test.md` |
| test result, pass/fail, bug triage, daily report, retest | `skills/qa-core/09-check-result/check-result.md` |
| sprint test report, test summary, báo cáo kiểm thử | `skills/qa-core/10-test-report/test-report.md` |
| demo script, sprint review demo | `skills/qa-core/11-demo-preparation/demo-preparation.md` |
| UAT, nghiệm thu, user acceptance | `skills/qa-core/12-uat-support/uat-support.md` |
| go/no-go, release gate, deploy decision | `skills/qa-core/13-go-no-go/go-no-go.md` |
| production smoke, smoke sau deploy | `skills/qa-core/14-smoke-production/smoke-production.md` |
| setup automation, clone automation template | `skills/qa-automation/01-setup-automation/setup-automation.md` |
| automation script, Robot Framework, Playwright script | `skills/qa-automation/02-gen-script-test/gen-script-test.md` |
| security test, OWASP, pentest, vulnerability | `skills/qa-specialist/01-security-testing/security-testing.md` |
| performance/load/stress test, JMeter/k6/Locust | `skills/qa-specialist/02-performance-testing/performance-testing.md` |
| accessibility, a11y, WCAG, screen reader, keyboard | `skills/qa-specialist/03-accessibility-testing/accessibility-testing.md` |

## Precedence

- Master vs sprint plan: explicit "master/project/MVP" -> `02`; explicit "sprint" -> `03`; if no Master Test Plan or `qa-config.yaml`, start with `02`.
- Functional vs SIT: AC/BR/User Story -> `05`; API contract, sequence, event, dependency, rollback/retry -> `06`.
- Manual TC vs automation: "gen testcase/TC" -> `05` or `06`; "write automation script/code" for concrete TC -> `qa-automation/02`.
- Integration tools: Confluence/Jira/QMetry sync or publish requests use `tools/` scripts directly, with governance approval when publishing.
- If a request spans multiple skills, ask which step to start from unless one step is clearly blocking.

## What To Read

- Always read the routed sub-skill file.
- Read `project/qa-config.yaml` only if the routed sub-skill says it can use project config and the file exists.
- Read `references/INDEX.md` to choose detailed references. Do not open all references.
- Read `governance/GOVERNANCE.md` before finalizing a skill execution.
- Read `references/skill-details/<skill-name>.md` only when the compact sub-skill says the exact template, checklist, or legacy procedure is needed.
- Treat `assets/` as copy/use assets. Do not load asset files into context unless editing the asset itself.

## Runtime Separation

The reusable skill package is `SKILL.md`, `skills/`, `references/`, `assets/`,
`governance/`, `shared-schema/`, `tools/`, `workflows/`, and `evaluation/`.
Runtime data is project-local: `project/`, `testing-output/`, `.env`,
`.env.local`, `.env.secrets`, and real tool configs such as
`tools/qmetry-config.json`. Keep runtime data out of shared skill releases.

## Output Rules

- Use Vietnamese with accents except IDs, endpoints, field names, status codes, keywords, and filenames.
- Create output directories before writing files.
- Prefer `output_paths` from `qa-config.yaml`; otherwise use the sub-skill default.
- Missing required input: write `[Cần bổ sung]`, list missing fields, and stop.
- Do not push to Confluence/Jira/QMetry until the required governance gate is approved.
