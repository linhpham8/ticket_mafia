# PRISM Standards Index

This folder hosts all enforced standards. PRISM phase prompts MUST read this INDEX first, then load the specific files (relative to this folder) per the rules below.

Path to this folder is resolved through `prism.json` → `paths.standards` (default `.prism/core/standards`). Every filename below is relative to that resolved folder.

## Load rules

| Standard | Filename | Always load | Conditional load (load only when scope matches) |
|---------|----------|-------------|--------------------------------------------------|
| Architecture principles | `architecture-principles.md` | ✅ | — |
| Architecture solution | `architecture-solution-standards.md` | ✅ | — |
| Security | `security-standards.md` | ✅ | — |
| DevSecOps | `devsecops-standards.md` | ✅ | — |
| Coding backend | `coding-standards-backend.md` | — | Task slice touches backend / server / API / DB / job / migration / service code |
| Coding frontend | `coding-standards-frontend.md` | — | Task slice touches web / mobile (native, hybrid, web) / UI / PWA code |
| Coding AI | `coding-standards-ai.md` | — | Task slice touches AI / ML / agentic / LLM components |
| Testing | `testing-standards.md` | — | Phase Test is active, or a task explicitly audits QA test intent / test artifacts |
| Unit + Integration test | `unit-test-standards.md` | — | Phase Implement ships a repo test delta (unit / integration tests), or Plan sizes `repo_test_delta_target` |
| IoT | `iot-standards.md` | — | Project includes IoT / device / edge components (confirmed by user) |

## Discovery flow (every phase that loads standards)

1. Read `prism.json` at project root. Resolve `paths.standards`. If `prism.json` or `paths.standards` is missing, fall back to `.prism/core/standards`.
2. Read `<resolved>/INDEX.md` (this file). If missing, halt and instruct the user to run `setup.sh` or check `prism.json`.
3. Load every file marked "Always load".
4. Decide which conditional files apply based on the actual task slice scope; load only those.
5. Never load **PRISM project standards** (security, compliance, architecture, naming, design tokens, observability, etc.) from the web, training data, or other folders. The catalog above is the only source for project standards.

   **Narrow exception — framework idioms:** general framework idioms (how to use Spring Boot, React, Flutter, Anthropic SDK, etc. correctly) are public ecosystem knowledge, NOT PRISM project standards. The AI may apply framework idioms from its training knowledge and may consult official framework documentation when uncertain. The coding standards files (`coding-standards-backend.md §8`, `coding-standards-frontend.md §11`, `coding-standards-ai.md §9`) carry only a short note pointing at this rule; they do NOT enumerate idioms.

## Maintenance

When a new standard file is added or renamed in this folder, update this INDEX in the same change. Phase prompts resolve through INDEX, not through hardcoded filenames.
