# Detailed Procedure: 03-sprint-test-plan

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

- [ ] Đủ 5 mục, Exit Criteria có pass_rate và health_score_baseline rõ ràng
- [ ] Không còn placeholder `{...}` trong nội dung chính
- [ ] `qa-config.yaml` đã đọc (hoặc đã nhắc user chạy skill 02 trước)
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `current_sprint`

---

## Nguyên tắc

Sprint Test Plan chỉ ghi những gì **thay đổi trong sprint này**. Chiến lược, test technique, KPI target, suspension criteria đã có trong Master Test Plan — **tham chiếu, không viết lại**.

## Đầu vào bắt buộc

| Thông tin | Bắt buộc |
|---|---|
| Tên sprint, ngày bắt đầu / kết thúc | ✅ |
| Danh sách ticket (key, summary) | ✅ |
| Người thực hiện QC và số ngày available | ✅ |

Thiếu → ghi `[Cần bổ sung]`, hỏi lại.

## Bước 0 — Đọc nguồn config

1. Đọc `qa-config.yaml` nếu có → `project.name`, `project.code`, `exit_criteria`, `environments`, `tools`
2. Đọc Master Test Plan nếu có → xác định risk rule, coverage target by flow để điền vào 1.2

---

## Sinh Sprint Test Plan — 5 mục

**Header:**

| | |
|---|---|
| **Tên dự án** | {project.name} |
| **Thời gian** | {dd/mm/yyyy} đến {dd/mm/yyyy} |
| **Phiên bản** | 1.0 |
| **Master Test Plan** | {link — chiến lược, KPI, kỹ thuật test xem tại đây} |

---

### 1. Tổng Quan Sprint

#### 1.1 Mục tiêu kiểm thử

Ghi ngắn gọn QC cần đạt gì trong sprint này:
- Ví dụ: "Test done tính năng Sprint 3, SIT full luồng chuyển tiền — 100% PASS"
- Ví dụ: "Regression pass = 100% trước khi cut release ngày {dd/mm}"

#### 1.2 Phạm vi kiểm thử

**Danh sách ticket:**

| Ticket | Summary | Risk | Ghi chú |
|---|---|---|---|
| {KEY-001} | {summary} | Cao / Trung / Thấp | |

> Risk Level theo Master Test Plan: Cao = luồng core/payment, Trung = tích hợp/tra soát, Thấp = truy vấn/UI.
> Coverage target theo risk xem Master Test Plan.
>
> Nhiều ticket → có thể thay bảng bằng Jira filter: `project = X AND sprint = Y`

#### 1.3 Lịch trình kiểm thử

| Thời gian | Công việc | Ghi chú |
|---|---|---|
| {dd/mm–dd/mm} | {Viết TC / Chuẩn bị data / Smoke / Functional / SIT / Regression} | |

#### 1.4 Các loại kiểm thử thực hiện

Chỉ liệt kê loại test **thực tế áp dụng trong sprint này**. Kỹ thuật và tool xem Master Test Plan.

| STT | Loại kiểm thử | Mục đích | Ghi chú |
|---|---|---|---|
| 1 | Functional Testing | Tính năng mới đáp ứng đúng yêu cầu User Story | |
| 2 | Integration / SIT | Kiểm tra tích hợp module/API/E2E | Chỉ điền nếu có SIT sprint này |
| 3 | Smoke Testing | Kiểm tra core flow trước khi test full | |
| 4 | Sanity / Retest | Fix bug đúng, không tạo bug mới | |
| 5 | Regression Testing | Thay đổi mới không làm hỏng chức năng cũ | |
| 6 | Performance | {scope cụ thể — endpoint/flow} | Metric: {p95 < Nms} — tool xem Master |
| 7 | Security | {module} | Tool xem Master Test Plan |
| 8 | UAT | Nghiệm thu với {stakeholder} | Nếu yêu cầu trong sprint này |

> Xóa dòng không áp dụng. Cột Ghi chú: ghi scope/metric nếu là NFT, ghi tên stakeholder nếu là UAT.

---

### 2. Công Cụ & Môi Trường Kiểm Thử

> Nếu không thay đổi so với Master Test Plan: "Theo Master Test Plan / qa-config.yaml — xem: {link}."
> Chỉ ghi phần thay đổi hoặc bổ sung trong sprint này.

#### 2.1 Công cụ kiểm thử

