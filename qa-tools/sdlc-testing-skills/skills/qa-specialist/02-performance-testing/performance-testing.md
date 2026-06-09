---
name: 02-performance-testing
description: >
  Lên kế hoạch và thực hiện performance testing: load test, stress test, spike test,
  soak test. Xác định baseline, cấu hình JMeter test plan, phân tích kết quả, phát
  hiện bottleneck. Trigger: performance test, load test, stress test, JMeter, tải,
  kiểm tra hiệu năng. Output: Performance Test Plan + kết quả so sánh baseline
  (JMeter mặc định; Artillery, Locust hỗ trợ thêm khi project đã chốt tool).
---

# Performance Testing

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/02-performance-testing.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L2`.

## Inputs

- Performance scope, workload model, SLA/baseline, target environment, tool choice, test data

## Core Workflow

1. Read SLA/baseline from qa-config or performance reference.
2. Define workload, scenarios, ramp-up, duration, metrics, and pass/fail thresholds.
3. Generate or review JMeter/k6/Locust plan according to chosen tool.
4. Analyze latency, throughput, error rate, saturation, and bottlenecks.
5. Emit L2 review request.

## Outputs

- Performance test plan/report and bottleneck analysis

## References

- references/performance-baseline.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
