# Detailed Procedure: 09-check-result

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

> ⚠️ **L2 — QA Lead review bắt buộc (SLA: 4h).** Không gửi output cho user cho đến khi nhận "Approved". Xem mục Sign-off cuối file.

- [ ] Daily report đủ: pass/fail/blocked, bug triage, health score đã tính
- [ ] Action items rõ ràng, có assignee cụ thể
- [ ] Sign-off request L2 đã emit, chờ QA Lead reply
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `sprint_progress`, `pending_sign_offs`

---

## Bước 0 — Đọc improvement log

Trước khi phân tích kết quả, đọc `feedback/improvement-log.md` để:
- Nắm `top_actions` từ sprint trước còn `pending` → ưu tiên theo dõi action đó hôm nay
- Nhận biết module nào đang có `delta_vs_prev` tăng → monitor kỹ hơn trong triage hôm nay
- Áp dụng lessons learned vào phân tích defect pattern và coverage delta

Nếu file chưa tồn tại → bỏ qua, bắt đầu từ zero.

---

## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| Kết quả TC (pass/fail/blocked, có thể dạng text/TSV/paste) | ✅ |
| Danh sách bug mới phát hiện (nếu có) | Khuyến nghị |
| Sprint Snapshot ngày hôm qua (dán từ block `Sprint Snapshot` cuối Daily Report ngày trước) | Khuyến nghị |
| Loại run: `Full` / `Re-run` / `Smoke` (mặc định `Full` nếu không nói rõ) | Khuyến nghị |
| Số thứ tự run trong ngày — nếu chạy nhiều lần cùng ngày (mặc định `1`) | Khuyến nghị |
| Test plan gốc (để so sánh tiến độ) | Khuyến nghị |
| Ngày hiện tại và ngày kết thúc sprint | Khuyến nghị |

> **Cách dùng Sprint Snapshot:**
> - Ngày đầu tiên: không có snapshot → bắt đầu từ zero.
> - Các ngày tiếp theo: paste block `### Sprint Snapshot` từ Daily Report hôm qua vào đây → Skill 07 tự merge và cập nhật tích lũy.
> - Cuối sprint: paste block `### Sprint Snapshot` ngày cuối vào Skill 08 — đã đủ toàn bộ dữ liệu, không cần aggregate thủ công.
> - Phần machine-readable bắt buộc cho auto-merge là block YAML `improvement_snapshot`; nếu chỉ có bảng Markdown, vẫn chạy fallback manual và đánh dấu `DONE_WITH_CONCERNS`.

Nếu project có `qa-config.yaml` → đọc trước khi phân tích:
- `exit_criteria.*` → ngưỡng pass rate, health score, max S1/S2 open để so sánh
- `suspension_criteria.*` → ngưỡng blocked_tc_rate và env_down_hours để đánh giá có nên suspend không
- `tools.communication` → kênh escalate khi có blocker
- `scope.modules` → dùng làm key chuẩn `module` cho defect pattern và coverage delta

## Phân tích thực hiện

### 1. Tổng hợp số liệu

Nếu có Sprint Snapshot ngày hôm qua → lấy danh sách TC và trạng thái từ snapshot làm base, cập nhật trạng thái mới nhất của các TC chạy hôm nay.
Nếu không có → bắt đầu từ zero.

> **Quy tắc tích lũy TC:** Mỗi TC chỉ đếm **một lần** theo **trạng thái mới nhất**. Nếu TC-001 là Fail hôm qua và Pass hôm nay → tính là Pass, không cộng thêm Fail cũ. Tổng = số lượng TC unique theo trạng thái hiện tại.

- Tổng TC tích lũy: pass / fail / blocked / not run (trạng thái mới nhất của mỗi TC, không cộng dồn số lần chạy)
- Pass rate = pass / (pass + fail) × 100%
- Block rate = blocked / total × 100%
- Tiến độ so với plan: đã chạy / tổng TC cần chạy

