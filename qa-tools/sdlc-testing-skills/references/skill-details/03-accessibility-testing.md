# Detailed Procedure: 03-accessibility-testing

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## Kiem tra truoc khi bao DONE

> **L2 - QA Lead review bat buoc.** Report chua duoc gui stakeholder cho den khi nhan Approved. Xem muc Sign-off cuoi file.

- [ ] WCAG 2.1 AA scope da cover (automated + manual)
- [ ] Lighthouse score da do va so voi target
- [ ] Top 3 action items ro rang
- [ ] Sign-off L2 da emit
- [ ] Append execution record vao governance/audit-log.md
- [ ] Cap nhat project/session-state.yaml -> last_execution, pending_sign_offs

---







## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| URL môi trường test | ✅ |
| Danh sách trang / luồng cần kiểm tra | ✅ |
| Tier kiểm tra (Quick / Standard / Exhaustive) | ✅ |
| Tiêu chuẩn áp dụng (mặc định: WCAG 2.1 AA) | Khuyến nghị |
| Đối tượng người dùng đặc biệt (nếu biết) | Khuyến nghị |

Nếu project có `qa-config.yaml` → đọc trước:
- `accessibility.required` → nếu `false`, nhắc user xác nhận trước khi tiếp tục
- `accessibility.wcag_level` → AA hoặc AAA (mặc định AA)
- `accessibility.lighthouse_score_min` → ngưỡng score tối thiểu
- `environments.staging.url` → URL test
- `scope.exploratory_tier` → tier áp dụng (Quick/Standard/Exhaustive)

Thiếu thông tin bắt buộc → ghi `[Cần bổ sung]`, hỏi lại. Không đoán mò.

---

## Bước 1 — Chạy automated scan trước

Automated tools phát hiện được ~30–57% lỗi WCAG. Chạy trước để có bức tranh tổng quan nhanh.

### Công cụ ưu tiên

| Công cụ | Cách chạy | Output |
|---|---|---|
| **axe DevTools** | Chrome extension → Analyze page | Danh sách lỗi có WCAG reference |
| **Lighthouse** | Chrome DevTools → Lighthouse → Accessibility | Score 0–100 + issues |
| **WAVE** | wave.webaim.org hoặc extension | Visual overlay lỗi trên trang |

### Ghi nhận kết quả automated

- Lighthouse Accessibility Score: {N}/100
- Số lỗi axe: Critical [{N}] / Serious [{N}] / Moderate [{N}] / Minor [{N}]
- Lỗi phổ biến nhất: {liệt kê top 3}

> Automated scan là **điểm bắt đầu**, không phải điểm kết thúc. Luôn manual test sau.

---

## Bước 2 — Keyboard navigation test

Đóng chuột. Chỉ dùng bàn phím. Đọc `../../references/accessibility-checklist.md` mục 2.

**Quy trình:**
1. Mở trang, nhấn Tab — quan sát focus xuất hiện ở đâu đầu tiên
2. Tab qua toàn bộ trang, ghi nhận:
   - Focus indicator có visible không?
   - Thứ tự Tab có logical không?
   - Có bị mắc kẹt ở đâu không?
3. Với mỗi interactive element: Enter/Space để activate, kiểm tra hoạt động đúng
4. Với modal/dialog: kiểm tra focus trap (Tab không thoát ra ngoài), Escape đóng được
5. Với dropdown/menu: Arrow keys navigate, Escape đóng, Enter chọn

**Ghi nhận lỗi ngay khi phát hiện** — không để đến cuối session.

---

## Bước 3 — Form accessibility

Đọc `../../references/accessibility-checklist.md` mục 3.

Với mỗi form trên trang:

- [ ] Click vào label text — input có được focus không? (kiểm tra `for`/`id` liên kết)
- [ ] Các field bắt buộc được đánh dấu không phải chỉ bằng màu
- [ ] Submit rỗng — error message xuất hiện gần field lỗi, mô tả cụ thể
- [ ] Error có thể đọc bằng screen reader (`aria-describedby` hoặc `aria-live`)
- [ ] Placeholder không thay thế label (label phải luôn visible)

---

## Bước 4 — Color contrast

Đọc `../../references/accessibility-checklist.md` mục 4.

**Ngưỡng WCAG 2.1 AA:**
- Text thường: tối thiểu **4.5:1**
- Text lớn (≥ 18pt / 14pt bold): tối thiểu **3:1**
- UI components (border của input, icon): tối thiểu **3:1**

**Cách đo:**
1. Chrome DevTools → chọn element → Accessibility tab → Contrast ratio
2. Hoặc: WebAIM Contrast Checker — nhập hex màu foreground/background

Ghi nhận: element, màu foreground, màu background, tỷ lệ đo được, tỷ lệ yêu cầu.

---

