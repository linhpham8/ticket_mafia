# Exploratory Testing — Per-Page Checklist & Session Guide

> Skill 07 và Skill 15 tham chiếu file này cho exploratory testing.
> Nguồn: OWASP Testing Guide + qa/references/issue-taxonomy.md (gstack).
> Dùng khi không có test case cụ thể — kiểm tra theo trực giác và kinh nghiệm.

---

## Per-Page Exploration Checklist

Áp dụng **cho mỗi trang** trong session exploratory testing. Mục tiêu: < 5 phút/trang cho Quick tier, không giới hạn cho Exhaustive.

### 1. Visual Scan
- [ ] Chụp screenshot toàn trang (annotate nếu có tool hỗ trợ)
- [ ] Layout có bị vỡ không? Phần tử chồng lên nhau? Text bị cắt?
- [ ] Hình ảnh load đủ không? Không có broken image icon?
- [ ] Nội dung có căn chỉnh theo grid không? Spacing đều?
- [ ] Màu sắc, font có nhất quán với các trang khác?

### 2. Interactive Elements
- [ ] Click mọi button — có phản hồi không? Đúng action không?
- [ ] Click mọi link — đến đúng đích? Không phải 404?
- [ ] Hover state hiển thị đúng (cursor thay đổi, tooltip xuất hiện)?
- [ ] Dropdown, accordion, tab — toggle đúng không?
- [ ] Icon button — có tooltip hoặc aria-label giải thích không?

### 3. Forms
- [ ] Submit form rỗng — validation xuất hiện đúng không?
- [ ] Submit form với data hợp lệ — xử lý thành công?
- [ ] Submit form với data biên (chuỗi rất dài, ký tự đặc biệt, số âm)?
- [ ] Validation message rõ ràng, chỉ đúng field lỗi?
- [ ] Sau submit thành công — có thông báo xác nhận không?
- [ ] Tab order trong form hợp lý (trên-xuống, trái-phải)?

### 4. Navigation
- [ ] Breadcrumb phản ánh đúng vị trí hiện tại?
- [ ] Nút Back của browser hoạt động đúng?
- [ ] Deep link (paste URL thẳng) vào đúng trang?
- [ ] Các link trong menu/sidebar đến đúng đích?
- [ ] Không có dead-end (trang không có đường thoát ra)?

### 5. States
- [ ] **Empty state:** Khi không có data — hiển thị gì? Có hướng dẫn không?
- [ ] **Loading state:** Khi đang tải — có spinner/skeleton không?
- [ ] **Error state:** Khi API lỗi — hiển thị thông báo gì?
- [ ] **Full/overflow state:** Khi có quá nhiều data — pagination? Scroll? Truncate?
- [ ] Refresh trang — data có giữ không? Form có bị reset không?

### 6. Console Check
- [ ] Mở DevTools → Console trước khi tương tác
- [ ] Thực hiện các hành động trên trang
- [ ] Kiểm tra: có JavaScript error (màu đỏ) mới xuất hiện không?
- [ ] Kiểm tra Network tab: có request 4xx/5xx không?
- [ ] Ghi nhận cả warning quan trọng (không phải chỉ error)

### 7. Responsiveness (nếu relevant)
- [ ] DevTools → Toggle Device Toolbar → Mobile (375px)
- [ ] Layout vẫn dùng được không? Không có horizontal scrollbar?
- [ ] Touch target đủ lớn (≥ 44px)?
- [ ] Text không bị chồng lên nhau?
- [ ] Navigation mobile (hamburger menu) hoạt động đúng?

---

## Testing Tiers

### Quick Tier (~15–30 phút)
**Scope:** Chỉ các luồng Critical và High — những gì chặn core workflow.

- Số trang cover: 3–5 trang chính
- Checklist: chỉ mục 2 (Interactive) và 6 (Console)
- Bug report: chỉ S1 và S2
- Dùng khi: hotfix review, pre-deploy smoke, time-boxed check

### Standard Tier (~1–2 giờ)
**Scope:** Critical + High + Medium — toàn bộ tính năng chính.

- Số trang cover: tất cả trang trong sprint scope
- Checklist: mục 1–6 đầy đủ
- Bug report: S1, S2, S3
- Dùng khi: Sprint review, regression test thông thường

### Exhaustive Tier (~3+ giờ)
**Scope:** Toàn bộ ứng dụng — bao gồm edge case và cosmetic.

- Số trang cover: toàn bộ app + edge case + luồng hiếm gặp
- Checklist: mục 1–7 đầy đủ + accessibility + security cơ bản
- Bug report: S1, S2, S3, S4
- Dùng khi: Pre-release lớn, sau re-design toàn bộ, UAT prep

---

## Session-Based Exploratory Testing (SBET)

Thay vì test tuỳ hứng, dùng **session có mục tiêu** (charter):

### Cấu trúc session

```
Charter: [Mục tiêu — 1 câu]
Scope: [Tính năng hoặc luồng cụ thể]
Thời gian: [30 / 60 / 90 phút]
Tester: [Tên]

--- Trong session ---
Ghi nhanh:
  + Phát hiện: [vấn đề]
  ? Câu hỏi: [điều cần confirm]
  i Ý tưởng: [test case bổ sung]

--- Sau session ---
Bug đã tìm: [N]
Câu hỏi chưa giải đáp: [N]
Vùng chưa test: [Mô tả]
```

### Ví dụ charter hiệu quả

- "Kiểm tra luồng thanh toán từ góc nhìn user lần đầu mua hàng — mục tiêu phát hiện điểm gây confusion"
- "Test tất cả trường hợp error trong form đăng ký — nhập data biên, network lỗi, trùng email"
- "Explore trang quản lý user với quyền admin — tìm hành động không có confirmation dialog"

### Charter KHÔNG hiệu quả

- "Test toàn bộ app" — quá rộng, không có focus
- "Tìm bug" — không có mục tiêu
- "Kiểm tra tính năng mới" — không rõ tính năng nào, không rõ "kiểm tra" theo tiêu chí gì

---

## Links Checking

Links là category riêng trong Health Score (trọng số 10%). Kiểm tra:

| Loại link | Cách kiểm tra | Severity nếu lỗi |
|---|---|---|
| Link nội bộ (trong app) | Click, kiểm tra URL đích đúng | S2 nếu 404, S3 nếu sai đích |
| Link ngoài (external) | Hover xem href, mở tab mới kiểm tra | S3 nếu 404 |
| Link trong email/PDF | Kiểm tra trong môi trường nhận | S2 nếu 404 |
| Deep link (share URL) | Paste URL vào tab mới | S2 nếu không resolve |
| Anchor link (#section) | Click, có scroll đến đúng section không | S3 |
| Link với `target="_blank"` | Có `rel="noopener noreferrer"` không (security) | S3 |

**Tool hỗ trợ:** Chrome extension "Link Checker" hoặc dùng crawler đơn giản cho ứng dụng lớn.

---

## Before/After Evidence

Khi phát hiện bug trong exploratory testing, ghi nhận evidence đủ để:
1. Dev reproduce độc lập (không cần hỏi lại)
2. So sánh sau khi fix để verify

### Template ghi nhận

```
Bug: [ID] — [Tiêu đề ngắn]

Before (trạng thái lỗi):
  URL: [URL cụ thể]
  Hành động: [Làm gì]
  Kết quả: [Thấy gì — sai]
  Screenshot: [file/link]

After (trạng thái mong đợi):
  Kết quả mong đợi: [Nên thấy gì]
  Screenshot reference: [Nếu có — design / trang khác hoạt động đúng]

Console output tại thời điểm lỗi: [Nếu relevant]
```
