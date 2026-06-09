# Báo Cáo Kiểm Thử: {TÊN_DỰ_ÁN}

| Trường | Giá trị |
|---|---|
| **Dự án** | {Tên dự án} |
| **Sprint / Phiên bản** | {Sprint X / v1.0.0} |
| **Ngày báo cáo** | {dd/mm/yyyy} |
| **Môi trường** | {Staging / UAT / Production} |
| **URL** | {https://...} |
| **Người thực hiện** | {Tên QC} |
| **Phạm vi kiểm thử** | {Module / luồng được test} |
| **Thời gian thực hiện** | {X ngày / X giờ} |
| **Tổng TC thực hiện** | {N} |
| **Tham chiếu Test Plan** | {Tên file test plan} |

---

## Health Score: {ĐIỂM}/100

> Health Score phản ánh chất lượng tổng thể của ứng dụng tại thời điểm test.
> Công thức: Tổng có trọng số của 8 hạng mục (mỗi hạng mục 0–100 điểm).

| Hạng mục | Trọng số | Điểm | Điểm có trọng số |
|---|---:|---:|---:|
| Console / Errors | 15% | {0-100} | {N} |
| Functional | 20% | {0-100} | {N} |
| UX | 15% | {0-100} | {N} |
| Accessibility | 15% | {0-100} | {N} |
| Visual / UI | 10% | {0-100} | {N} |
| Performance | 10% | {0-100} | {N} |
| Content | 5% | {0-100} | {N} |
| Links | 10% | {0-100} | {N} |
| **Tổng** | **100%** | — | **{ĐIỂM}** |

> **Quy tắc hạng mục Links:** Nếu sprint không có test link checking → điền điểm Links = 100 (không trừ điểm). Health Score luôn tính trên thang /100.

**Quy tắc trừ điểm theo severity (mỗi hạng mục bắt đầu từ 100):**
- Bug Critical (S1): −25 điểm
- Bug High (S2): −15 điểm
- Bug Medium (S3): −8 điểm
- Bug Low (S4): −3 điểm
- Minimum mỗi hạng mục: 0 điểm

---

## 3 Vấn Đề Ưu Tiên Xử Lý

1. **{BUG-NNN}: {tiêu đề}** — {mô tả 1 dòng, impact}
2. **{BUG-NNN}: {tiêu đề}** — {mô tả 1 dòng, impact}
3. **{BUG-NNN}: {tiêu đề}** — {mô tả 1 dòng, impact}

---

## Tổng Hợp Kết Quả

| Trạng thái | Số TC | Tỷ lệ |
|---|---:|---:|
| Pass | {N} | {x}% |
| Fail | {N} | {x}% |
| Blocked | {N} | {x}% |
| Not Run | {N} | {x}% |
| **Tổng** | **{N}** | |

**Pass rate:** {x}% | **Exit criteria:** {x}% | **Trạng thái:** ✅ Đạt / ❌ Chưa đạt

---

## Phân Bổ Bug Theo Severity & Category

### Theo Severity

| Severity | Số lượng | Đã fix | Còn open |
|---|---:|---:|---:|
| S1 — Critical | {N} | {N} | {N} |
| S2 — High | {N} | {N} | {N} |
| S3 — Medium | {N} | {N} | {N} |
| S4 — Low | {N} | {N} | {N} |
| **Tổng** | **{N}** | **{N}** | **{N}** |

### Theo Category

| Category | Số lượng |
|---|---:|
| Functional | {N} |
| Visual / UI | {N} |
| UX | {N} |
| Console / Errors | {N} |
| Performance | {N} |
| Accessibility | {N} |
| Content | {N} |

---

## Danh Sách Bug

### BUG-001: {Tiêu đề ngắn gọn}

| Trường | Giá trị |
|---|---|
| **Severity** | S1 / S2 / S3 / S4 |
| **Priority** | P1 / P2 / P3 / P4 |
| **Category** | Functional / Visual / UX / Content / Performance / Console / Accessibility |
| **URL** | {URL trang xảy ra bug} |
| **Trạng thái** | Open / Fixed / Verified / Deferred |
| **Assignee** | {Tên Dev / Để trống} |

**Mô tả:** {Thực tế là gì — Expected là gì.}

**Repro Steps:**

1. Truy cập {URL}
2. {Hành động}
3. **Quan sát:** {Điều gì xảy ra sai}

**Screenshot/Evidence:** {Đường dẫn file hoặc link}

---

## Console Health

| Lỗi | Số lần | Trang đầu tiên xuất hiện |
|---|---:|---|
| {Nội dung lỗi console} | {N} | {URL} |

---

## Blocker & Rủi Ro

| Loại | Mô tả | Tác động | Đề xuất xử lý |
|---|---|---|---|
| Blocker | {Bug / môi trường / data chặn test} | {N TC bị ảnh hưởng} | {Hành động cụ thể} |
| Rủi ro | {Vấn đề tiềm ẩn} | {Impact nếu xảy ra} | {Mitigate} |

---

## Retest Scope

| TC cần retest | Bug liên quan | Lý do | Ưu tiên |
|---|---|---|---|
| {TC-XXX} | {BUG-NNN} | {Bug đã fix / Môi trường ổn định} | P1 / P2 / P3 |

---

## Ship Readiness

| Chỉ số | Giá trị | Mục tiêu | Đạt? |
|---|---|---|---|
| Health Score | {N}/100 | ≥ {N}/100 | ✅ / ❌ |
| Pass rate | {x}% | ≥ {x}% | ✅ / ❌ |
| S1 còn open | {N} | = 0 | ✅ / ❌ |
| S2 còn open | {N} | ≤ {N} | ✅ / ❌ |
| TC chưa chạy | {N} | = 0 | ✅ / ❌ |

**Khuyến nghị:** ✅ Có thể release / ⚠️ Release có điều kiện ({điều kiện}) / ❌ Chưa sẵn sàng release

**Lý do:** {1-2 câu tóm tắt trạng thái và rủi ro chính}

---

## Regression So Với Baseline (nếu có)

| Chỉ số | Baseline | Hiện tại | Delta |
|---|---|---|---|
| Health Score | {N} | {N} | {+/-N} |
| Tổng bug | {N} | {N} | {+/-N} |
| Pass rate | {x}% | {x}% | {+/-x}% |

**Bug đã fix từ baseline:** {danh sách}
**Bug mới phát sinh:** {danh sách}

---

## Completion Status

- **DONE** — Hoàn thành toàn bộ scope, có đủ bằng chứng
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng có vấn đề cần lưu ý: {liệt kê}
- **BLOCKED** — Dừng do: {lý do} | Đã thử: {hành động} | Khuyến nghị: {tiếp theo}
- **NEEDS_CONTEXT** — Cần thêm: {thông tin còn thiếu}
