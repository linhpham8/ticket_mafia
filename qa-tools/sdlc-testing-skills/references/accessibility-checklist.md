# Accessibility Testing Checklist

> Skill 15 đọc file này để thực hiện accessibility testing theo chuẩn WCAG 2.1 AA.
> Mỗi hạng mục có: điểm kiểm tra cụ thể, cách kiểm tra, severity nếu phát hiện.
> Tham chiếu: WCAG 2.1 Level AA (tiêu chuẩn tối thiểu cho hầu hết ứng dụng B2B/B2C).

---

## 1. Hình ảnh và Media

### 1.1 Alt text cho hình ảnh
- [ ] Mọi `<img>` có nội dung cần có `alt` mô tả ý nghĩa, không phải tên file
  - Sai: `alt="image_001.jpg"` hoặc `alt="photo"`
  - Đúng: `alt="Biểu đồ doanh thu quý 3 — tăng 15% so với quý 2"`
- [ ] Hình ảnh trang trí (không mang thông tin) dùng `alt=""` (empty, không phải thiếu)
- [ ] Icon có nghĩa: phải có `aria-label` hoặc văn bản ẩn cho screen reader
- [ ] Hình ảnh trong link: `alt` mô tả đích đến, không phải mô tả hình

**Cách kiểm tra:** Inspect element, tìm `<img>` thiếu `alt` hoặc `alt` không có nghĩa.
Dùng browser extension: axe DevTools, WAVE, Lighthouse.

**Severity nếu thiếu:** S3 (Medium) — S2 (High) nếu hình ảnh là nội dung chính

---

### 1.2 Video và Audio
- [ ] Video có phụ đề (captions) đồng bộ — không chỉ auto-generate thiếu chính xác
- [ ] Audio có transcript văn bản đi kèm
- [ ] Video tự phát (autoplay) không có âm thanh — hoặc có nút tắt rõ ràng
- [ ] Player có đủ controls: play/pause/stop tiếp cận được bằng bàn phím

**Severity nếu thiếu:** S3 (Medium)

---

## 2. Keyboard Navigation

### 2.1 Tab order hợp lý
- [ ] Nhấn Tab từ đầu trang, focus di chuyển theo thứ tự logical (trái → phải, trên → dưới)
- [ ] Không có "focus trap" ngoài modal: sau khi tab hết trang, không bị mắc kẹt
- [ ] Skip navigation link ("Bỏ qua đến nội dung chính") có sẵn ở đầu trang

**Cách kiểm tra:** Đóng chuột, dùng Tab để navigate toàn bộ trang. Ghi nhận thứ tự focus.

**Severity nếu lỗi:** S2 (High) — người dùng bàn phím không thể dùng ứng dụng

---

### 2.2 Focus visible
- [ ] Focus indicator rõ ràng — không bị ẩn bởi CSS `outline: none` hoặc `outline: 0`
- [ ] Focus indicator đủ contrast (ít nhất 3:1 so với background)
- [ ] Custom component (dropdown, slider, tab) có focus indicator khi active

**Cách kiểm tra:** Tab qua từng element, quan sát có thấy focus ring không.

**Severity nếu thiếu:** S2 (High)

---

### 2.3 Keyboard traps
- [ ] Modal/dialog: focus bị trap bên trong khi mở (đúng), ESC đóng được, focus trả về trigger khi đóng
- [ ] Dropdown/menu: Escape đóng, focus trả về button mở
- [ ] Date picker, combobox: hoạt động đầy đủ bằng bàn phím (arrow keys, enter, escape)

**Severity nếu lỗi:** S1 (Critical) — người dùng bị mắc kẹt không thoát được

---

## 3. Form Accessibility

### 3.1 Label cho inputs
- [ ] Mọi input có `<label>` liên kết đúng (dùng `for`/`id` hoặc wrap)
  - Sai: placeholder thay thế label (placeholder biến mất khi nhập)
  - Đúng: `<label for="email">Email</label><input id="email">`
- [ ] Required fields được đánh dấu rõ ràng (không chỉ bằng màu đỏ)
- [ ] Group của radio/checkbox dùng `<fieldset>` và `<legend>`

**Cách kiểm tra:** Click vào label — input có được focus không? Kiểm tra bằng axe DevTools.

**Severity nếu thiếu:** S2 (High)

---

### 3.2 Error messages
- [ ] Thông báo lỗi form mô tả cụ thể — không chỉ "Trường này không hợp lệ"
  - Sai: "Lỗi định dạng"
  - Đúng: "Email phải có định dạng example@domain.com"
- [ ] Lỗi liên kết với field cụ thể (`aria-describedby` hoặc đặt ngay dưới field)
- [ ] Screen reader thông báo lỗi khi submit (`aria-live` hoặc focus vào error summary)
- [ ] Không dùng màu làm tín hiệu lỗi duy nhất — phải có icon hoặc text kèm theo

**Severity nếu thiếu:** S2 (High)

---

### 3.3 Input hints
- [ ] Format phức tạp có hướng dẫn trước khi nhập (không chỉ sau khi lỗi)
  - Ví dụ: "Nhập ngày theo định dạng DD/MM/YYYY" hiển thị ngay dưới field
- [ ] Password requirement hiển thị trước khi user submit

**Severity nếu thiếu:** S3 (Medium)