### 2. Triage bug
Đọc `../../references/bug-severity.md` để áp dụng phân loại đúng.
Với mỗi bug mới hôm nay: gán Severity (S1–S4) + Priority (P1–P4) + Category + đề xuất action.
Nếu có Sprint Snapshot ngày hôm qua → giữ nguyên danh sách bug cũ, thêm bug mới hôm nay vào danh sách tích lũy.

**Bảng triage chuẩn:**

| Bug ID | Mô tả ngắn | Severity | Priority | Category | Assigned | Action |
|---|---|---|---|---|---|---|
| BUG-001 | {mô tả} | S1/S2/S3/S4 | P1/P2/P3/P4 | Functional/Visual/UX/Content/Performance/Console/Accessibility | {Dev} | Fix ngay / Fix sprint / Backlog |

### 2.5 Phân loại bug theo Category (7 loại)
Đọc `../../references/bug-severity.md` mục "7 Category Phân loại Defect".
Gán đúng 1 trong 7 category cho mỗi bug: Visual, Functional, UX, Content, Performance, Console, Accessibility.

Tổng hợp phân bổ theo category để nhận diện khu vực có nhiều vấn đề nhất.

### 2.6 Defect Pattern theo module (cho handoff sprint)
- Dùng key `module` từ `scope.modules` trong `qa-config.yaml`.
- Tổng hợp theo `module + category` để tạo bảng pattern chuẩn.
- Nếu chưa có baseline sprint trước thì điền `so sprint trước = —` và `tín hiệu = —`.

**Bảng Defect Pattern by Module:**

| module | category | count | so sprint trước | tín hiệu |
|---|---|---|---|---|
| {module} | {Functional/Visual/UX/Console/Performance/Accessibility/Content} | {N} | {+N / -N / —} | {tăng/giảm/mới/ổn định/—} |

### 3. Tính Health Score
Đọc `../../references/report-template.md` để lấy công thức, trọng số 8 hạng mục và quy tắc trừ điểm theo severity.

> **Quy tắc hạng mục Links:** Nếu không test link checking trong sprint → điền điểm Links = 100 (không trừ điểm).

So sánh kết quả với `exit_criteria.health_score_baseline` trong `qa-config.yaml` (hoặc Exit Criteria trong Test Plan nếu chưa có config).

### 4. Xác định blocker và rủi ro
- Bug P1 nào đang block execution tiếp theo?
- Nhóm TC nào bị blocked do môi trường / data / dependency?
- Health Score hiện tại so với exit criteria — có nguy cơ không đạt không?
- Có cần suspend testing theo `suspension_criteria.*` trong `qa-config.yaml` không?

### 5. Retest scope
Liệt kê TC cần retest sau khi fix, ưu tiên theo P1 → P2 → P3.

### 6. Coverage Delta theo module (cho handoff sprint)
- Dùng cùng key `module` để join với Defect Pattern.
- `automated` chỉ tính script được execute trong sprint này.
- Không tính script chỉ tồn tại trong repo nhưng chưa chạy.

**Bảng Coverage Delta by Module:**

| module | planned TC | executed | automated (*) | gap |
|---|---|---|---|---|
| {module} | {N} | {N} | {N / —} | {executed - automated / —} |

`(*) automated = script được execute trong sprint này; không tính script tồn tại trong repo nhưng không chạy trong sprint`

## Format output — Daily Report

**Thư mục report chung (bắt buộc):**
- Ưu tiên dùng `output_paths.reports.root` từ `qa-config.yaml`
- Nếu chưa có config hoặc chưa khai báo `root` → dùng mặc định `reports/`

**Lưu file theo định dạng:**
- Markdown: `output_paths.reports.daily` (default: `testing-output/reports/daily/`)
- HTML: `output_paths.reports.html` (default: `testing-output/reports/html/`)
- Cần .docx → dùng `tools/md_to_docx.py` sau khi có file .md

**Quy tắc tên file:**
- `daily-report-{yyyy-mm-dd}_{HHmm}-R{N}-v{semver}.md`
- `daily-report-{yyyy-mm-dd}_{HHmm}-R{N}-v{semver}.html`

