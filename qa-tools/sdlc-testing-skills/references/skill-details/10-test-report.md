# Detailed Procedure: 10-test-report

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

> ⚠️ **L2 — QA Lead review bắt buộc (SLA: 8h).** Không gửi output cho user cho đến khi nhận "Approved". Xem mục Sign-off cuối file.

- [ ] Đủ mục theo report-template.md
- [ ] Health Score đã tính đúng công thức, ghi rõ breakdown từng hạng mục
- [ ] Ship Readiness so sánh với `exit_criteria` từ `qa-config.yaml`
- [ ] Không còn placeholder `{...}` trong nội dung chính
- [ ] Sign-off request L2 đã emit, chờ QA Lead reply
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `sprint_progress`, `pending_sign_offs`

---

## Bước 0 — Đọc improvement log

Trước khi tổng hợp report, đọc `feedback/improvement-log.md` để:
- So sánh `defect_pattern` sprint này với sprint trước (cột `so sprint trước`)
- Kiểm tra `top_actions` sprint trước có `status: done` chưa → ghi nhận vào Structured Lessons Learned
- Xác định module nào đang có trend tích cực / tiêu cực để highlight trong Ship Readiness

Nếu file chưa tồn tại → ghi `delta_vs_prev = NA` cho tất cả module.
Sau khi hoàn thành report, **append block `improvement_snapshot` mới** vào `feedback/improvement-log.md`..

---

## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| Sprint Snapshot từ Daily Report ngày cuối sprint (block `Sprint Snapshot` của Skill 07) | ✅ (ưu tiên) |
| Kết quả TC tổng hợp (pass/fail/blocked/not run) — nếu không có Sprint Snapshot | ✅ (fallback) |
| Danh sách bug đầy đủ (ID, mô tả, severity, priority, trạng thái) — nếu không có Sprint Snapshot | ✅ (fallback) |
| Test Plan gốc (để lấy scope nếu chưa có config) | Khuyến nghị |
| Tên sprint, ngày bắt đầu / kết thúc | ✅ |

> **Ưu tiên dùng Sprint Snapshot:** Block `Sprint Snapshot` từ Skill 07 đã tích lũy đủ TC counts + danh sách bug tất cả ngày → paste trực tiếp, không cần aggregate thủ công.
> Nếu không có Sprint Snapshot (ví dụ không dùng Skill 07 trong sprint) → cung cấp fallback: kết quả TC tổng hợp + danh sách bug đầy đủ.

Nếu project có `qa-config.yaml` → đọc trước, ưu tiên hơn Test Plan:
- `exit_criteria.*` → pass_rate, health_score_baseline, max_s1_open, max_s2_open, tc_executed_rate
- `suspension_criteria.*` → để đánh giá nếu đã có suspend trong sprint
- `team.*` → tên người thực hiện trong report header
- `definition_of_done` → dùng để đánh giá sprint có đạt DoD chưa
- `tools.communication` → kênh gửi report

Quy tắc precedence khi ngưỡng bị xung đột:
- Nếu `qa-config.yaml` và Test Plan khác nhau, dùng `qa-config.yaml` làm nguồn chính.
- Trong report phải ghi rõ nguồn ngưỡng đã dùng: `qa-config` hoặc `test-plan-fallback`.

Thiếu thông tin bắt buộc → ghi `[Cần bổ sung]`, hỏi lại. Không đoán mò.

---

## Bước 1 — Aggregate số liệu từ toàn sprint

**Nếu có Sprint Snapshot (từ Skill 07 ngày cuối):**
- Lấy trực tiếp TC tích lũy và danh sách bug từ block `Sprint Snapshot` — đã đủ, không cần tính lại.
- Chuyển thẳng sang Bước 2.

**Nếu không có Sprint Snapshot (fallback):**
- Tổng TC theo trạng thái: pass / fail / blocked / not run
- Pass rate = pass / (pass + fail) × 100%
- Tổng bug: theo severity (S1/S2/S3/S4) và trạng thái (open/fixed/verified/deferred)

So sánh với Exit Criteria từ `qa-config.yaml` (nếu có) hoặc Test Plan (fallback).

---

## Bước 2 — Tính Health Score

Đọc `../../references/report-template.md` để lấy công thức và trọng số.
Đọc `../../references/bug-severity.md` để phân loại bug theo 7 category.

