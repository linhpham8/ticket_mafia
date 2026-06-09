# Detailed Procedure: 07-review-tc

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

> ⚠️ **L2 — QA Lead review bắt buộc (SLA: 24h).** Không gửi output cho user cho đến khi nhận "Approved". Xem mục Sign-off cuối file.

- [ ] Coverage Map 19 cột đầy đủ
- [ ] Gap Analysis + Supplemental TC đã merge vào TSV chính
- [ ] Gate verdict rõ ràng: `Approved` hoặc `Not Approved`
- [ ] Sign-off request L2 đã emit, chờ QA Lead reply
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `pending_sign_offs`

---

## Quick Reference

| | |
|---|---|
| **Input bắt buộc** | Tài liệu yêu cầu (US/AC/BR) + File TC (TSV/Markdown/Excel) |
| **Output** | 3 bảng (Coverage Map, Gap Analysis, Supplemental TC) + Gate verdict |
| **Time estimate** | 30–90 phút tùy số lượng TC và AC |
| **Sign-off** | L2 — QA Lead xác nhận trước khi move sang data/automation |
| **Gate result** | Approved / Not Approved |

---

## Đầu vào

| Trường | Bắt buộc? | Mô tả |
|---|---|---|
| Tài liệu yêu cầu | ✔ | US / AC / BR — mỗi yêu cầu có ID riêng |
| File test case | ✔ | Danh sách TC đã viết (TSV, Excel, hoặc Markdown; Functional hoặc SIT) |
| qa-config.yaml | Khuyến nghị | Nếu có → đọc `scope.modules` để group coverage theo module |

Nếu thiếu tài liệu yêu cầu hoặc file TC → ghi `[Cần bổ sung]`, liệt kê câu hỏi làm rõ, dừng lại.

---

## Bước 1 — Xây dựng Rule Inventory

Trước khi review TC, tạo Rule Inventory từ tài liệu yêu cầu:

1. Đọc toàn bộ AC/US/BR
2. Gán ID cho mỗi rule/AC/BR nếu chưa có (AC-01, AC-02, BR-01...)
3. Tạo danh sách inventory:

| Rule ID | Mô tả ngắn | Loại | Độ phức tạp | Module |
|---|---|---|---|---|
| AC-01 | [Mô tả rule] | AC / BR / US | Cao / Trung bình / Thấp | [module nếu có] |

**Không bỏ sót rule nào** — mọi requirement phải có trong inventory.

---

## Bước 2 — Phân tích coverage theo 12 nhóm

Với mỗi Rule ID, kiểm tra file TC hiện tại đã cover nhóm nào:

| # | Nhóm | Mô tả | Bắt buộc? |
|---|---|---|---|
| 1 | Happy path | Luồng chính hoạt động đúng với data hợp lệ | Mọi AC |
| 2 | Negative / Invalid input | Data sai, thiếu, sai định dạng | AC có input |
| 3 | Boundary Value | Giá trị biên (min, max, min-1, max+1) | AC có giá trị số |
| 4 | Authorization | Phân quyền đúng role, block sai role | AC liên quan auth |
| 5 | Error handling | Lỗi hệ thống, timeout, network error | AC có external call |
| 6 | State transition | Thay đổi trạng thái đúng sequence | AC có workflow |
| 7 | Regression | Tính năng cũ không bị ảnh hưởng | AC thay đổi core |
| 8 | Performance | Response time, tải lớn | AC có SLA yêu cầu |
| 9 | Data integrity | Data lưu/xử lý đúng, không mất/corrupt | AC có data persistence |
| 10 | UI / UX | Hiển thị đúng, responsive, a11y cơ bản | AC có giao diện |
| 11 | Integration / API | Contract giữa service, response schema | AC có API call |
| 12 | Edge case / Exploratory | Scenario hiếm gặp, kết hợp điều kiện đặc biệt | Tùy độ phức tạp |

---

## Bảng 1 — Coverage Map

Mỗi dòng = 1 Rule ID/AC/BR từ tài liệu yêu cầu.
Header chuẩn 15 cột (đồng bộ references/tc-template.tsv) + 4 cột bổ sung:

