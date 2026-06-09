# Unit + Integration Test Standards (repo test delta)

This standard governs the **runnable repo test delta** the AI generates during **Phase Implement** — the unit and integration tests that ship inside the codebase (dev-owned `repo_test_delta_target`). It is the runnable-test counterpart of `testing-standards.md` (which governs the QA test-intent lane). The two lanes are **independent**: QA (Phase Test) is the final acceptance gate; Implement must still finish its own internal tests. Implement **reuses the ISTQB knowledge** in `testing-standards.md §1.5` but does not depend on QA artifacts.

## 0. Division of labour — PRISM vs CI

PRISM is a generator. It applies the test-design discipline below and runs the project's already-available local test commands (per `phase-implement.md` step 11). It does **not** run coverage/mutation as a quality gate.

| PRISM (Implement) does | Project / user / CI does |
|---|---|
| Generate tests with the right technique (unit + integration), with deterministic seams | Run coverage on push and enforce the threshold |
| Emit the technique-evidence table for the test delta | Dashboards, flaky management, multi-stack verdict |
| Run already-available local test commands (unit / integration / contract slice) | — |
| **Suggest** running mutation (with an ETA); run it **only on user request** and write the report to the Implement output folder | (optionally) run mutation in CI / nightly |

PRISM's only hard test gates are **structural** (`CODE-3a` / `CODE-3c`, §10): technique evidence present + deterministic + property selection. Coverage is a single flat DOD target (§1). **Mutation is optional** — never auto-run, never a blocker (§7).

## 1. Coverage standard (single, flat — no tiers)

