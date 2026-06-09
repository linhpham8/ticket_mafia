# Detailed Procedure: 11-demo-preparation

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| Danh sách ticket DONE trong sprint (key, summary) | ✅ |
| Tên sprint, ngày demo, thời lượng cho phép | ✅ |
| Danh sách người tham dự (stakeholder, PO, Dev, QC) | Khuyến nghị |
| Môi trường demo (staging URL, tài khoản test) | ✅ |
| Danh sách người trình bày (presenter) | Khuyến nghị |

Nếu project có `qa-config.yaml` → đọc trước:
- `environments.staging.url` → URL demo mặc định
- `team.qc_lead`, `team.qc_engineers` → danh sách presenter tiềm năng
- `uat.stakeholders` → danh sách người tham dự demo

Thiếu thông tin bắt buộc → ghi `[Cần bổ sung]`, hỏi lại. Không đoán mò.

---


## ⚑ Kiểm tra trước khi báo DONE

> ⚠️ **L2 — QA Lead review bắt buộc.** Xem mục Sign-off cuối file.

- [ ] Demo script đủ: luồng chính, presenter, data, timing ước tính
- [ ] Checklist pre-demo đủ mục (môi trường, tài khoản, backup plan)
- [ ] Sign-off request L2 đã emit, chờ QA Lead reply
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `pending_sign_offs`

---

## Bước 1 — Lọc và phân nhóm ticket demo

Từ danh sách ticket DONE, xác định:
- **Demo được:** ticket có UI / luồng người dùng rõ ràng, đã pass test
- **Không demo trực tiếp:** ticket backend-only, config, hotfix kỹ thuật → ghi note ngắn vào mục "Cập nhật kỹ thuật"
- **Cần thận trọng:** feature mới, thay đổi breaking → ưu tiên demo ổn định trước

Sắp xếp thứ tự demo theo nguyên tắc:
1. Feature lớn / high business value → demo trước
2. Luồng liên quan nhau → demo liền mạch, không nhảy cóc
3. Feature còn lỗi nhỏ → demo sau hoặc bỏ qua, ghi chú rõ

---

## Bước 2 — Thiết kế luồng demo

Với mỗi nhóm feature, thiết kế **1 kịch bản người dùng liên tục** (không demo từng ticket riêng lẻ).

Ví dụ: thay vì demo "Ticket-101: Thêm filter" → "Ticket-102: Export CSV" riêng nhau, gộp thành:
> "Người dùng vào trang báo cáo, áp dụng filter theo tháng, sau đó export kết quả ra CSV."

Mỗi luồng demo cần xác định:
- **Điểm bắt đầu:** URL / màn hình cụ thể
- **Các bước thực hiện:** hành động người dùng, không phải click kỹ thuật
- **Điểm kết thúc:** kết quả mong đợi stakeholder thấy
- **Thời gian ước tính:** thực tế (không tính hỏi đáp)

---

## Bước 3 — Chuẩn bị data demo

Với mỗi luồng demo, xác định data cần có sẵn trước:

| Luồng | Data cần chuẩn bị | Tài khoản | Ghi chú |
|---|---|---|---|
| {Luồng 1} | {Mô tả data} | {user/pass} | {Lưu ý đặc biệt} |

Nguyên tắc chuẩn bị data:
- Data phải **realistic** — không dùng "test123", "aaa", "1111"
- Tránh data nhạy cảm thật (email thật, CMND thật, số thẻ thật)
- Chuẩn bị **bản dự phòng** nếu thao tác demo làm thay đổi data (ví dụ: submit form → cần reset)
- Ghi rõ bước reset data sau mỗi luồng nếu cần

---

## Bước 4 — Phân công và thời gian

Tổng hợp thành bảng phân công:

| # | Luồng demo | Presenter | Thời gian | Ticket liên quan |
|---|---|---|---|---|
| 1 | {Tên luồng} | {Tên} | {X phút} | {PROJ-XXX} |

Cân đối tổng thời gian: để lại **ít nhất 20%** cho phần hỏi đáp.

---

## Bước 5 — Checklist môi trường trước demo

Tạo checklist cụ thể để kiểm tra **tối thiểu 1 ngày trước** và **30 phút trước** khi demo:

### Kiểm tra 1 ngày trước
- [ ] Môi trường staging hoạt động ổn định, không có deploy mới trong giờ demo
- [ ] Tài khoản test đăng nhập được, đúng role / permission
- [ ] Data demo đã chuẩn bị xong, kiểm tra lần cuối
- [ ] Tất cả luồng demo đã chạy thử thành công ít nhất 1 lần
- [ ] URL demo đã share cho người trình bày
- [ ] Backup plan xác định (nếu môi trường lỗi → dùng video / screenshot)

### Kiểm tra 30 phút trước demo
- [ ] Tắt thông báo (Slack, email, hệ thống)
- [ ] Zoom / Meet / Teams link hoạt động, share screen thử
- [ ] Browser đã xóa cache, đang ở đúng URL bắt đầu
- [ ] Data demo còn nguyên (chưa bị ai thay đổi)
- [ ] Tài liệu kịch bản mở sẵn để tham chiếu khi trình bày

---

## Format output — Demo Script

```markdown




**Ngày demo:** [dd/mm/yyyy] | **Thời lượng:** [X phút]
**Môi trường:** [URL staging]
**Người tham dự:** [Danh sách]

---

## Tổng quan Sprint

> [1-2 câu tóm tắt sprint này làm được gì — viết theo góc nhìn business, không phải kỹ thuật]

**Tổng ticket hoàn thành:** [N] | **Demo được:** [N] | **Cập nhật kỹ thuật:** [N]

---

## Kịch bản Demo

### [1. Tên luồng — X phút] — Presenter: [Tên]

**Mục tiêu:** [Điều stakeholder sẽ thấy/hiểu sau phần này]

**Bắt đầu tại:** [URL / màn hình]

**Các bước:**
1. [Hành động người dùng — viết theo ngôn ngữ nghiệp vụ]
2. [Hành động tiếp theo]
3. **Điểm nhấn:** [Tính năng mới / cải tiến cần stakeholder chú ý]

**Kết quả mong đợi:** [Stakeholder thấy gì]
**Ticket:** [PROJ-XXX, PROJ-YYY]

---

### [2. Tên luồng — X phút] — Presenter: [Tên]

[Tương tự]

---

## Cập nhật kỹ thuật (không demo trực tiếp)

| Hạng mục | Mô tả | Tác động |
|---|---|---|
| [Ticket] | [Mô tả ngắn] | [Lợi ích / cải thiện gì] |

---

## Hỏi & Đáp — [X phút]

[Để trống — ghi chú câu hỏi trong buổi demo]

---

## Checklist Pre-Demo

### 1 ngày trước
- [ ] Môi trường staging ổn định
- [ ] Tài khoản test OK
- [ ] Data demo sẵn sàng
- [ ] Dry-run thành công

### 30 phút trước
- [ ] Thông báo đã tắt
- [ ] Screen share thử xong
- [ ] Browser ở đúng URL bắt đầu
- [ ] Data demo còn nguyên
```

---

**Lưu file vào:** `output_paths.demo` từ qa-config (default: `testing-output/demo/`)
→ `demo/demo-script-{project.sprint}.md`

---

## Lưu ý khi trình bày

- **Nói theo ngôn ngữ nghiệp vụ** — không giải thích implementation, không đề cập tên bảng/API
- **Không demo feature chưa pass test** — nếu bắt buộc, cảnh báo trước: "Phần này đang hoàn thiện, demo để lấy feedback"
- **Sự cố môi trường** → không xin lỗi quá nhiều, chuyển sang backup (video / screenshot) và tiếp tục
- **Thời gian vượt** → cắt bớt luồng ít quan trọng, không đẩy nhanh luồng đang demo

---


## Sign-off Request (L2)



Sau khi nhan Approved: cap nhat project/session-state.yaml, xoa item khoi pending_sign_offs.

---

## Completion Status

- **DONE** — Kịch bản hoàn chỉnh, checklist đủ, phân công xong, data sẵn sàng
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng: {Môi trường chưa ổn định / Một số luồng chưa dry-run / Thiếu presenter}
- **BLOCKED** — Không thể chuẩn bị do: {Ticket chưa DONE / Môi trường không có / Thiếu thông tin demo}
- **NEEDS_CONTEXT** — Cần bổ sung: {Danh sách ticket DONE / URL môi trường / Thời lượng demo}


