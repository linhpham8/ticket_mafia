---
status: DRAFT
version: v1
sprint: 1
phase: test
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# Test Plan — {{PROJECT_NAME}} (Sprint v{{X}})

## 1. Test Strategy Overview

| Attribute | Value |
|-----------|-------|
| Testing approach | Risk-based, requirement-traceable |
| Planning target | Clear test intent before execution begins |
| Execution ownership | Implemented later in code / pipeline / QA runs |
| Release criteria | Defined here, executed later outside this planning phase |

> **Phase Test ownership**: phase này sở hữu `qa test intent` only — `test-plan` + `test-cases`. KHÔNG sở hữu `repo test delta` (in-repo unit / integration / contract / component tests), generated runtime data packs, hoặc external QC automation code. Repo test delta là dev-owned, sống trong Plan (`repo_test_delta_target` per task group) và Implement, được audit bởi `validate implementation --mode spec`. Không được duplicate hay thay thế repo test definitions trong file này.

## 2. Scope

### In Scope

| Area | Test Types | Priority |
|------|-----------|----------|
| <!-- e.g., User authentication --> | Functional / integration intent + QA manual validation intent | P0 |
| <!-- e.g., API endpoints --> | Planned integration, contract, security intent | P0 |
| <!-- e.g., UI components --> | Planned component, accessibility, exploratory intent | P1 |

### Out of Scope

<!-- Explicitly state what will NOT be tested in this sprint and why. -->

| Area | Reason |
|------|--------|
| | |

## 2a. Design State Coverage

<!-- Bắt buộc: mỗi state đã định nghĩa trong design (Empty / Loading / Populated / Error / Disabled / etc.) phải có ít nhất 1 TC. -->
<!-- State không có TC → block `approve test`. -->

| Screen / Component | State | Test Case ID | Mode (manual / auto) |
|--------------------|-------|--------------|----------------------|
| | Empty | TC-xxx | |
| | Loading | TC-xxx | |
| | Populated | TC-xxx | |
| | Error | TC-xxx | |

## 2b. Coverage Traceability Index

<!-- Đây là map ở phía Test để nối requirement / design / API / NFR / project boundary xuống TC IDs cụ thể. -->
<!-- Mọi Must Have FR và prioritized NFR nên xuất hiện ở đây; nếu còn gap, phải ghi rõ. -->

| FR / NFR | US | Design / API Refs | Project / Boundary Refs | TC IDs | Manual / Auto Mix | Coverage Status / Gap |
|---|---|---|---|---|---|---|
| FR-NNN, NFR-NNN | US-NNN | `/docs/design/design-system.md §...`, `/docs/architecture/api-specs.md §API-NNN` | `/docs/architecture/project-reference.md §PR-NNN` | `TC-NNN`, `TC-NNN` | automated + manual | covered / partial / gap |
| | | | | | | |

## 2c. Branch Discovery Summary

<!-- Optional but required for complex rule-heavy features. -->
<!-- Use before detailed cases when AC / BR / sequence docs imply many branches, rule precedence, fallback, rollback, async, or AI/rule-engine behavior. -->

| Feature / Flow | Branches Discovered | Unclear / Contradictory Inputs | Questions / Proposed Assumptions | Impacted TC Areas |
|---|---|---|---|---|
| | Happy / negative / fallback / timeout / rollback / async / edge | | | |

> **Rule**: This is an AI discovery step to expose missing branches and ask/propose back to the user before detailed TC generation; it is not a manual review gate.

## 3. Test Types & Tools

<!-- Tool cells for Unit / Integration / E2E / Contract PHẢI khớp Architecture Tech Stack §Test. Component / Performance / Security / A11Y tools come from Architecture or explicit project context. -->
<!-- Phase Test KHÔNG quyết định framework mới, chỉ consume từ Architecture/context hoặc ghi TBD risk. -->
<!-- Unit/contract/component rows describe future repo test delta context; detailed QA-owned cases should use component / integration / e2e intent, not define runnable unit tests here. -->

| Test Type | Purpose | Tool (from Architecture/context) | Run Frequency | Owner |
|-----------|---------|-------------------------|--------------|-------|
| Unit | Dev-owned repo test delta context | {{UNIT_TEST_FRAMEWORK_FROM_ARCH}} | During implementation | Dev |
| Component | Component-level behavior intent | {{COMPONENT_TEST_TOOL_FROM_ARCH_OR_CONTEXT}} | During implementation / CI | Dev |
| Integration | Component interaction intent | {{INTEGRATION_TEST_FRAMEWORK_FROM_ARCH}} | During implementation / CI | Dev |
| E2E | Full user-flow validation intent | {{E2E_TEST_FRAMEWORK_FROM_ARCH}} | Post-implementation | QA + Dev |
| API Contract | Request/response schema intent | {{CONTRACT_TEST_TOOL_FROM_ARCH}} | During implementation / CI | Dev |
| Performance | Load & stress validation intent | {{PERF_TEST_TOOL_FROM_ARCH_OR_CONTEXT}} | Pipeline / pre-release | Dev + QA |
| Security | Vulnerability and abuse-case intent | {{SECURITY_TEST_TOOL_FROM_ARCH_OR_CONTEXT}} | Pipeline / security review | Security + Dev |
| Accessibility | WCAG validation intent | {{A11Y_TEST_TOOL_FROM_ARCH_OR_CONTEXT}} | During implementation / QA review | Dev + QA |
| Manual / Exploratory | Edge cases, UX validation | Manual | QA execution stage | QA |

