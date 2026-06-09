# Testing Standards

This standard supports Phase Test. It defines reusable QA rules for coverage design, defect taxonomy, exploratory checks, accessibility, authorized security testing, performance baselines, and external QA handoff.

## 1. Coverage Dimensions

Use these dimensions when authoring or validating `docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md` TC items.

| Dimension | Required When | Minimum Expectation |
|---|---|---|
| AC positive / negative | User Story has acceptance criteria | At least one positive and one negative path per release-critical AC |
| BR / rule coverage | PRD / BRD / story defines business rules | Every in-scope rule maps to TC IDs or `N/A + reason` |
| Basic flow | Feature has a primary user/system flow | One executable happy path with concrete data |
| EP / BVA | Inputs have type, range, length, format, enum, or threshold | Representative valid/invalid partitions and boundary values |
| Decision table / data-driven | Logic has 2+ meaningful conditions | Cover important combinations, precedence, fallback, and default paths |
| State transition | Flow has explicit states or lifecycle | Valid and invalid transitions; final state is asserted |
| Corner / error guessing | User input, concurrency, retries, external calls, or high-risk UX exists | Idempotency, race, timeout, duplicate action, stale data, and network failure where relevant |
| Impact / regression | Existing flow, contract, data, or integration can be affected | Core unaffected flows and contract compatibility checks |
| NFR | NFR or risk requires it | Security, performance, reliability, accessibility, or observability checks as relevant |
| SIT | Multi-system / module / async / external dependency exists | Contract, failure, retry/idempotency, rollback/compensation, async, and consistency checks |

Not every feature needs every dimension. Any omitted applicable dimension needs `N/A + reason`.

## 1.5 Per-AC Technique Application Rules

This catalog drives the **Per-AC Technique Decision Matrix** in `test-cases-template.md §3.5`. For every in-scope AC, decide Yes/No for each of the five techniques below using these rules. A "Yes" decision MUST cite the AC clause that triggers it; a "No" decision MUST give a concrete reason (not generic "not applicable").

Each entry below has: **Trigger** (when Yes), **Emit pattern** (what TCs to produce), **Example** (one AC → one TC), **Exclusion** (when explicitly No — guards against bulk-tagging).

### BVA — Boundary Value Analysis

- **Trigger** — AC defines a numeric range, threshold, limit, duration, size, count, percentage, or any quantitative edge. Quote the boundary clause when marking Yes.
- **Emit pattern** — for each boundary `N`, emit TCs at `{N-1, N, N+1}` (or `{below, at, above}` where strict equality matters). When all variants share the same expected-result shape, fold them into one Data-Driven TC tagged `[BVA+DD]` rather than three separate TCs.
- **Example** — AC "cache TTL = 300s" → BVA TCs: `[BVA] 299s still cached (cacheHit=true)`, `[BVA] 301s cache expired (cacheHit=false)`.
- **Exclusion** — do NOT mark Yes if the input is enum/role/categorical, or if the AC describes a flow without a quantitative edge. Performance assertions like `p95 < 800ms` are BVA only if the test actually probes near 800ms; a single happy-path measurement is just Positive.

### EP — Equivalence Partitioning

- **Trigger** — input has two or more meaningful equivalence classes (roles, types, statuses, mask categories, regex groups, status enums). Cite the classes when marking Yes.
- **Emit pattern** — one TC per class for both valid and invalid partitions. When the partitions are uniform in shape, fold into one Data-Driven TC iterating the classes.
- **Example** — BR-15 "mask 7 sensitive fields (password, secret, token, …)" → one EP TC iterating all 7 fields with masked-equality assertion.
- **Exclusion** — do NOT mark Yes if input has a single value, or if all partitions collapse to the same TC (no behavioral split). Don't mark Yes purely because the field has a type — types alone don't justify EP.

### DT — Decision Table

- **Trigger** — AC combines two or more conditions via AND/OR with non-trivial outcomes (e.g., `format-valid AND schema-valid AND not-duplicate → success`). Decision precedence or fallback paths also qualify.
- **Emit pattern** — one TC per significant decision-table row, or one Data-Driven TC (tagged `[DT+DD]`) whose data rows mirror the table. Minimum coverage: (a) the all-true / "happy" row, (b) the all-false / fully-invalid row, and (c) one TC per condition where flipping just that condition (others held to the happy state) changes the outcome — this isolates each condition's contribution.
- **Example** — Import row outcome = f(format-valid, schema-valid, dup-check) → DT TCs: all-valid → success; format-invalid → reject; schema-invalid → reject; duplicate → reject; partial mix → partial-success.
- **Exclusion** — do NOT mark Yes if AC has a single condition, a linear flow, or only Positive/Negative branching on one input.

### ST — State Transition