One flat standard for the whole repo test delta (no tiers): on new / changed code, **line coverage ≥ 90%** (`quality_profile.coverage_min_new_code`) **AND branch coverage ≥ 90%** (`quality_profile.coverage_branch_min_new_code`). For **Swift**, measure **region** coverage in place of branch (llvm-cov has no real branch coverage). Measure on **new / changed logic only** — code merely *moved* during a refactor does not count as new. Apply the §8 exclusions (don't force coverage on trivial / generated / DTO / config code).

Both default 90; the same 90% applies everywhere (no risk tiers). `coverage_min_new_code` is base-PRISM's line-coverage field; `coverage_branch_min_new_code` adds the branch (region-for-Swift) requirement.

## 2. Technique discipline (unit)

Reuse the ISTQB catalog in `testing-standards.md §1.5` (full Trigger / Emit / Example / Exclusion rules live there). Apply **by code shape**, never blanket:

| Technique | Apply when the code… |
|---|---|
| **BVA** (boundary) | has a numeric range / threshold / limit / size / count / duration |
| **EP** (equivalence partitioning) | has ≥2 meaningful input classes (roles, types, status enums) |
| **Decision Table** | combines ≥2 conditions with non-trivial outcomes / precedence |
| **State Transition** | implements a state machine / lifecycle |
| **Negative / error-path** | rejects invalid input, throws, or returns an error result |
| **Corner / error-guessing** | has concurrency, retries, external calls, or high-risk edges that map to none of the above |

- **`N/A + reason`** (anti bulk-tagging): if a surface fits no technique (glue / simple mapper), write `N/A — <concrete reason>`. Do not bulk-tag; generic reasons like "not needed" are rejected — same discipline as `testing-standards.md §1.5`.
- **Fold to chống nổ số test**: a data-driven (parameterised) test = **one behaviour, many inputs**. Fold BVA `{N-1, N, N+1}`, EP classes, and DT rows into one parameterised test (`[BVA+DD]`, `[EP+DD]`, `[DT+DD]`) instead of many separate tests. This is consistent with "one behaviour per test".

## 3. Technique discipline (integration — only when there is an integration surface)

Integration tests are **required only when the task has an integration surface**: public API, DB transaction, external dependency, async / event / queue, cross-module contract, or runtime behaviour that must be verified across modules. **Pure unit logic does not need an integration test** — record `N/A + reason` in `repo_test_delta_target`.

When required, integration coverage reuses the **SIT** dimension of `testing-standards.md §1`:

- **Contract / schema** between modules (request/response shape, error shape).
- **Failure-injection**: dependency unavailable, timeout, partial failure.
- **Retry / idempotency**: repeated delivery, duplicate side-effect protection.
- **Rollback / compensation**: transaction boundary, partial-write recovery.
- **Async / event / queue path**: event published/consumed, DLQ, ordering where it matters.
- **Data consistency** across modules / stores.

BVA/EP/etc. rarely fit integration tests; integration leans on failure & contract. Property-based and mutation are primarily **unit** techniques.

## 4. Evidence of technique coverage

Do **not** rely on test names alone (unreliable and hard to parse across Java/Python/TS/Swift). Use one of these, **(a) preferred**:

| Format | What | Verifiable |
|---|---|---|
| **(a) structured-table** (preferred) | In `repo_test_delta_target`, a table `test_file → test_case → AC/requirement → techniques → observable_assertion` | ✅ deterministic |
| (b) annotation / comment | `@Tag` / `@Technique` annotation or a standard comment beside the test | ⚠️ needs per-stack parser |
| (c) name-prefix | Test name prefix `[AC-001][BVA]…` | ⚠️ weakest, fallback only |

The `observable_assertion` column forces each row to name a real assertion on output/state (ties into anti-tautology §5).

## 5. Anti-tautology + deterministic (quality of the test itself)

- **One behaviour per observable test**; assert on **spec / observable output / state**, not on implementation internals.
- A test whose only assertion is "mock called N times" is **not** acceptable — at least one assertion must be on real output/state.
- Every test must be able to **fail** if behaviour is wrong (no always-green tests).
- **Deterministic** (prevents flaky tests at the source, no quarantine infra needed): no real `now()` / clock, no real network / DB, no unseeded randomness, no `sleep`. Inject time / randomness / IDs / I/O behind a seam — this is the test-side counterpart of `CODE-8` (test seam presence).

## 6. Property-based testing (selective, not blanket)

Property-based testing is powerful but not every "pure" function has a good property; forcing it everywhere makes the AI write shallow properties to pass the gate. Two classes:

- **`property_required`** (must ship ≥1 property test): parser, serializer / encoder / decoder, validator, state-reducer, non-trivial algorithm.
- **`property_or_examples`** (property **OR** an explicit example-set covering invariant + boundary): small business rule, simple mapping / transform.
- **Anti-gaming**: a property must assert a **real invariant** — round-trip (`decode(encode(x)) == x`), idempotency, monotonicity, conservation — not a tautology. Cap `max_examples` (default 200) and use a **fixed seed** in CI. Do not apply to I/O glue.

## 7. Mutation testing (OPTIONAL — suggested, never auto-run)

Mutation score is the strongest objective signal of test quality (it injects bugs and checks the tests catch them), but it is expensive and stack-dependent (e.g. Swift `muter` recompiles per mutant → slow; see §9). So in PRISM it is **optional, not a gate**:

- PRISM **never auto-runs** mutation and **never blocks** on it.
- After an implement step, PRISM **suggests** running mutation alongside the other next-step suggestions (validate, next task group), stating an **estimated time** and the tool for the stack (§9), and noting that PRISM can run it on request (it must modify source to do so).
- If the user requests it, PRISM runs it (diff-scoped where possible) and writes the report into the **Implement output folder** (e.g. `docs/sprint-v{X}/implementation/`).
- Advisory target when run: `suggested_min_score` (default 80); surviving mutants should be **triaged** (killed by a new test, or marked equivalent with a reason). None of this blocks.
- Run mechanics (timeout, scope, baseline, flaky-mutant handling) are the user's / CI's concern, not PRISM's.

**Trade-off (stated honestly):** because mutation is opt-in, the structural gates (§10) are largely **self-graded** by the same AI that wrote the code. Suggest mutation more insistently on sensitive code (auth / payment / PII / money / data-loss), where that risk matters most.

## 8. Guardrails — don't over-generate

1. Measure coverage on **new/changed logic only** (branch; region for Swift); never whole-repo; never force trivial accessors.
2. **Exclusions** (no test required): `generated-code`, `dto-data-class`, `trivial-accessor`, `framework-config`, `logicless-migration`, `pure-presentational-ui`.
3. **Fold** to data-driven instead of many separate tests.
4. Property-based only for pure logic; **pairwise** (all-pairs) instead of full combinatorial when a function has ≥3 independent parameters — pairwise is an option **inside** technique discipline (`CODE-3a`), not a separate rule.
5. Mutation is **optional / suggested** — never forced, never blanket.
6. **Do not use** MC/DC, full combinatorial, or blanket fuzzing.
7. `N/A + reason` instead of forcing a technique that doesn't fit.

## 9. Tool matrix per stack (project CI chooses; PRISM does not bundle)

| Stack | Coverage | Property-based | Mutation |
|---|---|---|---|
| Java | JaCoCo (branch) | jqwik | PIT (pitest) |
| Kotlin | Kover / JaCoCo | Kotest property / jqwik | PIT (watch inline/coroutine noise) |
| Python | coverage.py `--branch` | Hypothesis | mutmut / cosmic-ray |
| TypeScript | c8 / istanbul (nyc) | fast-check | StrykerJS |
| JavaScript | c8 / istanbul (nyc) | fast-check | StrykerJS |
| Swift | llvm-cov (**region**, no branch) | SwiftCheck | muter |
| React Native | Jest (JS/TS) | fast-check | StrykerJS (JS); native bridge → stack-appropriate tool |

## 10. Rules and gate split

These rules are sub-rules of `CODE-3` (registered in `core/phase-quality-standards.md § Core Rule Registry`):

| Rule | Kind | What |
|---|---|---|
| `CODE-3a` | **PRISM gate (structural)** | Tests carry technique evidence (structured-table preferred) for unit **and** integration (when surface exists); negative & pairwise live inside 3a; `N/A + reason` when no technique fits; tests are deterministic. Missing evidence for a surface with boundary/multi-condition/state/failure path is a blocker. |
| `CODE-3b` | **Coverage DOD target** | On new code: **line ≥ 90%** (`coverage_min_new_code`) AND **branch ≥ 90%** (`coverage_branch_min_new_code`; region for Swift); exclusions apply. PRISM runs local tests + reads coverage when available; the project / CI is the authoritative enforcer. |
| `CODE-3c` | **PRISM gate (structural, light)** | `property_required` surfaces ship ≥1 real-invariant property test; `property_or_examples` accept a property OR an explicit example set covering invariant/boundary. |
| `CODE-3d` | **Optional — suggested, not a gate** | Mutation is suggested (with ETA), run **on user request**, report written to the Implement output folder. Advisory target `suggested_min_score`; never blocks. |

Reports/evidence live in the **Implement output folder** (e.g. `docs/sprint-v{X}/implementation/`), not a separate testing folder. PRISM reads a report if present; nothing blocks on a missing mutation report.

## 11. Freedom mode

Stable IDs (DOC-2) — including `AC-NNN` via `get_next_id.py` — exist in Freedom mode too, so the technique-evidence table anchors to AC/requirement IDs the same way. The difference: Freedom has no gate/approval flow, so `CODE-3a` / `CODE-3c` run as **self-review / quality items**, not blockers. Everything else in this standard applies unchanged.