**API Contract testing rule**: Ưu tiên consumer-driven contract testing khi frontend / downstream service phụ thuộc chặt vào response schema. Consumer team viết contract; provider verify contract trong CI trước merge / release.

## 4. Test Environment

| Environment | Purpose | Data | Access |
|------------|---------|------|--------|
| Local | Developer implementation and test wiring | Seed data, fixtures | Dev team |
| CI | Later automated execution target | Ephemeral test DB, fixtures | CI pipeline |
| Staging | Later integrated validation target | Anonymized production data | QA team |

### Test Data Strategy

<!-- Phase Test defines data requirements only. It does not generate runtime TSV/SQL data packs or secrets. -->

- **Golden dataset**: <!-- Base happy-path dataset used for mutation, if applicable. -->
- **Mutation strategy**: <!-- Which fields/conditions mutate for BVA, EP, negative cases, rule precedence, rollback, etc. -->
- **PII / sensitive data rule**: <!-- Synthetic only, masking requirement, forbidden production data. -->
- **Isolation model**: <!-- Ephemeral DB, isolated schema, prefixed records, tenant sandbox, etc. -->
- **Teardown/reset expectation**: <!-- API reset hook, fixture cleanup, transaction rollback, seed refresh, manual reset, etc. -->
- **Repo unit-test data requirement**: In-memory fixture / factory / builder needs for Dev-owned repo tests
- **Integration-test data requirement**: Test database, reset per test suite
- **E2E data requirement**: Seeded test data, deterministic state
- **Performance data requirement**: Realistic dataset size / shape needed later ({{PERF_DATA_SIZE}} records), without generating the dataset in Phase Test

## 4a. External QA Handoff Summary

<!-- Use when testers / QC automation execute outside the product repo or in a separate automation repo. -->
<!-- This is a handoff contract, not execution output. -->

| Handoff Need | Detail | Source / Owner | Status |
|---|---|---|---|
| Target environment | local / QA / staging / UAT / pipeline | | ready / TBD |
| Stable UI selectors | `data-testid` / aria-label / route hooks required | Dev / Design | |
| API contracts | Endpoint refs and schema refs required by QC automation | Architecture | |
| Seed/reset hooks | API / script / process for deterministic data setup and teardown | Dev / Ops | |
| Test accounts | Roles only; secrets stored outside PRISM | QA / Ops | |
| Feature flags/config | Flags required before QC can execute | Dev / Ops | |
| Evidence expectation | screenshot / API response / logs / automation report | QA | |

> **Boundary**: external QC automation packs and execution reports may live outside PRISM. They are not repo test delta and are not generated by Phase Test.

## 5. Entry Criteria

Planning is complete when:

- [ ] Every in-scope feature has defined test intent
- [ ] Planned automated vs manual boundaries are clear
- [ ] Required test data is identified
- [ ] Future execution environments are identified
- [ ] Release-critical risks have explicit validation coverage
- [ ] Branch Discovery Summary exists for rule-heavy / complex branching / high-risk SIT features, or is explicitly N/A
- [ ] External QA Handoff Summary is complete when testers or automation live outside the product repo

## 6. Exit Criteria

Execution success is measured later when:

- [ ] Tất cả TC-P0 cases implemented và pass — không có P0 failure tồn tại
- [ ] Tất cả TC-P1 cases implemented và pass — hoặc explicitly deferred với sign-off
- [ ] Unit test coverage ≥ **{{UNIT_COVERAGE_TARGET}}%** *(default: 90% — lấy từ NFR nếu khác)*
- [ ] Integration test coverage: tất cả API endpoints có ít nhất 1 integration test (happy + 1 error path)
- [ ] 0 Critical defect open
- [ ] 0 High defect open (hoặc đã có accepted workaround với sign-off)
- [ ] Performance tests pass theo p50/p95/p99 targets từ NFR-xxx
- [ ] Security tests pass: SQL injection, XSS, IDOR, JWT, CSRF, rate limiting
- [ ] Accessibility: 0 WCAG 2.1 AA violations từ automated scan (axe-core / Lighthouse)
- [ ] QA sign-off trên exploratory execution cho P0 user flows
- [ ] Regression strategy được thực thi theo định nghĩa ở §7