- **Trigger** — AC implies a state machine (lifecycle, cache state, draft/published, active/inactive, processing/done/failed). Cite the state set and the transitions when marking Yes.
- **Emit pattern** — one TC per valid transition path; assert final state. Add one TC per invalid transition the AC explicitly forbids.
- **Example** — Cache "cold → warm → invalidate → warm" → one ST TC walking 3 transitions, asserting `cacheHit` flag at each step.
- **Exclusion** — do NOT mark Yes if the flow is stateless or each call is independent. A repeated idempotent call is not a state transition.

### DD — Data-Driven

- **Trigger** — the same behavior must be verified across three or more meaningful input variants that share an expected-result shape (e.g., three permission paths all yielding "has permission"; multiple sensitive fields all yielding "masked"). Cite the variant set.
- **Emit pattern** — one DD TC with an input/expected table embedded in the Test Data block. Do NOT emit three separate Positive TCs when one DD TC captures them.
- **Example** — "User has permission via direct grant / via role-with-perm / via role-without-perm" → one DD TC with three rows: direct → has; role-with-perm → has; role-without-perm → has-not.
- **Exclusion** — do NOT mark Yes if variants need different setup or different expected shape — those belong to separate Positive/Negative TCs. Two variants is borderline; prefer DD only at ≥3.

### Multi-technique combination

A single TC may legitimately apply more than one technique. When this happens, the title prefix combines tags with `+` (see `test-cases-template.md §1 Conventions`). The matrix cell counts the TC under every applicable technique row, but the TC ID column lists the TC once.

Common pairings to recognize:

- **`[BVA+Negative]`** — boundary value on a negative path (e.g., `[BVA+Negative] 5001 rows fails client-side` for a 5000-row limit).
- **`[BVA+DD]`** — three boundary values folded into one Data-Driven TC.
- **`[EP+DD]`** — equivalence classes iterated as one Data-Driven TC (e.g., 7 sensitive fields → one `[EP+DD]` TC instead of 7 separate ones).
- **`[DT+DD]`** — decision-table rows materialised as one Data-Driven TC.
- **`[ST+Security]`** — a state transition whose transitions cross a security boundary (e.g., policy lifecycle `DRAFT → ACTIVE` where the actor must hold elevated permission for the transition itself).

Tie-breaker when two techniques each independently fit: prefer the more specific/structural one (BVA over Positive; DT over Negative; ST over Positive) and add the secondary with `+`. Never drop a tag just to keep the title short.

### Non-technique edge cases remain required

The five techniques above are **necessary, not sufficient**. Edge cases that do NOT map cleanly to any of {BVA, EP, DT, ST, DD} belong to the `Corner / error guessing` dimension in §1 and to the `Corner / Error Guessing` column of the Coverage Category Checklist in `test-cases-template.md §4`. Examples (none of these should appear as `Y` in the matrix):

- **Pure infrastructure failure**: dependency service unreachable (search backend down, message queue partition), object storage returns 404 on a previously-valid object, container OOM kill mid-request.
- **Race conditions / concurrency**: two writers updating the same record simultaneously, double-click triggering duplicate side effect, retry colliding with a successful first attempt.
- **Worker / queue path failures**: job poisoned and routed to DLQ, transient retry succeeds on Nth attempt, scheduler missing a tick.
- **Mid-transaction failures**: client disconnect after server commit, network drop mid-multipart-upload, partial write detected by checksum.

Disambiguation against matrix techniques:

- A **boundary** value (file size = 10MB exact, TTL = 300s exact, p95 = 800ms exact) → **BVA** in matrix, NOT Corner.
- A **state transition** (cache cold→warm, policy DRAFT→ACTIVE, admin role grant→revoke) → **ST** in matrix, NOT Corner.
- An **infrastructure outage** with no state machine and no boundary → Corner / Error Guessing.

These TCs must still be authored regardless of the matrix outcome.

## 2. Rule / Branch Inventory

When upstream artifacts contain AC IDs, BR IDs, rule IDs, decision-table rows, named branches, or state transitions:

- list every item in the Rule / Branch Inventory
- map each item to TC IDs
- use `N/A + reason` only when the item is out of scope or not testable in this sprint
- do not mark Test complete while in-scope items have blank coverage

## 3. Defect Taxonomy

Severity:

| Severity | Meaning | Examples |
|---|---|---|
| S1 Critical | Core flow blocked, data loss, crash, serious security issue | checkout broken, data deleted, auth bypass |
| S2 High | Main feature broken with no acceptable workaround | search wrong, upload silently fails, redirect loop |
| S3 Medium | Feature impaired but workaround exists | slow page, weak validation, mobile layout broken |
| S4 Low | Minor issue with limited functional impact | typo, small alignment issue, cosmetic inconsistency |

Priority:

| Priority | Action |
|---|---|
| P1 | Fix immediately / blocks release |
| P2 | Fix in current delivery window |
| P3 | Plan for next delivery window |
| P4 | Backlog / nice-to-have |

Categories:
- Functional
- Visual / UI
- UX
- Content
- Performance
- Console / Errors
- Accessibility

Every defect should have severity, priority, exactly one category, reproducible steps, expected vs actual, and evidence when applicable.