```
STT	Summary	Test Level	Precondition	Test Data	Step summary	Expected result	Priority	Story Linkages	Test Type	Smoke	Auto	Phụ thuộc TC	Teardown	Trace	Rule ID	Nhóm cover	Nhóm còn thiếu	Coverage score
```

Coverage score: Full (≥8/12 nhóm áp dụng) / Partial (4-7) / Minimal (<4)

---

## Bảng 2 — Gap Analysis (Per-rule)

Với mỗi Rule ID có Coverage score Partial hoặc Minimal:

```
Rule ID	Nhóm còn thiếu	Mô tả lỗ hổng	Rủi ro (Critical/High/Medium/Low)	Đề xuất TC bổ sung	Priority	Câu hỏi làm rõ
```

Rủi ro: Critical = thiếu happy path/auth; High = thiếu negative/boundary; Medium = thiếu regression; Low = thiếu edge case.

---

## Bảng 3 — TC bổ sung (Supplemental TC)

TC mới để lấp gap. Dùng đúng 15 cột chuẩn + cột Note:

```
STT	Summary	Test Level	Precondition	Test Data	Step summary	Expected result	Priority	Story Linkages	Test Type	Smoke	Auto	Phụ thuộc TC	Teardown	Trace	Note
```

Quy tắc: STT tiếp nối STT cuối file gốc. Note: "Bổ sung từ review {yyyy-mm-dd} — Gap: {nhóm thiếu}".
TC bổ sung phải được merge vào TSV chính trước khi gate = Approved.

---

## Bước 3 — Kiểm tra chất lượng TC hiện tại

Với từng TC trong file gốc, check theo shared-schema/testcase.schema.yaml:

| Tiêu chí | Flag nếu fail |
|---|---|
| Summary ≥ 10 ký tự, mô tả rõ action + object | TC-XXX: Summary quá ngắn |
| Expected result cụ thể, không chứa "hoạt động đúng" / "thành công" | TC-XXX: Expected result mơ hồ |
| Trace field có giá trị, map về Rule ID tồn tại | TC-XXX: Trace trống hoặc sai |
| Priority hợp lý (P1 → Smoke=Yes) | TC-XXX: P1 nhưng Smoke=No |
| Precondition không trống (ghi None nếu không có) | TC-XXX: Precondition trống |

Liệt kê tất cả TC cần sửa vào cuối Bảng 2.

---

## Review Gate — Checklist bắt buộc pass 100%

- [ ] Rule Inventory đầy đủ — mọi AC/BR có trong danh sách
- [ ] Mọi Rule ID có ít nhất 1 TC map trong Coverage Map
- [ ] Trace field hợp lệ trong tất cả TC — không trống, không trỏ ID không tồn tại
- [ ] Happy path cover ≥ 90% Rule ID áp dụng
- [ ] Negative/Invalid input cover ≥ 70% Rule ID có input
- [ ] TC bổ sung từ gap analysis đã merge vào file TSV chính
- [ ] Không còn TC nào có Expected result mơ hồ (theo forbidden_phrases trong schema)
- [ ] Coverage score "Minimal" = 0 — không còn Rule ID nào dưới mức tối thiểu

**Kết quả gate:**
- **Approved** → emit sign-off request L2, proceed sang skill 08 sau khi QA Lead confirm
- **Not Approved** → liệt kê mục fail, không proceed

---

## Sign-off Request (L2) + Audit Log

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

Append vào governance/audit-log.md:
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

---

## Lưu file

- Coverage Map + Gap Analysis: `testing-output/test-cases/review/review-{sprint}-{yyyy-mm-dd}.md`
- Supplemental TC: `testing-output/test-cases/functional/supplemental-{sprint}-{yyyy-mm-dd}.tsv`

## Definition of Done

- [ ] Rule Inventory đầy đủ
- [ ] Bảng Coverage Map (19 cột) có trong output
- [ ] Bảng Gap Analysis với rủi ro đã phân loại
- [ ] Bảng Supplemental TC đã viết và merge vào TSV chính
- [ ] Gate verdict rõ ràng: Approved / Not Approved
- [ ] Sign-off request đã emit
- [ ] Audit log entry đã append