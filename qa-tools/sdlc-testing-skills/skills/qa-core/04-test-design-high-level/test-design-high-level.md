---
name: 04-test-design-high-level
description: >
  Thiết kế test design high-level dạng Markdown outline cho function có logic phức tạp,
  phục vụ review nhanh trước khi viết test case chi tiết. Bước này optional,
  chỉ chạy khi cần. Output bắt buộc: Markdown outline + checklist review gate 9 mục.
---

# High-Level Test Design

> **BẮT BUỘC**: Đọc toàn bộ skill này TRƯỚC khi bắt đầu. Không bỏ qua bất kỳ bước nào.

## Khi nào dùng skill này

Dùng khi có một trong các dấu hiệu sau:
- Function có nhiều nhánh logic, nhiều rule, nhiều hệ thống phụ thuộc.
- Có nhiều mode xử lý (AI + Rule, fallback, override, precedence).
- Team cần review nhanh scope test trước khi chi tiết hóa.

**Không bắt buộc** cho mọi yêu cầu.

## Đọc trước khi bắt đầu

- Đọc `project/qa-config.yaml` nếu tồn tại.
- Đọc `governance/GOVERNANCE.md` trước khi finalize.
- Governance gate: `L1` — không cần QA Lead review trước khi proceed.
- Đọc `references/test-design-mindmap-template.md` để lấy template Markdown outline.

## Inputs

- AC/User Story/BR liên quan function (bắt buộc)
- Test Plan và/hoặc qa-config.yaml (nếu có)
- Danh sách function/module cần review (nếu user chỉ định)

Nếu thiếu AC/BR có ý nghĩa → ghi `[Cần bổ sung]` và dừng.

## Workflow bắt buộc

### Bước 1 — Xác định boundary và actors

- Feature boundary, actors, states, critical paths.
- Mọi kênh UI có liên quan (Web / App / API).

### Bước 2 — Sinh Markdown outline (định dạng bắt buộc)

Sử dụng **đúng 1 format** Markdown outline/Markmap. Không dùng bảng, không dùng format khác.

Cấu trúc bắt buộc:
```
# HLTC: [Tên feature]
## Main flow
### [Sub flow 1]
#### UI (Web / App / API)
#### Validation
- Authorization: [quyền cần có]
- Business rule: [rule quan trọng]
#### Impact
- Ảnh hưởng tới: [module/data]
#### Abnormal case
- Timeout
- Network/system error
### [Sub flow 2]
...
```

Nhánh bắt buộc có nội dung tối thiểu:
- **Function/Sub flow**: liệt kê AC/Sub flow chính
- **UI**: nếu đa kênh thì phải có Web/App/API
- **Validation**: authorization + business validation quan trọng
- **Impact**: current functions + data impact/cut-off data
- **Abnormal case**: timeout + network/system error
- **Negative**: ≥1 nhánh negative cho mỗi rule quan trọng

Nếu có quy tắc ưu tiên (precedence): mô tả rõ trong outline, ghi tiêu chí chọn rule ưu tiên.

### Bước 3 — Review Gate (bắt buộc, 9 mục cố định)

Đánh giá chính xác 9 mục sau (không tự thêm/bớt):

- [ ] Đã cover đủ các nhánh Function/Sub flow chính
- [ ] Đã cover UI đúng kênh cần áp dụng (Web/App/API)
- [ ] Đã cover Validation: authorization + business rule quan trọng
- [ ] Đã cover Impact: current functions và data impact
- [ ] Đã cover Abnormal case: timeout và network/system error
- [ ] Đã cover ít nhất 1 negative branch mỗi rule quan trọng
- [ ] Đã xác định rõ branch cần vào Smoke
- [ ] Không có mâu thuẫn rõ ràng với AC/BR
- [ ] Team đã review và chốt "Approved" scope high-level

Dòng kết quả gate (bắt buộc có trong file):
```
Kết quả gate: Approved / Not Approved
```

### Bước 4 — Xử lý kết quả gate

**Approved**: được chuyển sang Skill 05 (gen-tc-functional) để viết TC chi tiết.

**Not Approved**: cập nhật lại HLTC outline, review lại trước khi vào Skill 05.

## Quy tắc Approved / trạng thái file

- HLTC chỉ được xem là đã chốt khi có xác nhận review và Approved từ user/team trong context hiện tại.
- Khi có xác nhận Approved → cập nhật ngay file HLTC:
  - Tick `[x] Team đã review và chốt "Approved" scope high-level`
  - Đổi dòng `Kết quả gate` thành `Approved`
- Không được giữ trạng thái cuối file là `Not Approved` nếu context mới nhất đã xác nhận Approved.
- Mọi bước tiếp theo phụ thuộc HLTC phải dựa trên trạng thái đã ghi trong file — không dựa trên trao đổi miệng trong chat.

## Đường dẫn lưu file

`testing-output/test-cases/hltc/hltc-{module}-{sprint}-v{semver}-{yyyy-mm-dd}_{HHmm}.md`
→ Ưu tiên `output_paths.test_cases.hltc` từ qa-config nếu có.

## Completion Status

| Status | Điều kiện |
|---|---|
| `DONE` | Có Markdown outline hợp lệ + checklist 9 mục + dòng `Kết quả gate` rõ ràng + file lưu đúng path |
| `BLOCKED` | Thiếu AC/BR có ý nghĩa |
| `NEEDS_CONTEXT` | AC/BR không đủ để xác định scope — liệt kê câu hỏi bổ sung |

## Checklist trước khi DONE

- [ ] Markdown outline đủ nhánh chính + ít nhất 1 nhánh negative mỗi rule quan trọng
- [ ] Review Gate 9 mục đã tick đầy đủ
- [ ] Dòng kết quả gate rõ ràng: `Kết quả gate: Approved` hoặc `Not Approved`
- [ ] File lưu đúng `testing-output/test-cases/hltc/` với version và timestamp trong tên
- [ ] Đã append execution record vào `governance/audit-log.md`
- [ ] Đã cập nhật `project/session-state.yaml` → `last_execution`

## Stop Conditions

- Thiếu AC/BR và không thể suy diễn từ artifacts hiện có.
- Task yêu cầu publish ra ngoài nhưng chưa có governance approval.
- Action nằm ngoài scope của skill này.
