---
name: 07-review-tc
description: >
  Review và đánh giá chất lượng test case có sẵn: phân tích coverage 12 nhóm, rule inventory đầy đủ,
  phát hiện lỗ hổng, đề xuất TC bổ sung đúng format. Gating skill — chỉ approve khi coverage đủ.
  Trigger: review testcase có sẵn, đánh giá TC từ sprint trước, TC viết thủ công, TC nhận từ team khác,
  coverage analysis file TC hiện có, gap analysis testcase đã có.
  Output: Coverage Map + Gap Analysis + Supplemental TC + Review Gate verdict.
  Sign-off: Level 2 — QA Lead review required.
---

# Review Existing Testcases

> **BẮT BUỘC**: Đọc toàn bộ skill này TRƯỚC khi bắt đầu. Không bỏ qua bước nào.

## Đọc trước khi bắt đầu

- Đọc `project/qa-config.yaml` nếu tồn tại.
- Đọc `governance/GOVERNANCE.md` trước khi finalize.
- Governance gate: `L2` — QA Lead review bắt buộc (SLA: 24h). Không send output cho user cho đến khi nhận "Approved".

## Inputs

- Tài liệu yêu cầu (US/AC/BR, mỗi yêu cầu có ID riêng) — **bắt buộc**
- File TC hiện có (TSV, Excel, hoặc Markdown; Functional hoặc SIT) — **bắt buộc**
- `qa-config.yaml` (nếu có → đọc `scope.modules` để group coverage theo module)

Nếu thiếu tài liệu yêu cầu hoặc file TC → ghi `[Cần bổ sung]`, liệt kê câu hỏi làm rõ, dừng lại.

## Workflow bắt buộc (theo thứ tự)

### Bước 1 — Xây dựng Rule Inventory

Trước khi review TC, tạo Rule Inventory từ tài liệu yêu cầu:

1. Đọc toàn bộ AC/US/BR.
2. Gán ID cho mỗi rule/AC/BR nếu chưa có (AC-01, AC-02, BR-01...).
3. Tạo danh sách inventory:

| Rule ID | Mô tả ngắn | Loại | Độ phức tạp | Module |
|---|---|---|---|---|
| AC-01 | [Mô tả rule] | AC / BR / US | Cao / Trung bình / Thấp | [module nếu có] |

**Không bỏ sót rule nào** — mọi requirement phải có trong inventory.

### Bước 2 — Phân tích coverage theo 12 nhóm

Với mỗi Rule ID, kiểm tra file TC hiện tại đã cover nhóm nào trong 12 nhóm sau:

| # | Nhóm | Bắt buộc? |
|---|---|---|
| 1 | Happy path — Luồng chính hoạt động đúng với data hợp lệ | Mọi AC |
| 2 | Negative / Invalid input — Data sai, thiếu, sai định dạng | AC có input |
| 3 | Boundary Value — Giá trị biên (min, max, min-1, max+1) | AC có giá trị số |
| 4 | Authorization — Phân quyền đúng role, block sai role | AC liên quan auth |
| 5 | Error handling — Lỗi hệ thống, timeout, network error | AC có external call |
| 6 | State transition — Thay đổi trạng thái đúng sequence | AC có workflow |
| 7 | Regression — Tính năng cũ không bị ảnh hưởng | AC thay đổi core |
| 8 | Performance — Response time, tải lớn | AC có SLA |
| 9 | Data integrity — Data lưu/xử lý đúng, không mất/corrupt | AC có data persistence |
| 10 | UI / UX — Hiển thị đúng, responsive, a11y cơ bản | AC có giao diện |
| 11 | Integration / API — Contract giữa service, response schema | AC có API call |
| 12 | Edge case / Exploratory — Scenario hiếm gặp, kết hợp điều kiện đặc biệt | Tùy độ phức tạp |

### Bước 3 — Tạo Coverage Map (Bảng 1)