---

## 4. Color và Contrast

### 4.1 Text contrast ratio
- [ ] Text thường (< 18pt): tối thiểu **4.5:1** contrast ratio so với background
- [ ] Text lớn (≥ 18pt hoặc 14pt bold): tối thiểu **3:1**
- [ ] Placeholder text: tối thiểu 4.5:1 (thường bị bỏ qua — placeholder hay bị quá nhạt)
- [ ] Text trên ảnh/gradient: tính contrast với vùng tối/sáng nhất phía sau

**Cách kiểm tra:** Chrome DevTools → Accessibility tab → xem contrast ratio.
Tools: WebAIM Contrast Checker, axe DevTools.

**Severity nếu dưới ngưỡng:** S2 (High) — gây khó đọc cho người thị lực kém

---

### 4.2 Không dùng màu làm thông tin duy nhất
- [ ] Link phân biệt với text thường bằng cả màu VÀ underline hoặc icon
- [ ] Status (success/error/warning) có icon + text — không chỉ màu xanh/đỏ/vàng
- [ ] Biểu đồ: các line/bar phân biệt bằng pattern/shape — không chỉ màu

**Severity nếu vi phạm:** S2 (High)

---

## 5. ARIA và Semantic HTML

### 5.1 Landmark regions
- [ ] Có `<main>`, `<nav>`, `<header>`, `<footer>` hoặc ARIA role tương đương
- [ ] Chỉ có 1 `<main>` trên trang
- [ ] Navigation (`<nav>`) có `aria-label` nếu có nhiều nav (ví dụ: "Nav chính", "Breadcrumb")

**Cách kiểm tra:** Inspect HTML structure, dùng Screen Reader (NVDA, VoiceOver) để nghe landmarks.

**Severity nếu thiếu:** S3 (Medium)

---

### 5.2 ARIA attributes
- [ ] `aria-hidden="true"` dùng đúng chỗ (icon trang trí, không phải content thật)
- [ ] `aria-expanded` update đúng trạng thái (true khi mở, false khi đóng)
- [ ] `aria-live` vùng dùng cho nội dung dynamic (thông báo, kết quả search, loading state)
- [ ] Không dùng ARIA role không phù hợp (ví dụ: `role="button"` trên `<div>` nhưng không có keyboard handler)

**Severity nếu sai:** S2 (High) — screen reader đọc sai thông tin

---

### 5.3 Page title và heading hierarchy
- [ ] Mỗi trang có `<title>` mô tả nội dung (không chỉ tên app)
  - Sai: `<title>MyApp</title>`
  - Đúng: `<title>Danh sách đơn hàng — MyApp</title>`
- [ ] Heading dùng đúng cấp bậc: H1 → H2 → H3 (không nhảy từ H1 sang H3)
- [ ] Chỉ có 1 H1 trên mỗi trang

**Severity nếu lỗi:** S3 (Medium)

---

## 6. Motion và Animation

- [ ] Animation > 5 giây có thể pause, stop, hoặc hide
- [ ] Không có nội dung nhấp nháy > 3 lần/giây (gây nguy hiểm cho người bị động kinh)
- [ ] Tôn trọng `prefers-reduced-motion`: CSS animation giảm hoặc tắt khi user chọn

**Severity nếu vi phạm:** S1 (Critical) nếu có content nhấp nháy nguy hiểm, S3 với animation thông thường

---

## 7. Responsive và Zoom

- [ ] Layout không vỡ khi zoom đến 200% trên desktop
- [ ] Không có horizontal scrollbar khi zoom 200%
- [ ] Text không bị cắt, overflow khi user tăng font-size hệ thống
- [ ] Touch target trên mobile: tối thiểu 44×44px (iOS) hoặc 48×48dp (Android)

**Severity nếu lỗi:** S2 (High) — người dùng low vision, người dùng mobile

---

## Công cụ kiểm tra nhanh

| Công cụ | Loại | Phát hiện |
|---|---|---|
| **axe DevTools** (Chrome extension) | Automated | ~57% lỗi WCAG tự động |
| **WAVE** (WebAIM) | Automated | Contrast, structure, ARIA |
| **Lighthouse** (Chrome DevTools) | Automated | Accessibility score tổng hợp |
| **NVDA** (Windows) + Chrome | Screen reader | Keyboard nav, ARIA, reading order |
| **VoiceOver** (Mac/iOS) + Safari | Screen reader | Mobile, native behavior |
| **Keyboard only** (Tab, Enter, Escape, Arrow) | Manual | Focus, trap, order |

---

## Severity mặc định theo loại lỗi

| Lỗi | Severity | WCAG Criteria |
|---|---|---|
| Focus trap không thoát được | S1 | 2.1.2 |
| Content nhấp nháy nguy hiểm | S1 | 2.3.1 |
| Input không có label | S2 | 1.3.1 |
| Focus không visible | S2 | 2.4.7 |
| Contrast < 4.5:1 | S2 | 1.4.3 |
| Alt text thiếu trên content image | S2 | 1.1.1 |
| Error message không mô tả | S2 | 3.3.1 |
| Heading hierarchy sai | S3 | 1.3.1 |
| Landmark thiếu | S3 | 1.3.1 |
| Animation không hỗ trợ reduced-motion | S3 | 2.3.3 |