## 4. Exploratory Testing

Use exploratory checks when scripted cases are insufficient or when UI/user-flow risk is high.

Per-page checks:
- visual scan: layout, broken images, alignment, overflow
- interactive elements: buttons, links, hover, menus, tabs
- forms: empty submit, valid submit, boundary input, validation clarity
- navigation: breadcrumb, browser back, deep link, menu links, dead ends
- states: empty, loading, populated, error, overflow
- console/network: JavaScript errors, 4xx/5xx, important warnings
- responsive: mobile layout, touch targets, text overlap

Tiers:
- Quick: core flows only, roughly 15-30 minutes
- Standard: sprint scope, roughly 1-2 hours
- Exhaustive: broad app/edge coverage, 3+ hours

Exploratory defects need enough evidence for independent reproduction.

## 5. Accessibility Testing

Default target is WCAG 2.1 AA unless NFR specifies another level.

Minimum checks:
- meaningful `alt` text for informative images
- keyboard navigation, visible focus, no unintended focus trap
- labels and error messages for form controls
- text contrast: 4.5:1 for normal text, 3:1 for large text and UI components
- semantic landmarks and heading hierarchy
- ARIA only when native semantic HTML is insufficient
- reduced-motion support where motion can affect users
- responsive/zoom at 200% without unusable overflow

Automated tools such as axe or Lighthouse are useful but do not replace keyboard and screen-reader checks for high-risk flows.

## 6. Authorized Security Testing

Security testing must be scoped and authorized. Do not run invasive tests against production unless the user explicitly provides approval and scope.

Common checks:
- A01 Broken Access Control: IDOR, privilege escalation, restricted pages, method tampering
- A02 Cryptographic Failures: HTTPS, cookie flags, secrets/tokens in URL, unnecessary sensitive response fields
- A03 Injection: SQLi, XSS, path traversal on safe non-production inputs
- A04 Insecure Design: rate limiting, password reset, workflow bypass, business logic abuse
- A05 Misconfiguration: stack traces, debug mode, public docs, missing security headers
- A07 Authentication Failures: brute force controls, session invalidation, JWT tampering
- A08 Integrity Failures: upload validation, webhook signatures, deserialization validation
- A09 Logging / Monitoring: security event logging without sensitive data leakage
- A10 SSRF: user-controlled URL fetch controls in authorized environments

Record safe repro steps, endpoint/screen, expected vs actual, severity, impact, and recommended fix. Do not paste sensitive secrets into public reports.

## 7. Performance Baseline

Use NFR targets first. If absent, use these defaults as prompts, not absolute release gates:

| Area | Default Target |
|---|---|
| Simple API P95 | <= 500ms |
| Business API P95 | <= 1000ms |
| Third-party integration P95 | <= 3000ms |
| Error rate under expected load | < 1% |
| Web LCP | <= 2.5s for normal pages, <= 4s for data-heavy pages |
| CPU sustained | < 80% unless architecture states otherwise |

Performance test cases must state environment, dataset size, concurrency, duration, warm-up, p50/p95/p99, error rate, and bottleneck evidence to collect.

The performance tool is consumed from Architecture or project context. Do not hardcode JMeter, k6, Locust, or any other tool as PRISM default.

## 8. Test Data And Teardown

Test cases that depend on data must specify:
- fixture/seed source
- synthetic/PII-safe requirement
- golden dataset and mutation strategy when relevant
- isolation model
- setup responsibility
- teardown/reset expectation

Phase Test defines requirements. It does not generate runtime datasets, SQL teardown, credentials, or external `testing-output/` files.

## 9. Generated TSV Export

`docs/sprint-v{X}/testing/proposals/test-cases-v{X}.md` is the active sprint source of truth for TC items until sprint seal merges them into `/docs/testing/test-cases.md`. Generated Functional/SIT TSV companions are export views for QC import/handoff and must be derived deterministically from the active sprint Markdown.

Required generated files:
- `testing/generated/test-cases-functional-v{X}.tsv`
- `testing/generated/test-cases-sit-v{X}.tsv`
- `testing/generated/test-cases-export-manifest-v{X}.json`

Do not edit generated TSV files by hand. If they drift from the Markdown, regenerate them with `core/tools/export_test_cases.py`.

## 10. Automation Intent And External QA Handoff

Phase Test may define automation intent:
- `Auto=Y/N` with reason
- target level: `component`, `integration`, `e2e`
- expected suite/script owner: repo test delta or external QC automation
- required selectors/API contracts/data
- target run environment
- expected evidence

Runnable automation code is not generated by Phase Test.

If testers or automation live outside the product repo, Test artifacts should include handoff needs:
- target environment
- stable selectors / `data-testid`
- API contracts
- seed/reset hooks
- test account roles with secret references only
- feature flags/config
- evidence expectations

External QC automation packs and execution reports are external evidence unless PRISM adds a dedicated execution/release workflow.