Mỗi dòng = 1 Rule ID/AC/BR từ tài liệu yêu cầu.
Header 15 cột chuẩn (đồng bộ `references/tc-template.tsv`) + 4 cột bổ sung:

```
STT	Summary	Test Level	Precondition	Test Data	Step summary	Expected result	Priority	Story Linkages	Test Type	Smoke	Auto	Phụ thuộc TC	Teardown	Trace	Rule ID	Nhóm cover	Nhóm còn thiếu	Coverage score
```

Coverage score: `Full` (≥8/12 nhóm áp dụng) / `Partial` (4–7) / `Minimal` (<4)

### Bước 4 — Kiểm tra chất lượng TC hiện tại

Với từng TC trong file gốc, kiểm tra theo các tiêu chí:

| Tiêu chí | Flag nếu fail |
|---|---|
| Summary ≥ 10 ký tự, mô tả rõ action + object | TC-XXX: Summary quá ngắn |
| Expected result cụ thể, không chứa "hoạt động đúng" / "thành công" vô nghĩa | TC-XXX: Expected result mơ hồ |
| Trace field có giá trị, map về Rule ID tồn tại | TC-XXX: Trace trống hoặc sai |
| Priority dùng `High` / `Medium` / `Low` — không dùng P1/P2/P3 | TC-XXX: Priority sai format |
| Khi Priority = `High` → Smoke = `Y` | TC-XXX: Priority=High nhưng Smoke=N |
| Precondition không trống (ghi `None` nếu không có) | TC-XXX: Precondition trống |
| **Auto ≥80% toàn file** — mọi Auto=N phải có lý do trong cột Trace | TC-XXX: Auto=N không có lý do |
| **Exploratory Testing rows ≥2, ở cuối file, STT là số nguyên tiếp nối** | File thiếu ET rows hoặc STT ET sai format |

Liệt kê tất cả TC cần sửa vào phần cuối Bảng 2 — Gap Analysis.

### Bước 5 — Gap Analysis (Bảng 2)

Với mỗi Rule ID có Coverage score `Partial` hoặc `Minimal`:

```
Rule ID	Nhóm còn thiếu	Mô tả lỗ hổng	Rủi ro	Đề xuất TC bổ sung	Priority	Câu hỏi làm rõ
```

Rủi ro: `Critical` = thiếu happy path/auth; `High` = thiếu negative/boundary; `Medium` = thiếu regression; `Low` = thiếu edge case.

### Bước 6 — Supplemental TC (Bảng 3)

TC mới để lấp gap. Dùng đúng 15 cột chuẩn + cột Note:

```
STT	Summary	Test Level	Precondition	Test Data	Step summary	Expected result	Priority	Story Linkages	Test Type	Smoke	Auto	Phụ thuộc TC	Teardown	Trace	Note
```

Quy tắc:
- STT tiếp nối STT cuối file gốc.
- Note: `"Bổ sung từ review {yyyy-mm-dd} — Gap: {nhóm thiếu}"`.
- Priority: `High` / `Medium` / `Low` (không dùng P1/P2/P3).
- Auto: `Y` mặc định; `N` chỉ khi UX chủ quan, hardware, Visual Builder drag-drop UI, race condition khó reproduce trong CI/CD, hoặc Exploratory — khi `N` phải ghi lý do ngắn trong cột Trace (ví dụ: Manual-UX, Manual-VB-DragDrop).
- TC bổ sung phải được merge vào TSV chính trước khi gate = `Approved`.

## Review Gate — Checklist bắt buộc pass 100%

