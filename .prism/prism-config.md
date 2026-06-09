# PRISM Project Configuration

<!-- This file is lightweight runtime context that every PRISM phase can read.
  Keep only stable facts you already know at setup time.

  Do not try to pre-fill everything here:
  - tech choices belong in the architecture conversation
  - team names belong in your normal collaboration tools
  - delivery conventions can be decided during planning / implementation

  Replace placeholders inside the YAML block.
  Keep the YAML structure, quotes, and array format intact. -->

<!-- Standards path resolution:
  PRISM phase prompts resolve standards location through `prism.json` → `paths.standards`
  (default `.prism/core/standards`).
  - Project layout custom (monorepo / vendored / symlinked)? Override `paths.standards`
    in `prism.json` to your real location.
  - Phase prompt always reads `<paths.standards>/INDEX.md` first to know which standards
    files to load when. INDEX.md is the source of truth for "which standard, when".
  - If `prism.json` or `paths.standards` is missing, prompts fall back to default
    `.prism/core/standards` for backward compat. -->

```yaml
prism:
  version: "__PRISM_VERSION__"  # installed PRISM version — set by setup.sh / setup.sh --upgrade
  mode: "guided"               # guided | freedom

project:
  name: "{{PROJECT_NAME}}"
  summary: ""                  # optional — one sentence is enough

sprints:
  - id: v1
    sealed: false              # Guided seals on approve implement; Freedom keeps sprints editable

# Atomic ID counters (21 prefixes, per PRISM v2.0.0 model).
# Read + bumped by `core/tools/get_next_id.py --type {EP|FR|US|AC|BR|NFR|TC|SCREEN|DS-COMP|ARCH-COMP|ARCH|GLOSS|PERSONA|MR|SEQ|ENT|ADR|FLOW|API|EVT|PR}`.
# If this block is absent, get_next_id will bootstrap it on first call.
# v2.0 migration: `EPIC` → `EP` (one-time, preserves value) and split `COMP`
# → `DS-COMP` (design system UI) + `ARCH-COMP` (architecture component boundary).
id_counters:
  # Product
  EP: 0
  FR: 0
  US: 0
  AC: 0
  BR: 0
  GLOSS: 0
  PERSONA: 0
  MR: 0
  # Design
  SCREEN: 0
  DS-COMP: 0
  # Architecture
  ARCH: 0
  ARCH-COMP: 0
  NFR: 0
  SEQ: 0
  ENT: 0
  ADR: 0
  FLOW: 0
  API: 0
  EVT: 0
  PR: 0
  # Testing
  TC: 0

# Quality profile — schema v2
# Read by phase prompts and validate commands. Missing fields fall back to defaults
# defined in core/phase-quality-standards.md § Quality Profile.
quality_profile:
  review_modes_required: [spec, quality]    # validate modes Plan declares and Implement self-applies before declaring the scope done; Guided approval also requires them
  repo_test_delta_required: true            # non-trivial code change must ship repo test delta or substantive justification
  coverage_min_new_code: 90                 # LINE coverage on new code >= 90% (base-PRISM field). Paired with coverage_branch_min_new_code below.
  require_contract_tests: conditional       # always | never | conditional (cross-service / public APIs)
  required_standards_profiles: [architecture-principles, architecture-solution, backend, security, devsecops]  # add frontend / ai / iot when applicable
  manual_observation_required_for_ui: true  # Test phase must include manual observation TCs for UI changes
  work_hours_per_day: 6                     # default hours per day per developer working WITH the AI (prompt + review + feedback). The remaining ~2h of the workday absorbs stand-ups / peer review / meetings. Read by Plan when sizing task groups and computing the cumulative day range.

  # --- Unit + Integration test quality (schema v2) — read by Implement; full rules in core/standards/unit-test-standards.md ---
  # Coverage standard on new code (flat, no tiers): BOTH line >= 90% (coverage_min_new_code above) AND branch >= 90% (coverage_branch_min_new_code below).
  # Mutation is OPTIONAL: PRISM never auto-runs it — it only suggests it (with an ETA); it runs only on user request, then writes the report to the Implement output folder.
  coverage_branch_min_new_code: 90          # BRANCH coverage on new code >= 90% (region for Swift, whose llvm-cov has no branch). No tiers.
  test_design:
    technique_source: testing-standards-1.5 # ISTQB catalog reused as knowledge; applied INDEPENDENTLY of QA lane
    reuse_qa_matrix: optional               # MAY read-only the qa_test_refs Per-AC matrix if Test is already approved; not required, no coupling
    techniques_by_code_shape: [EP, BVA, Negative, DT, ST]   # apply by code shape, never blanket
    integration_when_surface: true          # IT required only when task has an integration surface; pure unit → N/A + reason
    na_with_reason: required                # shape fits no technique → write `N/A — <concrete reason>` (anti bulk-tagging)
    technique_evidence: structured-table    # structured-table (preferred) | annotation-comment | name-prefix — emitted by Implement
    one_behavior_per_test: true             # data-driven = one behaviour, many inputs (not many behaviours)
    assert_behavior_not_impl: true          # forbid tests whose only assertion is mock-call-count
    deterministic: true                     # no real clock/now(), no real network/DB, no unseeded randomness, no sleep
    fold_data_driven: true                  # fold BVA triple / EP classes / DT rows into one parameterised test
    exclusions: [generated-code, dto-data-class, trivial-accessor, framework-config, logicless-migration, pure-presentational-ui]
  property_based:
    enabled: true
    property_required: [parser, serializer, encoder, decoder, validator, state-reducer, non-trivial-algorithm]  # MUST ship >=1 property test
    property_or_examples: [small-business-rule, simple-mapping, simple-transform]   # property OR explicit examples covering invariant/boundary
    invariant_must_be_real: true            # reject tautological properties; require round-trip/idempotency/monotonicity/conservation
    max_examples: 200
    ci_seed: fixed
  mutation_testing:                         # OPTIONAL — not a gate. PRISM suggests it (with ETA); never auto-runs.
    mode: suggest-only                      # framework only suggests; runs on explicit user request, then writes report to the Implement output folder
    suggested_min_score: 80                 # advisory target WHEN run (not enforced, not blocking)
    triage_required: true                   # WHEN run: surviving mutant should be killed by a new test OR marked equivalent with a reason

  # code_thresholds — optional override for the size / complexity thresholds in coding-standards-*.md §Code Quality Thresholds.
  # When omitted, the defaults in each language's standards file apply (CODE-6 / CODE-7).
  # code_thresholds:
  #   backend:
  #     function_lines_warn: 80
  #     function_lines_blocker: 120
  #     file_lines_warn: 500
  #     file_lines_blocker: 800
  #     cyclomatic_warn: 10
  #     cyclomatic_blocker: 15
  #     parameter_count_warn: 5
  #     parameter_count_blocker: 7
  #     nesting_depth_warn: 3
  #   frontend:
  #     component_lines_warn: 150
  #     component_lines_blocker: 250
  #     hook_lines_warn: 60
  #     hook_lines_blocker: 100
  #     file_lines_warn: 400
  #     file_lines_blocker: 600
  #     prop_count_warn: 7
  #     prop_count_blocker: 10
  #     use_effect_per_component_warn: 3
  #   ai:
  #     prompt_template_chars_warn: 4000

# Guided open change packs are discovered by scanning docs/sprint-v*/changes/*/change-request.md with status: DRAFT
```