**Run result manifest (bắt buộc cho mỗi lần chạy):**
- Lưu thêm file: `run-result-{yyyy-mm-dd}_{HHmm}-R{N}.yaml` tại `output_paths.reports.daily` (default: `testing-output/reports/daily/`)
- Nội dung tối thiểu: `run_id`, `run_type`, `artifact_version`, `timestamp`, `result`, `metrics`, `bug_summary`, `report_files`
- `result` dùng 1 trong 4 giá trị chuẩn: `SUCCESS|PARTIAL|FAILED|BLOCKED`

Run ID được tạo tự động theo quy tắc: `{dd/mm/yyyy}-R{N}` trong đó N là số thứ tự run trong ngày (R1, R2...).
Ví dụ: ngày 15/04, run đầu tiên → `15/04/2024-R1`; re-run sau fix → `15/04/2024-R2`.

```markdown
## Daily Test Report — [dd/mm/yyyy] | Run [dd/mm/yyyy]-R[N]

**Sprint:** [Tên sprint] | **Ngày:** [X/Y ngày sprint]
**Loại run:** Full / Re-run (sau fix [BUG-ID]) / Smoke | **Thời điểm:** [HH:mm]
**Scope run này:** [Tất cả TC / Chỉ retest: TC-XXX, TC-YYY / Smoke suite]

### Tiến độ run này
| Trạng thái | Số TC | % |
|---|---:|---:|
| Pass | [n] | [x]% |
| Fail | [n] | [x]% |
| Blocked | [n] | [x]% |
| Not Run | [n] | [x]% |
| **Total trong scope run** | **[n]** | |

**Pass rate run này:** [x]% | **Mục tiêu exit criteria:** [x]%
**Health Score run này:** [N]/100 (Functional: [N] | Console: [N] | UX: [N] | Visual: [N])

### Bug mới trong run này
| Bug ID | Mô tả | Severity | Priority | Category | Assigned | Run ID |
|---|---|---|---|---|---|---|

### Phân bổ bug theo Category
| Category | Tổng | Open | Fixed |
|---|---:|---:|---:|
| Functional | | | |
| Visual / UI | | | |
| UX | | | |
| Console / Errors | | | |
| Performance | | | |
| Accessibility | | | |
| Content | | | |

### Blocker cần xử lý ngay
[Danh sách nếu có — ghi rõ bug ID, tác động, người phụ trách]

### Kế hoạch ngày mai
[Retest scope + TC mới cần chạy — ưu tiên P1 trước]

### Rủi ro
[Ghi rõ nếu tiến độ chậm hơn plan hoặc Health Score dưới ngưỡng]

---

### Sprint Snapshot — Tích lũy đến [dd/mm/yyyy]-R[N]

> Block này dùng để handoff sang ngày tiếp theo (paste vào đầu Skill 07) hoặc sang Skill 08 cuối sprint.

**Run history:**
| Run ID | Loại | Thời điểm | Scope | Pass | Fail | Blocked |
|---|---|---|---|---:|---:|---:|
| [dd/mm]-R1 | Full | HH:mm | Tất cả TC | [n] | [n] | [n] |
| [dd/mm]-R2 | Re-run | HH:mm | TC-XXX, TC-YYY | [n] | [n] | [n] |

**TC tích lũy (trạng thái mới nhất của mỗi TC):**
| Trạng thái | Tổng tích lũy |
|---|---:|
| Pass | [n] |
| Fail | [n] |
| Blocked | [n] |
| Not Run | [n] |
| Total trong scope | [n] |

**Danh sách bug tích lũy (tất cả bug từ đầu sprint):**
| Bug ID | Mô tả ngắn | Severity | Priority | Category | Trạng thái | Run ID phát hiện |
|---|---|---|---|---|---|---|
| BUG-001 | ... | S? | P? | ... | Open/Fixed/Verified | [dd/mm]-R1 |

**Health Score tích lũy:** [N]/100
(Functional: [N] | Console: [N] | UX: [N] | Accessibility: [N] | Visual: [N] | Performance: [N] | Links: [N] | Content: [N])

**Defect Pattern by Module (snapshot):**
| module | category | count | so sprint trước | tín hiệu |
|---|---|---|---|---|
| [module] | [category] | [n] | [+/−/—] | [signal] |

**Coverage Delta by Module (snapshot):**
| module | planned TC | executed | automated (*) | gap |
|---|---:|---:|---:|---:|
| [module] | [n] | [n] | [n/—] | [n/—] |

`(*) automated = script được execute trong sprint này; không tính script tồn tại trong repo nhưng không chạy trong sprint`

### improvement_snapshot (machine-readable)

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
```