## Bước 5 — Screen reader test (nếu Exhaustive tier)

Đọc `../../references/accessibility-checklist.md` mục 5.

**Môi trường khuyến nghị:**
- Windows: NVDA (free) + Chrome
- Mac: VoiceOver (built-in) + Safari

**Quy trình cơ bản:**
1. Bật screen reader, mở trang
2. Nghe title của trang — mô tả đúng nội dung không?
3. Dùng screen reader shortcut để nghe danh sách heading — có hierarchy hợp lý không?
4. Navigate qua landmarks (nav, main, footer)
5. Tương tác với form — nghe label của từng field trước khi nhập
6. Submit form — thông báo lỗi có được đọc không?

---

## Bước 6 — Per-page checklist

Với mỗi trang trong scope, chạy checklist từ `../../references/exploratory-checklist.md` — tập trung vào mục 1 (Visual Scan) và mục 2 (Interactive Elements) để phát hiện lỗi visual accessibility.

---

## Format output — Accessibility Test Report

```markdown




| Trường | Giá trị |
|---|---|
| **Ngày test** | [dd/mm/yyyy] |
| **Tiêu chuẩn** | WCAG 2.1 Level AA |
| **Tier** | Quick / Standard / Exhaustive |
| **Trang đã test** | [N] trang |
| **Tester** | [Tên] |
| **Công cụ** | axe DevTools, Lighthouse, Keyboard manual |

---

## Tổng quan

| Chỉ số | Kết quả |
|---|---|
| Lighthouse Accessibility Score | [N]/100 |
| axe: Critical | [N] |
| axe: Serious | [N] |
| axe: Moderate | [N] |
| axe: Minor | [N] |
| Lỗi manual (không phát hiện bởi automated) | [N] |

**Mức độ tổng thể:** 🔴 Cần cải thiện đáng kể / 🟡 Có lỗi cần fix / 🟢 Đạt cơ bản

---

## Danh sách lỗi

### A11Y-001: [Tiêu đề ngắn gọn]

| Trường | Giá trị |
|---|---|
| **WCAG Criteria** | [1.1.1 / 1.4.3 / 2.1.1 / ...] |
| **Severity** | S1 / S2 / S3 |
| **Trang** | [URL] |
| **Element** | [CSS selector hoặc mô tả element] |
| **Trạng thái** | Open / Fixed |

**Vấn đề:** [Thực tế là gì — vi phạm WCAG như thế nào]

**Ảnh hưởng:** [Người dùng nào bị ảnh hưởng — người mù, người dùng bàn phím, người thị lực kém]

**Khuyến nghị fix:** [Giải pháp cụ thể — thêm `alt`, tăng contrast từ X lên Y, thêm `aria-label`]

---

## Kết quả Keyboard Navigation

| Trang | Tab order | Focus visible | Keyboard trap | Kết quả |
|---|---|---|---|---|
| [Trang] | ✅ / ❌ | ✅ / ❌ | Không có / Có tại [element] | ✅ Pass / ❌ Fail |

---

## Kết quả Contrast

| Element | Màu text | Màu BG | Tỷ lệ đo | Yêu cầu | Đạt? |
|---|---|---|---|---|---|
| Body text | #[hex] | #[hex] | [N]:1 | 4.5:1 | ✅ / ❌ |
| Placeholder | #[hex] | #[hex] | [N]:1 | 4.5:1 | ✅ / ❌ |

---

## Kết luận

**Có thể release không?**
- ❌ Không — Còn [N] lỗi S1 (keyboard trap, nguy hiểm cho người dùng)
- ⚠️ Có điều kiện — S1 đã fix, còn [N] lỗi S2 (contrast, label) cần fix trong sprint tiếp
- ✅ Có — Đạt WCAG 2.1 AA cơ bản, Lighthouse score ≥ [N]

**Top 3 hành động ưu tiên:**
1. [Fix cụ thể]
2. [Fix cụ thể]
3. [Fix cụ thể]
```

---

**Lưu file vào:** `output_paths.reports.accessibility` từ qa-config (default: `testing-output/reports/accessibility/`)
→ `reports/accessibility-report-{project.sprint}.md`

## Sign-off Request (L2)



Sau khi nhan Approved: cap nhat project/session-state.yaml, xoa item khoi pending_sign_offs.

---

## Completion Status

- **DONE** — Automated scan + manual test hoàn thành, report đủ WCAG reference
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng: {Một số trang không test được / Screen reader test bỏ qua / Score thấp hơn target}
- **BLOCKED** — Không thể test do: {Không có tool / Trang yêu cầu auth không có account / Môi trường không ổn định}
- **NEEDS_CONTEXT** — Cần bổ sung: {Danh sách trang cần test / Tier áp dụng / Tiêu chuẩn WCAG level}


