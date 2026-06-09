---
name: 08-gen-data-test
description: >
  Tạo bộ dữ liệu kiểm thử chi tiết từ danh sách test case: BVA boundary values,
  EP partitions, synthetic PII-safe data, dataset cho Data-Driven TC, teardown script.
  Trigger: data test, dữ liệu kiểm thử, tạo data, test data, chuẩn bị dữ liệu test.
  Output: TSV Master dataset + TC Coverage Map + Data-Driven table + SQL/script teardown.
---

# Generate Test Data

Compact workflow. Read the detailed procedure only when exact legacy wording or edge cases are needed:
`references/skill-details/08-gen-data-test.md`.

## Read First

- Read `project/qa-config.yaml` only if it exists and the task needs project config.
- Use `references/INDEX.md` to choose optional references; do not open all references.
- Apply `governance/GOVERNANCE.md` before finalizing or publishing.
- Governance gate: `L1`.

## Inputs

- Approved TC files, data rules, environment constraints, reset/teardown constraints

## Core Workflow

1. Identify data classes from TC preconditions and test data fields.
2. Generate valid, invalid, boundary, permission, stateful, and dependency data sets.
3. Mark sensitive values as placeholders or env references; do not include real secrets.
4. Add teardown or reset instructions where state changes matter.
5. Save under `output_paths.test_data` or default test-data folder.

## Format output — 2 lựa chọn

**Format A — Standard 6-column** (mặc định, dùng cho BVA/EP với nhiều biến thể):
```
TC_ID	Dataset_ID	Test_Data	Loại	Teardown	Ghi chú
```
- `Test_Data`: tất cả field=value trên 1 dòng, phân cách bằng `; `
- `Loại`: `BVA-min` / `EP-valid` / `EP-invalid` / `Normal` / `Corner`
- 1 TC có thể có nhiều dòng nếu cần nhiều biến thể (BVA sub-values, EP partitions)

**Format B — Flat all-in-one** (dùng khi mỗi TC có 1 bộ data duy nhất, hoặc khi file TSV là nguồn duy nhất để chạy automation):
- 1 dòng / TC, tất cả fields là cột riêng (không có Dataset_ID)
- Payload phức tạp (JSON, container image, API payload) inline trong cột tương ứng
- Ưu tiên khi: TC là happy path, không cần biến thể BVA/EP, và team dùng TSV để review thay vì YAML

Ví dụ header Format B:
```
TC_ID	TC_Summary	Role	Account_Email	Entity_ID	Workspace_ID	Stage_ID	Agent_Name	Agent_Type	Agent_Version	Container_Image	Flow_JSON	Expected_HTTP	Expected_Status	Teardown	Ghi_chu
```

**Khi nào dùng format nào:**
| Tình huống | Format |
|---|---|
| TC có nhiều biến thể BVA/EP | A (6 cột) |
| Happy path, 1 bộ data / TC | B (flat) |
| Team dùng YAML cho RF, TSV chỉ để review | B (flat, export YAML khi cần) |
| Cần import vào QMetry hoặc Google Sheet | A (6 cột) |

## Outputs

- Master test data file (Format A hoặc B tùy tình huống)
- Optional teardown/cleanup notes or scripts

## References

- references/project-folder-convention.md

## Stop Conditions

- Required input is missing and cannot be inferred from provided artifacts.
- The task requires external publishing but the required governance approval is not present.
- The requested action is outside the skill scope selected by `SKILL.md`.