**Công thức:**
- Mỗi hạng mục bắt đầu từ 100 điểm
- Trừ điểm theo severity: S1 = −25, S2 = −15, S3 = −8, S4 = −3
- Nhân với trọng số: Functional 20%, Console 15%, UX 15%, Accessibility 15%, Visual 10%, Performance 10%, Links 10%, Content 5% (tổng = 100%)
- Nếu sprint không test link checking → Links = 100 điểm (không trừ)
- Health Score = Tổng điểm có trọng số

Ghi nhận Health Score so với baseline đầu sprint (nếu có).

---

## Bước 3 — Phân tích xu hướng

Nếu Sprint Snapshot ghi rõ `Ngày phát hiện` cho từng bug → dùng để phân tích:
- Bug mới theo ngày: tập trung vào ngày nào? Module nào?
- Retest cycle: bug được fix (trạng thái Fixed/Verified) trong bao lâu sau khi phát hiện?
- Health Score theo ngày: nếu Skill 07 đã tính Health Score mỗi ngày → liệt kê trajectory.

Nếu không có dữ liệu theo ngày → bỏ qua phần này, ghi rõ "Không có daily data để phân tích xu hướng".

**Bảng A — Defect Pattern by Module:**

| module | category | count | so sprint trước | tín hiệu |
|---|---|---|---|---|
| {module} | {Functional/Visual/UX/Console/Performance/Accessibility/Content} | {N} | {+N / -N / —} | {tăng/giảm/mới/ổn định/—} |

- `module`: lấy từ `scope.modules` trong `qa-config.yaml` để dùng làm key join với Coverage Delta
- `so sprint trước`: nếu sprint đầu tiên hoặc chưa có dữ liệu baseline/qa-improvement-log thì ghi `—`, không để trống
- `tín hiệu`: suy từ delta theo module-category; thiếu dữ liệu thì ghi `—`

**Bảng B — Coverage Delta by Module:**

| module | planned TC | executed | automated (*) | gap |
|---|---|---|---|---|
| {module} | {N} | {N} | {N / —} | {executed - automated / —} |

`(*) automated = script được execute trong sprint này; không tính script tồn tại trong repo nhưng không chạy trong sprint`

- Dùng cùng key `module` để join với Bảng A
- Nếu thiếu số liệu execution automation thì điền `—` cho `automated` và `gap`

---

## Bước 4 — Đánh giá Ship Readiness

So sánh với Exit Criteria từ `qa-config.yaml` (nếu có) hoặc Test Plan (fallback):

| Chỉ số | Mục tiêu (Exit Criteria) | Thực tế | Đạt? |
|---|---|---|---|
| Pass rate | ≥ {x}% | {x}% | ✅ / ❌ |
| Health Score | ≥ {N}/100 | {N}/100 | ✅ / ❌ |
| S1 còn open | = 0 | {N} | ✅ / ❌ |
| S2 còn open | ≤ {N} | {N} | ✅ / ❌ |
| TC chưa chạy | = 0 | {N} | ✅ / ❌ |
| Regression pass | = 100% | {x}% | ✅ / ❌ |

**Khuyến nghị ship:**
- ✅ **Sẵn sàng release** — Mọi exit criteria đạt
- ⚠️ **Release có điều kiện** — Đạt đủ điều kiện bắt buộc, còn {N} vấn đề minor cần theo dõi sau release
- ❌ **Chưa sẵn sàng** — {Lý do cụ thể: S1 còn open / Pass rate {x}% thấp hơn mục tiêu {y}%}

---

## Bước 5 — Xuất báo cáo

Đọc `../../references/report-template.md` để lấy format chuẩn đầy đủ.

Bổ sung so với template cơ bản:
- **Phần Xu hướng Sprint** (nếu có daily data): biểu đồ dạng bảng pass rate theo ngày
- **Structured Lessons Learned** (bắt buộc, machine-readable):

| # | Loại | Mô tả | Module/Skill nguồn | Action sprint sau |
|---|---|---|---|---|
| 1 | {TC Design / Automation / Process / Environment} | {quan sát cụ thể} | {module hoặc skill số} | {hành động có địa chỉ} |