| Activities | Tools | Version | Ghi chú |
|---|---|---|---|
| Quản lý TC | QMetry / Google Sheet | | |
| API test / Automation | Postman + Robot Framework | | |
| Bug tracking | Jira | | |
| Performance (nếu có) | JMeter | | Scope sprint: {endpoint} |

#### 2.2 Môi trường kiểm thử

| Hệ thống | Môi trường | Link | Ghi chú |
|---|---|---|---|
| {service} | {QC / Staging / UAT} | {URL} | Deploy mới nhất: {ngày} |

---

### 3. Nguồn Lực Kiểm Thử

| Tên | Vai trò | Số ngày | Allocation | Ghi chú |
|---|---|---:|---:|---|
| {Tên} | QC Lead | {N} | 100% | |
| {Tên} | QC | {N} | {N}% | Nghỉ {N} ngày |
| **Tổng** | | **{N}** | | |

**Phân tích capacity:**

| | Giờ |
|---|---:|
| Tổng effort cần (estimate) | {N}h |
| Tổng giờ available ({N} ngày × 7h) | {N}h |
| **Chênh lệch** | **{+/−N}h** |

> Thiếu giờ → đề xuất phương án cụ thể: giảm scope P3 / OT / defer sang sprint sau.

**Estimate chi tiết:** {link Google Sheet / QMetry nếu có}

---

### 4. Điều Kiện Kết Thúc Kiểm Thử

**Entry Criteria** (điều kiện bắt đầu test — ghi nếu cần theo dõi trạng thái):

| Điều kiện | Xác nhận bởi | Trạng thái |
|---|---|---|
| Build deploy thành công lên {môi trường} | Dev Lead | Sẵn sàng / Chờ |
| TC đã viết và review xong | QC Lead | Sẵn sàng / Chờ |
| Test data sẵn sàng | QC | Sẵn sàng / Chờ |

**Exit Criteria — Test Completion** (QC quyết định):

Đọc `exit_criteria.*` từ `qa-config.yaml` (nếu có) làm nguồn chính. Ghi rõ nguồn: `qa-config` hoặc `master-test-plan-fallback`.

| Chỉ số | Nguồn field | Mục tiêu sprint này | Ghi chú |
|---|---|---|---|
| Pass rate | `exit_criteria.pass_rate` | ≥ {N}% | High-risk TC: 100% |
| TC Execution Rate | `exit_criteria.tc_executed_rate` | ≥ {N}% | |
| Health Score | `exit_criteria.health_score_baseline` | ≥ {N}/100 | Tính theo skill 09 (qa-core/09-check-result) |
| S1/Critical open | `exit_criteria.max_s1_open` | = 0 | Blocker cứng |
| S2/High open | `exit_criteria.max_s2_open` | ≤ {N} | Xác nhận bởi QC Lead + Dev |
| SIT pass rate | — | = 100% | Nếu có SIT sprint này |
| Regression pass | — | = 100% | |

> Nếu sprint không có điều chỉnh so với Master Test Plan: ghi "Theo `exit_criteria` trong qa-config.yaml — không thay đổi sprint này" và bỏ qua bảng trên.
> Nếu sprint có điều chỉnh (nới lỏng hoặc siết thêm): điền bảng đầy đủ và ghi lý do trong cột Ghi chú.

**Go-Live Decision** (PM/Product quyết định): Theo Master Test Plan.
**Suspension Criteria:** Theo Master Test Plan / `suspension_criteria.*` trong qa-config.yaml.

---

### 5. Tài Liệu Tham Khảo

| Tài liệu | Link |
|---|---|
| Master Test Plan (chiến lược, KPI, kỹ thuật) | {link Confluence} |
| Requirement / BRD / PRD | {link} |
| Jira Board | {link} |
| TC Sheet (QMetry / Google Sheet) | {link} |
| Test Data | {link nếu có} |

---

## Xuất file

**Naming:** `Sprint_Test_Plan_{project.code}_{sprint}_v{semver}_{yyyy-mm-dd}_{HHmm}.md`

**Lưu vào:** `output_paths.test_plan` từ qa-config (default: `testing-output/test-plan/`)

Sau khi xong, gợi ý:
- **skill 04 (qa-core/04-test-design-high-level)** cho module logic phức tạp → HLTC trước khi viết TC
- **skill 05 (qa-core/05-gen-tc-functional)** → gen functional TC
- **skill 08 (qa-core/08-gen-data-test)** → gen test data ngay sau khi có TC
