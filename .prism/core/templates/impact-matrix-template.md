# Impact Matrix — v{{SPRINT}}.{{PACK}}

## 1. Overview

- Source phase: {{SOURCE_PHASE}}
- Earliest affected phase: {{EARLIEST_PHASE}}
- Current downstream phase(s): {{CURRENT_DOWNSTREAM_PHASES}}

## 2. Phase Impact

| Phase | Status in current sprint | Impacted? | Action now | Stop / continue |
|---|---|---|---|---|
| Product | {{PRODUCT_STATUS}} | {{PRODUCT_IMPACT}} | {{PRODUCT_ACTION}} | {{PRODUCT_FLOW}} |
| Design | {{DESIGN_STATUS}} | {{DESIGN_IMPACT}} | {{DESIGN_ACTION}} | {{DESIGN_FLOW}} |
| Architecture | {{ARCH_STATUS}} | {{ARCH_IMPACT}} | {{ARCH_ACTION}} | {{ARCH_FLOW}} |
| Plan | {{PLAN_STATUS}} | {{PLAN_IMPACT}} | {{PLAN_ACTION}} | {{PLAN_FLOW}} |
| Test | {{TEST_STATUS}} | {{TEST_IMPACT}} | {{TEST_ACTION}} | {{TEST_FLOW}} |
| Implement | {{IMPLEMENT_STATUS}} | {{IMPLEMENT_IMPACT}} | {{IMPLEMENT_ACTION}} | {{IMPLEMENT_FLOW}} |

## 3. Generated Artifacts

{{GENERATED_ARTIFACTS}}

## 4. Current Blockers

{{CURRENT_BLOCKERS}}

## 5. Approval Rule

`approve changes` is allowed only when all generated artifacts above are complete, the current downstream phase(s) have absorbed the change, and `validate changes [pack-id|slug]` has produced fresh clean pack-cycle validate files.

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ORB-2`
- [ ] Every impacted phase has clear action now and stop / continue decision
- [ ] Generated artifacts link concrete delta files or section IDs
- [ ] Current blockers state dependency, downstream impact, and validation signal