- [ ] Rule Inventory đầy đủ — mọi AC/BR có trong danh sách
- [ ] Mọi Rule ID có ít nhất 1 TC map trong Coverage Map
- [ ] Trace field hợp lệ trong tất cả TC — không trống, không trỏ ID không tồn tại
- [ ] Happy path cover ≥90% Rule ID áp dụng
- [ ] Negative/Invalid input cover ≥70% Rule ID có input
- [ ] TC bổ sung từ gap analysis đã merge vào file TSV chính
- [ ] Không còn TC nào có Expected result mơ hồ
- [ ] Coverage score "Minimal" = 0 — không còn Rule ID nào dưới mức tối thiểu
- [ ] **Priority dùng `High`/`Medium`/`Low` — không có P1/P2/P3 trong file**
- [ ] **Khi Priority = `High` → Smoke = `Y` (không có ngoại lệ)**
- [ ] **Auto ≥80% toàn file; mọi Auto=N đều có lý do trong cột Trace**
- [ ] **Có ≥2 rows Exploratory Testing ở cuối file; STT là số nguyên tiếp nối từ TC scripted cuối cùng**

**Kết quả gate:**
- **Approved** → emit sign-off request L2, proceed sang skill 08 sau khi QA Lead confirm.
- **Not Approved** → liệt kê mục fail, không proceed.

## Sign-off Request (L2)

Emit sau khi hoàn thành — dù Approved hay Not Approved:

```
---
⏳ SIGN-OFF REQUEST — 07-review-tc (Level 2 — QA Lead)
Người review: [team.qc_lead từ qa-config]
SLA: 24 giờ
Output: testing-output/test-cases/review/review-{sprint}-{date}.md
Gate verdict: Approved / Not Approved
Action: Reply "Approved" hoặc "Cần chỉnh: [nội dung]"
---
```

Append vào `governance/audit-log.md`:
```yaml
execution_record:
  id: "{yyyy-mm-dd}-{HHmm}-07-review"
  timestamp: "{yyyy-mm-ddTHH:mm}"
  skill: "07-review-tc"
  project: "{project.name}"
  sprint: "{project.sprint}"
  executor: "{executor}"
  input_summary: "TC file: {filename}, {N} AC/BR, {N} TC existing"
  output_paths:
    - "testing-output/test-cases/review/review-{sprint}-{date}.md"
    - "testing-output/test-cases/functional/supplemental-{sprint}-{date}.tsv"
  status: "DONE"
  requires_human_review: true
  reviewer: null
  reviewed_at: null
  sign_off_status: "PENDING"
```

## Đường dẫn lưu file

- Coverage Map + Gap Analysis: `testing-output/test-cases/review/review-{sprint}-{yyyy-mm-dd}.md`
- Supplemental TC: `testing-output/test-cases/functional/supplemental-{sprint}-{yyyy-mm-dd}.tsv`
→ Ưu tiên `output_paths.test_cases.review` từ qa-config nếu có.

## Completion Status

| Status | Điều kiện |
|---|---|
| `DONE` | Coverage Map + Gap Analysis + Supplemental TC + gate verdict + sign-off emitted |
| `BLOCKED` | Thiếu tài liệu yêu cầu hoặc file TC không đọc được |
| `NEEDS_CONTEXT` | AC/BR không đủ để đánh giá coverage — liệt kê câu hỏi bổ sung |

## Checklist trước khi DONE

- [ ] Rule Inventory đầy đủ
- [ ] Bảng Coverage Map (19 cột) có trong output
- [ ] Bảng Gap Analysis với rủi ro đã phân loại
- [ ] Bảng Supplemental TC đã viết và merge vào TSV chính
- [ ] Gate verdict rõ ràng: `Approved` hoặc `Not Approved`
- [ ] Không còn P1/P2/P3 trong file TC được review
- [ ] Auto ≥80% và mọi Auto=N có lý do
- [ ] ET rows ≥2 ở cuối file với STT tiếp nối số nguyên
- [ ] Sign-off request đã emit
- [ ] Đã append execution record vào `governance/audit-log.md`
- [ ] Đã cập nhật `project/session-state.yaml` → `last_execution`, `pending_sign_offs`

## Stop Conditions

- Thiếu input bắt buộc và không thể suy diễn từ artifacts hiện có.
- Task yêu cầu publish ra ngoài nhưng chưa có governance approval.
- Action nằm ngoài scope của skill này.
