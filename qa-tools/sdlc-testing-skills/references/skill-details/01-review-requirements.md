# Detailed Procedure: 01-review-requirements

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

- [ ] Review đủ 3 góc nhìn: QC Expert, End User, BA/Dev
- [ ] TSV issues list đủ cột, không còn dòng trống không giải thích
- [ ] Completion Status rõ ràng: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution.skill`, `last_execution.status`, `notes`

---

## Mục đích

Review tài liệu yêu cầu từ 3 góc nhìn thực chiến: **QC Expert · End User · BA/Senior Dev**

Áp dụng được cho mọi domain và kiến trúc.
Output tập trung vào những vấn đề thực sự cản trở development và testing —
không liệt kê dài dòng theo checklist học thuật.

---

## Biến đầu vào

| Biến | Mô tả | Ví dụ |
|------|-------|-------|
| `{DOCUMENT}` | Tài liệu yêu cầu cần review | Paste nội dung hoặc section cụ thể |
| `{DOMAIN}` | Domain nghiệp vụ | ecommerce / AI platform / fintech / data platform |
| `{ARCHITECTURE}` | Kiến trúc kỹ thuật | Microservice / Monolith / Event-driven / API-first |
| `{COMPLIANCE}` | Yêu cầu tuân thủ nếu có | PCI-DSS / GDPR / Decree 356 / N/A |

---

## VAI 1 — QC EXPERT

Bạn là QC Lead 10 năm kinh nghiệm. Bạn đọc requirements với mục tiêu duy nhất: viết được test case đầy đủ và chính xác.

Hỏi và chỉ ra vấn đề khi:

**Không thể viết test case vì thiếu thông tin**
- Expected output chưa được định nghĩa: khi X xảy ra thì hệ thống trả về gì?
- Điều kiện pass/fail không rõ: "hệ thống xử lý nhanh" — nhanh là bao nhiêu ms?
- Precondition chưa rõ: test case này cần data/state gì trước khi chạy?
- Không rõ ai là actor: hành động này do user, system, hay external service thực hiện?

**Luồng chưa đầy đủ**
- Happy path có nhưng failure case không có: nếu bước X thất bại thì sao?
- Edge case bị bỏ qua: giá trị rỗng, null, giới hạn trên/dưới, timeout, concurrent request?
- Luồng hủy/rollback chưa được mô tả: nếu user hủy giữa chừng ở bước X thì state của hệ thống như thế nào?
- Trạng thái chuyển đổi chưa đầy đủ: từ trạng thái A có thể đi đến những trạng thái nào?

**Mâu thuẫn gây khó test**
- 2 requirement nói ngược nhau về cùng 1 behavior
- Non-functional requirement không đo được
- Cùng 1 khái niệm được gọi bằng nhiều tên khác nhau trong tài liệu

---

## VAI 2 — END USER

Bạn là người dùng cuối thực tế của hệ thống trong domain `{DOMAIN}`.
Bạn không quan tâm kỹ thuật — bạn chỉ quan tâm đến trải nghiệm.

Hỏi và chỉ ra vấn đề khi:

**Luồng nghiệp vụ không tự nhiên**
- Các bước bắt buộc có hợp lý với thực tế sử dụng không?
- Thứ tự thực hiện có đúng với cách người dùng thực sự làm không?
- Có bước nào thừa hoặc gây friction không cần thiết không?

**Thông báo và phản hồi chưa đủ**
- Khi lỗi xảy ra, user biết lỗi gì và cần làm gì tiếp theo không?
- Trạng thái xử lý có được thông báo cho user không (loading, pending, completed)?
- Kết quả thành công/thất bại có rõ ràng với user không?

**Thiếu use case thực tế**
- Scenario nào người dùng hay gặp nhất mà tài liệu chưa đề cập?
- Có trường hợp nào user làm sai/làm khác expected flow mà chưa được xử lý?
- Permission và quyền truy cập có phù hợp với từng loại user không?

---

## VAI 3 — BA / SENIOR DEV

Bạn là BA hoặc Senior Dev nhiều năm kinh nghiệm với `{ARCHITECTURE}`.
Bạn đọc requirements để estimate, design, và implement.

Hỏi và chỉ ra vấn đề khi:

**Business rule chưa đủ rõ để implement**
- Logic tính toán chưa có công thức cụ thể: tính như thế nào, làm tròn không?
- Điều kiện phân nhánh chưa cover hết: nếu A và B cùng đúng thì ưu tiên cái nào?
- Thứ tự ưu tiên giữa các rule chưa rõ khi chúng conflict nhau
- Giới hạn/constraint của nghiệp vụ chưa được định nghĩa: tối đa bao nhiêu, tối thiểu bao nhiêu?

**Tích hợp và dependency chưa rõ**
- Service/system nào cần tích hợp, ai gọi ai, theo flow nào?
- Data nào cần từ service khác, format là gì, khi service đó unavailable thì xử lý thế nào?
- Có async flow nào không? Nếu có, trạng thái trung gian được xử lý ra sao?
- Với `{ARCHITECTURE}`: ranh giới trách nhiệm giữa các service/module có rõ không?

**Mâu thuẫn hoặc thiếu sót kỹ thuật**
- Requirement này có conflict với constraint kỹ thuật đã biết không?
- Có requirement nào không khả thi với kiến trúc `{ARCHITECTURE}` không?
- Performance expectation có realistic không?
- Với `{COMPLIANCE}`: requirement có đáp ứng đủ yêu cầu tuân thủ không?

**Data và state chưa được định nghĩa đủ**
- Data model/schema cần thiết cho feature này đã được mô tả chưa?
- State machine của object chính đã đầy đủ chưa (tất cả trạng thái + transition)?
- Ai là owner của data, ai được phép đọc/ghi?
- Versioning và backward compatibility có được xem xét không?

---

## Format output

Output gồm 2 phần:

### PHẦN 1 — TSV (copy thẳng vào Google Sheet)

In ra dòng header và toàn bộ issues theo định dạng TSV.
Mỗi issue = 1 dòng. Các cột cách nhau bằng TAB.
KHÔNG dùng dấu phẩy làm separator. KHÔNG wrap trong code block.
Nếu nội dung 1 ô có dấu TAB hoặc xuống dòng, thay bằng dấu cách.

Dòng header (copy nguyên):
ID	Vai trò	Loại vấn đề	Vị trí	Vấn đề	Tại sao quan trọng	Câu hỏi / đề xuất	Mức độ	Trạng thái

Giải thích từng cột:

| Cột | Giá trị cho phép | Ghi chú |
|-----|-----------------|---------|
| ID | RV-001, RV-002... | Tăng dần |
| Vai trò | QC / END_USER / BA_DEV | Vai trò phát hiện issue |
| Loại vấn đề | Thiếu failure case / Mơ hồ / Mâu thuẫn / Không testable / Thiếu business rule / Thiếu integration spec / Thiếu data spec / Không khả thi | Chọn 1 loại gần nhất |
| Vị trí | Tên AC / section cụ thể | Ví dụ: AC1.2, AC3.1, Precondition |
| Vấn đề | Mô tả ngắn gọn tối đa 30 từ | Súc tích, không giải thích dài |
| Tại sao quan trọng | Impact cụ thể nếu không clarify | Ví dụ: không viết được TC, dev implement sai |
| Câu hỏi / đề xuất | Câu hỏi cho BA/PM hoặc gợi ý sửa | Actionable, cụ thể |
| Mức độ | Blocker / Major / Minor | Blocker = phải clarify trước khi dev bắt đầu |
| Trạng thái | Open | Mặc định Open — BA/PM tự cập nhật sau |

Ví dụ 1 dòng TSV (minh họa):
RV-001	QC	Thiếu failure case	AC3.2	Không mô tả behavior khi payment gateway timeout	Không viết được TC negative, dev implement tùy ý	Khi GW timeout sau X giây hệ thống làm gì? Đơn hàng ở trạng thái nào?	Blocker	Open

---

### PHẦN 2 — TỔNG KẾT (sau TSV)

Sau khi in xong toàn bộ TSV, in thêm:

```
Tổng số issues: [N]
- Blocker: [n] — [liệt kê ID]
- Major:   [n] — [liệt kê ID]
- Minor:   [n] — [liệt kê ID]

Đánh giá tổng thể: [sẵn sàng để dev / cần clarify trước khi dev / cần làm lại đáng kể]
Lý do: [1-2 câu ngắn gọn]
```

---

## Ghi chú sử dụng

- Nếu tài liệu dài, chia nhỏ theo section và chạy prompt từng phần
- Kết quả TSV nên được QC Lead review trước khi gửi cho BA/PM
- Copy toàn bộ phần TSV → paste vào Google Sheet ô A1 → Data > Split text to columns (separator: Tab)
- Không dùng data thật (PII, credentials) khi paste vào prompt
- Với domain có compliance đặc thù (fintech, healthcare, AI law): điền `{COMPLIANCE}` đầy đủ để AI có context phù hợp

---

## Completion Status

- **DONE** — Đã review đủ 3 góc nhìn, TSV đầy đủ, tổng kết rõ ràng
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng tài liệu quá ít thông tin để review sâu
- **NEEDS_CONTEXT** — Cần bổ sung: {Domain / Architecture / Compliance chưa được cung cấp}
- **BLOCKED** — Tài liệu không đọc được hoặc quá ngắn để review có ý nghĩa
