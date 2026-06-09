---
id: EP-NNN
title: {{EPIC_TITLE}}
status: DRAFT
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

<!-- ID: EP-NNN -->
# EP-NNN — {{EPIC_TITLE}}

<!-- This file is ONE epic = ONE file. Stores epic info + all FRs + all User Stories + all AC for this epic.
     File name = `EP-NNN-{slug}.md` where slug derives from title (lowercase kebab, alnum-only, max 40 chars,
     strip diacritics for Vietnamese: vd "Thanh toán" → "thanh-toan"). Slug set once at create; rename title
     later does NOT auto-rename file (use `git mv` manually if needed). -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Every mergeable unit (this epic, each FR, each US, each AC) is preceded by an HTML-comment anchor on
     its own line, e.g.:
         <!-- ID: FR-101 -->
         **FR-101 — Cart operations**: ...
     Atomic IDs (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type {EP|FR|US|AC}`.
     Strict format `[A-Z]+(?:-[A-Z]+)*-\d{3,}` (multi-segment, zero-padded ≥3 digits) — same as the canonical convention.
     The `id: EP-NNN` frontmatter field above is filled with a real EP ID in both modes (not left as `EP-NNN`).
     (Guided seal only) The anchors also let apply_proposal.py merge individual items at sprint seal — Freedom has no seal but still issues the IDs above and keeps the anchors. -->

## Epic Overview

**Priority**: Must / Should / Could / Won't (MoSCoW)
**Affected personas**: <!-- vd `PERSONA-001 (Khách hàng cá nhân)`, `PERSONA-003 (Quản trị viên)` — link by ID from `/docs/product/personas.md` -->
**KPI contribution** *(optional)*: <!-- vd "Conversion Rate (PRD §3.1)". Không bắt buộc; nhưng nếu epic không link KPI → đặt câu hỏi tại sao làm -->

### Bối cảnh (Tại sao Epic này tồn tại?)

<!-- 4W để team Engineering hiểu context trước khi estimate. -->

- **Bối cảnh hiện tại**: <!-- VD: Tỷ lệ bỏ giỏ hàng đang ở mức 65%, cao hơn benchmark ngành 20%. -->
- **Mục tiêu cụ thể**: <!-- VD: Giảm tỷ lệ bỏ giỏ hàng xuống < 45% trong vòng 3 tháng. -->
- **Đối tượng hưởng lợi**: <!-- VD: Người dùng Gen Z, chưa có thẻ tín dụng, thu nhập 5–15 triệu/tháng. -->
- **Tính cấp thiết**: <!-- Tại sao làm ngay bây giờ? VD: Trước mùa Black Friday T11, cạnh tranh đang tung BNPL. -->

### Vấn đề cần giải quyết

- <!-- VD: Người dùng thiếu hụt tài chính tức thời khi mua món đồ giá trị cao. -->
- <!-- VD: Thủ tục trả góp qua ngân hàng hiện tại quá chậm và rườm rà (mất 2–3 ngày). -->

### Giá trị mang lại

**Cho người dùng**:
- <!-- VD: Sở hữu sản phẩm ngay, trả tiền sau theo kỳ hạn linh hoạt. -->
- <!-- VD: Trải nghiệm mượt mà, duyệt hồ sơ trong vài phút. -->

**Cho tổ chức**:
- <!-- VD: Tăng tỷ lệ chuyển đổi tại bước thanh toán. -->
- <!-- VD: Mở rộng tệp khách hàng chưa có thẻ tín dụng. -->

### Tiêu chí nghiệm thu cấp Epic

<!-- Điều kiện DONE ở mức Epic — không phải AC từng story. Epic chỉ đóng khi TẤT CẢ tiêu chí này đạt. -->

- [ ] <!-- VD: Tính năng hoạt động ổn định trên iOS, Android và Web. -->
- [ ] <!-- VD: Thời gian phản hồi từ đối tác tài chính không quá 3 giây (P95). -->
- [ ] <!-- VD: Hệ thống ghi nhận chính xác doanh thu từ nguồn này trong báo cáo. -->

### Phụ thuộc & Ghi chú

<!-- Liên kết tới epic khác, NFR, ADR, ràng buộc kỹ thuật. -->

| Loại | Item | Ghi chú |
|---|---|---|
| Depends-on | <!-- EP-XXX, ADR-NNN --> | |
| Respects (NFR) | <!-- NFR-001, NFR-005 --> | |
| Rủi ro | | |

### Product Traceability Map

<!-- BẮT BUỘC theo `PROD-4`: map dễ đọc từ Epic -> FR -> US.
     Mỗi FR thuộc epic này phải có 1 dòng. Must Have FR phải map tới ít nhất 1 Must Have US.
     Accepted gap chỉ dùng cho non-Must / deferred FR, kèm reason + owner.
     LƯU Ý: file epic KHÔNG nhận auto `## Index` lúc seal (khác 15 file LT gốc) — chính map
     này là "index" của epic. Catalog cross-epic nằm ở Epic Index của prd.md (auto-generated). -->

| Epic | FR | Related US | Priority / Coverage | Notes |
|---|---|---|---|---|
| EP-NNN | FR-NNN | US-NNN, US-NNN | Must / covered | |
| EP-NNN | FR-NNN | <!-- US-NNN hoặc `accepted gap — reason + owner` cho non-Must/deferred --> | Should / gap | |

---

## Functional Requirements (FRs)

<!-- Liệt kê tất cả FR thuộc epic này. Mỗi FR là 1 anchored block. -->
<!-- FR mô tả WHAT system làm. Câu mẫu: "Hệ thống PHẢI X". -->
<!-- Stable: đổi FR = breaking. Reframe (giữ ID, đổi description) qua proposal `## Updated`. -->

<!-- ID: FR-NNN -->
**FR-NNN — {{Tên ngắn của capability}}**

<!-- VD: Hỗ trợ add/remove/update item trong giỏ hàng. -->

- Phạm vi: <!-- VD: User thao tác trên giao diện cart, hệ thống tính lại tổng tiền tức thời. -->
- Trace:
  - Covered by US: <!-- vd `US-201, US-202`; phải khớp Product Traceability Map -->
  - Verifies KPI: <!-- vd "Conversion Rate" — link tới prd.md exec section -->
- Ghi chú: <!-- caveats, edge cases, dependencies; ghi `—` nếu không có -->

<!-- ID: FR-NNN -->
**FR-NNN — {{Tên capability khác}}**

<!-- Description / scope / trace như block trên. -->

<!-- Lặp lại block ở trên cho mỗi FR. Tất cả FR cùng level (không phân MoSCoW nội bộ epic — MoSCoW ở prd.md cấp epic). -->

---

## User Stories

<!-- Mỗi US là 1 anchored block. US covers 1+ FR. AC verifies US (không gắn FR trực tiếp). -->
<!-- Definition of Ready cho 1 story:
       • Story có thể deliver độc lập — không cần story khác mới dùng được
       • Tất cả AC đã viết, testable, không còn câu hỏi mở
       • Story đủ nhỏ để hoàn thành trong 1 sprint (5 ngày)
       • Trace FR / NFR / BR đầy đủ -->

<!-- ID: US-NNN -->
### US-NNN: [Tên ngắn gọn của story]

> Với tư cách là **[persona/role]**,
> Tôi muốn **[khả năng / hành động]**,
> Để **[giá trị kinh doanh / lý do thực sự]**.

**Priority**
Must / Should / Could

**Persona**
<!-- BẮT BUỘC cho Must — vd `PERSONA-001 (Khách hàng cá nhân)`. -->

**Covers FR**
<!-- FR-NNN, FR-NNN — link tới FR trong epic này hoặc cross-epic -->

**Respects NFR**
<!-- NFR-NNN, NFR-NNN — link tới `/docs/architecture/nfr.md` -->

**Respects BR**
<!-- BR-NNN — link tới `/docs/product/prd.md` Business Rules section -->

**Design Reference**
<!-- SCREEN-NNN, DS-COMP-NNN — link tới `/docs/design/design-system.md`. Ghi "Chưa có design" nếu chưa tồn tại -->

**Scope**
<!-- BẮT BUỘC — IN: hành vi/trạng thái/dữ liệu nào nằm trong story này. -->

**Out of Scope**
<!-- BẮT BUỘC — KHÔNG làm gì trong story này. VD: "Filter theo trạng thái → US-NNN; Export CSV → US-NNN". -->

**Testability**
<!-- BẮT BUỘC cho Must — verify như thế nào: manual/auto, signal nào QA quan sát, dữ liệu/điều kiện cần. -->

#### Acceptance Criteria

<!-- AC mô tả BƯỚC HÀNH VI quan sát được từ user/hệ thống. KHÔNG ghi chi tiết kỹ thuật (HTTP status, JSON contract, query params) — đó thuộc Test Cases. -->

<!-- ID: AC-NNN -->
**AC-NNN (Happy Path)**
<!-- VD: Người dùng đăng nhập thành công với email và mật khẩu hợp lệ → chuyển vào dashboard và thấy toast chào mừng hiển thị 3 giây. -->

<!-- ID: AC-NNN -->
**AC-NNN**
<!-- Kịch bản bổ sung. -->

<!-- ID: AC-NNN -->
**AC-NNN (Error/Edge)**
<!-- VD: Nhập sai mật khẩu 3 lần liên tiếp → tài khoản bị khóa tạm 15 phút. Hiển thị: "Tài khoản bị khóa tạm thời. Vui lòng thử lại sau 15 phút hoặc reset mật khẩu." Button "Đăng nhập" bị disabled trong thời gian lockout. -->

> **Assumption**: <!-- Giả định đằng sau story này. VD: "User đã có tài khoản. Nếu cần luồng đăng ký → scope sang US-NNN." Nếu chưa rõ → ghi "TBD — cần xác nhận với [stakeholder]". -->
> **Validate**: <!-- Ai xác nhận assumption này, và khi nào? VD: "PO confirm trước khi story vào sprint." -->
> **Change trigger**: <!-- Điều kiện nào thì cần revisit story này? VD: "Nếu thêm SSO / OAuth → revisit AC-NNN qua `feedback:`." -->

<!-- ID: US-NNN -->
### US-NNN: [Story thứ 2]

<!-- Lặp lại block ở trên cho mỗi user story. Mỗi US có AC blocks riêng. -->

---

## Edge cases & câu hỏi mở

<!-- Edge cases KHÔNG gắn 1 story cụ thể, hoặc apply nhiều stories cùng lúc. Edge case gắn với 1 story thì để trong AC của story đó. -->

| ID | Kịch bản | Hành vi mong đợi | Story / FR liên quan | Đã xử lý? |
|---|---|---|---|---|
| | | | | |

| # | Câu hỏi | Owner | Story / FR liên quan | Deadline | Trạng thái |
|---|---|---|---|---|---|
| | | | | | |

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `PROD-1`, `PROD-4`
- [ ] Frontmatter `id: EP-NNN` khớp với file name `EP-NNN-{slug}.md` và anchor `<!-- ID: EP-NNN -->` ở đầu file
- [ ] Product Traceability Map tồn tại và map đủ `EP -> FR -> Related US`; mọi FR trong epic có 1 dòng, Must Have FR có ít nhất 1 Must Have US
- [ ] Mỗi FR có anchor `<!-- ID: FR-NNN -->` ngay trên bold-name line; ID unique trong toàn project (qua `get_next_id.py`)
- [ ] Mỗi US có anchor `<!-- ID: US-NNN -->` ngay trên H3 heading; ID unique
- [ ] Mỗi AC có anchor `<!-- ID: AC-NNN -->` ngay trên bold-name line; ID unique
- [ ] Mỗi Must US có đủ Story Readiness: Persona, Covers FR, AC, Scope, Testability
- [ ] Mỗi US có thể deliver và test độc lập
- [ ] AC mô tả BƯỚC HÀNH VI user-facing, có exact message text + UI state — KHÔNG ghi HTTP status / response body / mã lỗi kỹ thuật
- [ ] Mỗi US có ít nhất 1 AC xử lý lỗi hoặc edge case
- [ ] Mỗi US có Assumption block với Validate và Change trigger — hoặc "TBD" kèm owner
- [ ] Tất cả persona refs (`PERSONA-NNN`) tồn tại trong `/docs/product/personas.md`
- [ ] Tất cả NFR refs (`NFR-NNN`) tồn tại trong `/docs/architecture/nfr.md`
- [ ] Tất cả BR refs (`BR-NNN`) tồn tại trong `/docs/product/prd.md`
- [ ] Tất cả design refs (`SCREEN-NNN`, `DS-COMP-NNN`) tồn tại trong `/docs/design/design-system.md` — hoặc ghi "Chưa có design"
- [ ] QA trace từng US-NNN sang `/docs/testing/test-cases.md` qua `TC-NNN` `Verifies: US-NNN`
- [ ] Đã chạy `validate user story` và clear toàn bộ blocker trước khi đề xuất `approve product`