## 7. Regression Strategy

<!-- Khi nào chạy regression gì — không có strategy rõ ràng → team tự quyết → inconsistent coverage. -->
<!-- Risk matrix ở §8 ảnh hưởng đến depth của regression. -->

| Trigger | Regression Scope | Duration Estimate | Owner |
|---|---|---|---|
| Hotfix / urgent patch | Smoke test: P0 test cases cho affected features + core happy paths | ~30 phút | Dev + 1 QA |
| Feature branch merge vào dev | Targeted regression: affected feature area + integration points | ~1–2 giờ | Dev |
| End of sprint / release candidate | Full regression: tất cả P0 + P1 test cases | ~4–8 giờ | QA |
| After infrastructure change (DB migration, 3rd party update) | Risk-based regression: P0 data integrity + integration tests | ~2–3 giờ | Dev + QA |
| Before go-live (production deploy) | Full regression + smoke test sau deploy | Full + 30 phút post-deploy | QA + Dev |

**Automated regression gate** *(CI/CD pipeline)*:
- Pull request → run: unit tests + integration tests
- Merge to main → run: unit + integration + E2E smoke tests
- Release tag → run: full test suite

## 8. Risk-Based Test Priority

| Risk Area | Likelihood | Impact | Test Priority | Test Depth |
|-----------|-----------|--------|--------------|-----------|
| Authentication / authorization | High | Critical | P0 | Deep (all paths) |
| Payment / financial transactions | High | Critical | P0 | Deep + edge cases |
| Data integrity | Medium | High | P0 | All CRUD paths |
| Third-party integrations | Medium | High | P1 | Happy + error paths |
| UI rendering | Low | Medium | P2 | Key flows + responsive |

## 9. Defect Management

| Severity | Definition | Response Time | Resolution SLA |
|----------|-----------|--------------|----------------|
| Critical | System down, data loss, security breach | Immediate | Same day |
| High | Core feature broken, no workaround | < 4 hours | Next delivery phase |
| Medium | Feature impaired, workaround exists | < 1 day | Within 2 delivery phases |
| Low | Cosmetic, minor inconvenience | Best effort | Backlog |

## 10. Test Reporting

| Report | Frequency | Audience | Contents |
|--------|----------|---------|----------|
| Planning review | During planning | Tech Lead, QA, Dev | Coverage map, risks, execution intent |
| Implementation checkpoint | During coding | Dev team | Which planned tests are implemented |
| External release test report | Pre-release, if execution is run | All stakeholders | Execution results, risk assessment, go/no-go |
| Generated TSV companions | During `start test` / `validate test` | QA / external QC | Functional/SIT import views generated from the active `docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md`; not manually edited |

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `TEST-1`, `TEST-2`, `TEST-3`, `TEST-3b`, `TEST-4`, `TEST-5`, `TEST-6`, `TEST-7`, `TEST-8`
- [ ] Mọi Must Have FR (P0) đều có test coverage plan
- [ ] `Coverage Traceability Index` nối được Must Have FR / prioritized NFR xuống design / API / project-boundary refs, TC IDs hoặc gap note rõ ràng
- [ ] Test types phù hợp với từng area (không phải mọi thứ đều cần E2E)
- [ ] §6 Exit Criteria có số cụ thể: coverage %, defect count, performance targets — không có item vague
- [ ] §7 Regression Strategy có trigger, scope, duration estimate, owner cho mỗi scenario
- [ ] Risk matrix ở §8 dựa trên actual FRs của project — không phải ví dụ generic (Auth/Payment/DataIntegrity)
- [ ] Planning criteria measurable; execution criteria clearly deferred đến implementation phase
- [ ] Test tools specified và available trong team
- [ ] Test data strategy cover tất cả test types bao gồm PII masking guidance
- [ ] Branch Discovery Summary exists for complex features or is explicitly N/A with reason
- [ ] External QA Handoff Summary is complete when testers / QC automation execute outside the product repo
- [ ] Defect severity definitions rõ ràng và actionable
- [ ] Performance benchmarks reference NFR targets từ PRD
- [ ] Phase Test KHÔNG ghi repo test delta, generated runtime data packs, or external QC automation code — chỉ owns test intent và generated TSV companions từ markdown
- [ ] Mỗi Must Have FR có test design đủ để Dev viết repo test delta tương ứng mà không phải hỏi lại QA (`TEST-2` Execution-Ready + Implementation-Consumable Handoff)
- [ ] Generated TSV companions under `testing/generated/` đã được export từ active `proposals/test-cases-v{X}.md` và không edit tay (`TEST-8`)
