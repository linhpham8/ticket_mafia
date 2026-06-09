# Bug Severity & Defect Taxonomy

## Mức độ Severity

| Severity | Ký hiệu | Định nghĩa | Ví dụ |
|---|---|---|---|
| **Critical** | S1 | Chặn luồng nghiệp vụ cốt lõi, mất dữ liệu, crash app, bảo mật nghiêm trọng | Submit form ra trang lỗi, checkout bị vỡ, dữ liệu bị xóa không báo, SQL injection |
| **High** | S2 | Tính năng chính bị hỏng hoàn toàn, không có workaround | Tìm kiếm trả kết quả sai, upload file im lặng thất bại, vòng lặp redirect auth |
| **Medium** | S3 | Tính năng hoạt động nhưng có vấn đề rõ ràng, có workaround | Trang tải chậm >5s, validation thiếu nhưng submit vẫn qua, layout vỡ trên mobile |
| **Low** | S4 | Vấn đề nhỏ về giao diện, không ảnh hưởng chức năng | Typo trong footer, lệch 1px, hover state không nhất quán |

---

## Mức độ Priority

| Priority | Ký hiệu | Hành động |
|---|---|---|
| **Khẩn cấp** | P1 | Fix ngay trong ngày — chặn release hoặc gây mất dữ liệu |
| **Cao** | P2 | Fix trong sprint hiện tại |
| **Trung bình** | P3 | Fix sprint tiếp theo |
| **Thấp** | P4 | Defer — backlog, nice-to-have |

---

## Ma trận S/P (Severity × Priority)

| | S1 — Critical | S2 — High | S3 — Medium | S4 — Low |
|---|---|---|---|---|
| Luồng core, nhiều user ảnh hưởng | **P1** | **P1** | P2 | P3 |
| Luồng quan trọng, ít user ảnh hưởng | **P1** | P2 | P2 | P3 |
| Luồng phụ, workaround tồn tại | P2 | P2 | P3 | P4 |
| Edge case, ít khi gặp | P2 | P3 | P3 | P4 |

> **Nguyên tắc:** S1 luôn tối thiểu P2. P1 chỉ dùng khi cần action ngay trong ngày.

---

## 7 Category Phân loại Defect

### 1. Visual / UI
- Layout vỡ: các phần tử chồng lên nhau, text bị cắt, horizontal scrollbar xuất hiện
- Ảnh bị vỡ hoặc thiếu
- Z-index sai (element bị che khuất)
- Font / màu không nhất quán với design system
- Animation bị giật, transition không hoàn chỉnh
- Alignment lệch, spacing không đều
- Dark mode / theme bị lỗi

### 2. Functional
- Link bị gãy (404, sai đích đến)
- Button chết (click không có phản hồi)
- Form validation thiếu, sai, hoặc bị bypass
- Redirect sai luồng
- State không giữ được (data mất khi refresh, nhấn back)
- Race condition (double-submit, stale data)
- Kết quả tìm kiếm sai hoặc trống

### 3. UX
- Navigation khó hiểu (không có breadcrumb, dead-end)
- Thiếu loading indicator (người dùng không biết đang xử lý)
- Tương tác chậm >500ms không có feedback
- Thông báo lỗi mơ hồ ("Có lỗi xảy ra" không có chi tiết)
- Không có confirmation trước hành động hủy/xóa
- Pattern tương tác không nhất quán giữa các trang
- Dead-end: không có đường thoát hoặc hành động tiếp theo

### 4. Content
- Typo, lỗi ngữ pháp, lỗi chính tả
- Nội dung lỗi thời hoặc sai thông tin
- Placeholder / lorem ipsum còn sót
- Text bị cắt không có ellipsis
- Label nút hoặc field bị sai
- Empty state thiếu hoặc không hữu ích

### 5. Performance
- Trang tải chậm >3 giây
- Scroll bị giật (dropped frames)
- Layout shift: nội dung nhảy sau khi load
- Quá nhiều request mạng (>50 trên 1 trang)
- Ảnh chưa được tối ưu, kích thước quá lớn
- JavaScript blocking làm trang không phản hồi khi đang load

### 6. Console / Errors
- JavaScript exception (uncaught error)
- Network request thất bại (4xx, 5xx)
- Deprecation warning (sắp bị hỏng)
- CORS error
- Mixed content warning (HTTP resource trên HTTPS)
- CSP violation

### 7. Accessibility
- Ảnh thiếu alt text
- Form input không có label
- Keyboard navigation bị hỏng (không tab được đến element)
- Focus trap (không thoát được modal / dropdown)
- ARIA attribute thiếu hoặc sai
- Contrast màu không đủ (WCAG AA: tối thiểu 4.5:1)
- Nội dung không tiếp cận được bằng screen reader

---

## Action theo Severity

| Severity | Action QA | Action Dev |
|---|---|---|
| S1 | Dừng test liên quan, báo ngay QC Lead + Dev | Fix trong ngày, không merge feature mới |
| S2 | Document đầy đủ repro steps, retest ngay sau fix | Fix trong sprint, không close ticket chưa có regression test |
| S3 | Document, schedule retest | Fix theo kế hoạch sprint |
| S4 | Log vào backlog, optional screenshot | Fix khi có thời gian |

---

## Checklist triage bug mới

- [ ] Đã xác định Severity (S1–S4) dựa trên impact + frequency
- [ ] Đã xác định Priority (P1–P4) dựa trên ma trận S/P + business context
- [ ] Đã gán đúng 1 trong 7 Category
- [ ] Repro steps đủ để Dev reproduce độc lập
- [ ] Screenshot hoặc video đính kèm (bắt buộc với S1/S2)
- [ ] Đã check xem bug này có block TC khác không → nếu có, ghi vào Blocker