Schema tối thiểu bắt buộc cho block này: `sprint`, `date`, `modules[]`, `top_actions[]`.

## Khi pass rate < exit criteria

Tự động cảnh báo và đề xuất một trong ba hành động:
1. Tăng tốc retest nếu nhiều bug đã được fix
2. Giảm scope P3 nếu thiếu thời gian
3. Escalate lên QC Lead / PM nếu P1 còn open

## Completion Status

Kết thúc mỗi ngày phân tích, báo cáo status:

- **DONE** — Đã phân tích đủ kết quả, daily report hoàn chỉnh, health score đã tính
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng: {Pass rate thấp hơn kỳ vọng / Health Score dưới ngưỡng / Có S1 còn open / Sprint Snapshot chỉ có Markdown, thiếu block YAML `improvement_snapshot` / Run result manifest ghi `PARTIAL`}
- **BLOCKED** — Không thể phân tích do: {Kết quả chưa đủ / Thiếu thông tin bug / Môi trường chưa ổn định}
- **NEEDS_CONTEXT** — Cần bổ sung: {Danh sách bug đầy đủ / Test plan để so sánh tiến độ / Ngày kết thúc sprint}



---

## Bước cuối — Tool Integration + Sign-off + Audit Log

### 1. Publish artifacts (sau khi report hoàn chỉnh)

Nếu project có Confluence config trong qa-config.yaml:
```bash
python tools/confluence_publish_markdown.py \
  --file "testing-output/reports/daily/daily-report-{date}-R{N}.md" \
  --parent-page "{confluence.parent_pages.reports}"
```

Nếu project có Jira config → cập nhật trạng thái sprint:
```bash
python tools/jira_sync.py --action comment \
  --issue "{sprint_ticket_id}" \
  --comment "Daily report {date}: Pass {N}%, Health {N}/100. Xem chi tiết: [Confluence link]"
```

**Chỉ thực hiện tool integration khi:** QA Lead đã confirm hoặc user chủ động yêu cầu push.

### 2. Sign-off Request (L2)

```
---
⏳ SIGN-OFF REQUEST — 09-check-result (Level 2 — QA Lead)
Người review: [team.qc_lead từ qa-config]
SLA: 4 giờ
Output: testing-output/reports/daily/daily-report-{date}-R{N}.md
Action: Reply "Approved" hoặc "Cần điều chỉnh: [nội dung]"
---
```

### 3. Audit Log

Append vào `governance/audit-log.md`:
```yaml
execution_record:
  id: "{yyyy-mm-dd}-{HHmm}-09-check"
  timestamp: "{yyyy-mm-ddTHH:mm}"
  skill: "09-check-result"
  project: "{project.name}"
  sprint: "{project.sprint}"
  executor: "{executor}"
  input_summary: "Run {run_id}: Pass {N}, Fail {N}, Blocked {N}, {N} bug mới"
  output_paths:
    - "testing-output/reports/daily/daily-report-{date}-R{N}.md"
    - "testing-output/reports/daily/run-result-{date}-R{N}.yaml"
  status: "DONE | DONE_WITH_CONCERNS | BLOCKED"
  requires_human_review: true
  reviewer: null
  reviewed_at: null
  sign_off_status: "PENDING"
```