Phân loại:
- **TC Design** — lỗ hổng coverage hoặc chất lượng thiết kế test case
- **Automation** — script chưa đủ hoặc chưa được execute trong sprint
- **Process** — vấn đề phối hợp, triage, handoff, hoặc cadence
- **Environment** — vấn đề môi trường, dữ liệu, hoặc hạ tầng chạy test

Định dạng xuất:
- Markdown: dùng trực tiếp trong conversation
- HTML: cùng nội dung với Markdown, giữ đúng section và bảng theo `report-template.md`
- Cần .docx → dùng `tools/md_to_docx.py` sau khi có file .md

**Thư mục report chung (bắt buộc):**
- Ưu tiên dùng `output_paths.reports.root` từ `qa-config.yaml`
- Nếu chưa có config hoặc chưa khai báo `root` → dùng mặc định `reports/`

**Lưu file theo định dạng:**
- Markdown: `output_paths.reports.sprint` (default: `testing-output/reports/sprint/`)
- HTML: `output_paths.reports.html` (default: `testing-output/reports/html/`)

**Quy tắc tên file:**
- `sprint-report-{project.sprint}-{yyyy-mm-dd}_{HHmm}-v{semver}.md`
- `sprint-report-{project.sprint}-{yyyy-mm-dd}_{HHmm}-v{semver}.html`

**Run/result traceability cho lần tổng hợp sprint:**
- Khuyến nghị xuất thêm `run-result-{yyyy-mm-dd}_{HHmm}-R{N}.yaml` (hoặc `sprint-result-{yyyy-mm-dd}_{HHmm}.yaml`) tại `output_paths.reports.sprint`
- Gồm các key: `artifact_version`, `timestamp`, `result`, `metrics`, `ship_readiness`, `report_files`

---

## Checklist trước khi xuất

- [ ] Đủ các mục trong report-template.md
- [ ] Health Score đã tính đúng công thức và ghi rõ breakdown từng hạng mục
- [ ] Bảng Ship Readiness đã so sánh với exit criteria từ `qa-config.yaml` hoặc Test Plan fallback
- [ ] Không còn placeholder `{...}` trong nội dung chính
- [ ] Khuyến nghị ship có lý do cụ thể, không chung chung
- [ ] Bảng Defect Pattern đủ 5 cột: module, category, count, so sprint trước, tín hiệu
- [ ] Bảng Coverage Delta dùng cùng key module; cột `automated` chỉ tính script được execute trong sprint
- [ ] Structured Lessons Learned có đủ 5 cột, action có địa chỉ cụ thể

---

## Đầu ra cho vòng cải tiến sprint sau

Sau khi xuất Sprint Report, trích xuất thêm một block chuẩn để dùng lại cho sprint kế tiếp (append vào `references/qa-improvement-log.md` của project):

```yaml
improvement_snapshot:
  sprint: {project.sprint}
  date: {yyyy-mm-dd}
  modules:
    - module: {module}
      defect_pattern:
        - category: {category}
          count: {N}
          delta_vs_prev: {+N|-N|0|NA}
      coverage_delta:
        planned_tc: {N}
        executed_tc: {N}
        automated_executed_tc: {N|NA}
        gap: {N|NA}
  top_actions:
    - type: {TC Design|Automation|Process|Environment}
      owner: {role/name}
      action: {specific action}
      due_in_sprint: {Sprint-X}
```

Nếu chưa có baseline sprint trước thì dùng `NA` cho delta.

---

## Sign-off Request (L2)

```
---
⏳ SIGN-OFF REQUEST — 10-test-report (Level 2 — QA Lead)
Người review: [team.qc_lead từ qa-config]
SLA: 8 giờ
Output: testing-output/reports/sprint/sprint-report-{sprint}-{date}.md
Action: Reply "Approved" hoặc "Cần chỉnh: [nội dung]"
---
```

Sau khi nhận Approved → cập nhật `project/session-state.yaml`: xóa item khỏi `pending_sign_offs`.

---

## Completion Status

- **DONE** — Báo cáo đầy đủ, health score tính xong, ship readiness rõ ràng
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng: {Còn S1 open / Pass rate thấp / Coverage chưa đủ}
- **BLOCKED** — Thiếu: {Danh sách bug đầy đủ / Exit criteria từ `qa-config.yaml` hoặc Test Plan / Kết quả TC}
- **NEEDS_CONTEXT** — Cần bổ sung: {Thông tin cụ thể}

