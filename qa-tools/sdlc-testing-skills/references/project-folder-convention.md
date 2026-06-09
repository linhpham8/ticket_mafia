# Project Folder Convention

Mỗi skill có mục "Lưu file vào:" chỉ rõ output path. Nếu project có `output_paths` trong `qa-config.yaml` thì dùng path đó thay default.

## Output root (khuyến nghị bắt buộc)

Toàn bộ output testing phải nằm dưới 1 thư mục gốc duy nhất:
- `testing-output/`

Cấu trúc mặc định:
- `testing-output/test-plan/`
- `testing-output/test-cases/hltc/`
- `testing-output/test-cases/functional/`
- `testing-output/test-cases/sit/`
- `testing-output/test-data/`
- `testing-output/automation/`
- `testing-output/demo/`
- `testing-output/reports/` (daily/sprint/html/security/performance/accessibility)

## Naming convention

- `{Project}` = `project.code` từ qa-config (VD: `EW`, `PROJ`)
- `{Sprint}` = `project.sprint` từ qa-config (VD: `Sprint-12`)
- `{module}` = tên module viết thường, dấu gạch ngang (VD: `checkout`, `user-profile`)
- `{run-id}` = Run ID từ Skill 07 (VD: `15-04-2024-R1`)

## Global artifact traceability (bắt buộc)

Mọi artifact được tạo theo từng lần chạy hoặc từng lần sinh dữ liệu phải có đủ 3 thành phần:
- **Version** của artifact (SemVer dạng `v{major.minor.patch}`)
- **Timestamp** thời điểm tạo (`{yyyy-mm-dd}_{HHmm}`)
- **Result status** của lần tạo/chạy (`SUCCESS|PARTIAL|FAILED|BLOCKED`)

Không ghi đè file cũ theo kiểu "latest". Mỗi lần chạy phải tạo bản ghi mới để truy vết được lịch sử.

## File naming chuẩn theo loại artifact

- High-level test design (Markdown outline, Mermaid optional): `hltc-{module}-{sprint}-v{semver}-{yyyy-mm-dd}_{HHmm}.md` → lưu vào `testing-output/test-cases/hltc/`
- Functional TC: `tc-functional-{module}-{sprint}-v{semver}-{yyyy-mm-dd}_{HHmm}.tsv` → lưu vào `testing-output/test-cases/functional/`
- SIT TC: `tc-sit-{module}-{sprint}-v{semver}-{yyyy-mm-dd}_{HHmm}.tsv` → lưu vào `testing-output/test-cases/sit/`
- Test data master: `master-dataset-{sprint}-v{semver}-{yyyy-mm-dd}_{HHmm}.tsv`
- Data teardown script: `teardown-{sprint}-v{semver}-{yyyy-mm-dd}_{HHmm}.sql`
- Automation script pack: `automation-pack-{module}-{sprint}-v{semver}-{yyyy-mm-dd}_{HHmm}.zip` (hoặc thư mục cùng tên)
- Daily report: `daily-report-{yyyy-mm-dd}_{HHmm}-R{N}-v{semver}.md|html`
- Sprint report: `sprint-report-{sprint}-{yyyy-mm-dd}_{HHmm}-v{semver}.md|html`

## Result manifest bắt buộc cho mỗi lần tạo/chạy

Mỗi lần tạo artifact hoặc chạy test phải đi kèm 1 file manifest kết quả trong cùng nhóm output.

### 1) Data generation manifest

Tên file:
- `data-generation-result-{yyyy-mm-dd}_{HHmm}-R{N}.yaml`

Schema tối thiểu:
```yaml
run_id: <dd/mm/yyyy-RN>
artifact_type: test_data_generation
artifact_version: v<major.minor.patch>
timestamp: <yyyy-mm-dd_HHmm>
result: <SUCCESS|PARTIAL|FAILED|BLOCKED>
source_inputs:
	- <tc-file-path>
output_files:
	- <testing-output/test-data/master-dataset-...>
	- <testing-output/test-data/teardown-...>
summary:
	total_tc: <N>
	covered_tc: <N>
	uncovered_tc: <N>
notes: <optional>
```

### 2) Test run manifest

Tên file:
- `run-result-{yyyy-mm-dd}_{HHmm}-R{N}.yaml`

Schema tối thiểu:
```yaml
run_id: <dd/mm/yyyy-RN>
run_type: <Full|Re-run|Smoke>
artifact_version: v<major.minor.patch>
timestamp: <yyyy-mm-dd_HHmm>
result: <SUCCESS|PARTIAL|FAILED|BLOCKED>
metrics:
	pass: <N>
	fail: <N>
	blocked: <N>
	not_run: <N>
	pass_rate: <N>
bug_summary:
	s1_open: <N>
	s2_open: <N>
report_files:
	- <testing-output/reports/daily/daily-report-...>
```

Quy ước `result`:
- `SUCCESS`: đạt mục tiêu chính của lần chạy/tạo data, không blocker
- `PARTIAL`: có output nhưng còn thiếu/concern cần xử lý tiếp
- `FAILED`: chạy không hoàn thành do lỗi kỹ thuật/chất lượng
- `BLOCKED`: không thể thực hiện do dependency/môi trường/thiếu input

## Report convention (bắt buộc cho skill 09/10 (check-result / test-report))

- Dùng thư mục chung `output_paths.reports.root` (fallback: `testing-output/reports/`)
- Không dùng tên file chung chung kiểu `test-report.md`
- Tên file report phải có timestamp `{yyyy-mm-dd}_{HHmm}`
- Xuất tối thiểu 2 định dạng: Markdown + (HTML hoặc DOCX)
