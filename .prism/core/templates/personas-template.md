---
status: DRAFT
version: v1
sprint: 1
phase: product
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# User Personas — {{PROJECT_NAME}}

<!-- This file is the Living Truth root for personas. Each persona is a mergeable anchored block. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each PERSONA-NNN block in §2 MUST be preceded by `<!-- ID: PERSONA-NNN -->` on its own line.
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type PERSONA`
     Strict format: `PERSONA-\d{3,}` (zero-padded ≥3 digits).
     (Guided seal only) The anchor also lets `apply_proposal.py` merge this block at sprint seal — Freedom has no seal but still issues the ID above and keeps the anchor. -->

<!-- PRISM:LT-SKELETON-END -->

## 1. Persona Summary

<!-- Bảng index. Mỗi row đối ứng với 1 PERSONA-NNN block ở §2. -->

| Persona ID | Persona | Role | Priority | Primary Goals | Key Risks |
|---|---------|------|----------|---------------|-----------|
| PERSONA-NNN | | | Primary / Secondary | | |

## 2. Detailed Personas

<!-- ID: PERSONA-NNN -->
### PERSONA-NNN: {{PERSONA_NAME}}

- **Role**: <!-- Chức vụ, công ty, industry. VD: "Senior Accountant tại SME 50–200 nhân viên, ngành bán lẻ" -->

- **Tech Level**: <!-- Đánh giá theo tiêu chí cụ thể, không chỉ "High/Medium/Low":
  - **High**: Dùng thành thạo nhiều SaaS tools, tự tìm hiểu tính năng mới không cần hướng dẫn, biết shortcuts
  - **Medium**: Dùng được các tính năng chính, cần hướng dẫn cho tính năng mới, đôi khi cần support
  - **Low**: Chủ yếu làm theo hướng dẫn có sẵn, ngại tự khám phá, thường nhờ đồng nghiệp hoặc hotline --> 
  Tiêu chí cho persona này: <!-- Mô tả cụ thể. VD: "Dùng Excel thành thạo, dùng ERP nhưng chỉ dùng 20% tính năng, không tự cài phần mềm" -->

- **Mindset / Quote**: <!-- 1–2 câu nói thể hiện mental model và frustration threshold. VD: "Tôi không cần hiểu bên trong hoạt động thế nào — tôi chỉ cần nó chạy đúng và nhanh." Nếu chưa có user research → ghi "TBD — cần interview" -->

- **Goals** *(liệt kê theo thứ tự ưu tiên, tối thiểu 3 goals cụ thể)*:
  1. <!-- VD: Hoàn thành báo cáo tháng trước ngày 5 — không phải "muốn làm việc hiệu quả" -->
  2.
  3.

- **Pain Points** *(liệt kê tối thiểu 3, cụ thể)*:
  1. <!-- VD: Mất 2–3 giờ/tuần copy data từ hệ thống cũ sang Excel để làm báo cáo -->
  2.
  3.

- **Usage Context**:
  - **Tần suất**: <!-- VD: "Hàng ngày, 2–3 lần/ngày trong giờ hành chính" -->
  - **Môi trường**: <!-- VD: "Văn phòng, bàn làm việc cố định, màn hình 24 inch" hoặc "Di chuyển nhiều, chủ yếu dùng smartphone 5–6 inch" -->
  - **Workflow context**: <!-- VD: "Dùng app trong lúc đang họp với khách hàng" hoặc "Dùng cuối ngày để tổng kết" -->
  - **Device ưu tiên**: <!-- VD: "Desktop (Chrome trên Windows 10)" / "iOS 16 (iPhone 13)" / "Cả hai" -->
  - **Offline / connectivity**: <!-- VD: "Luôn có WiFi" hoặc "Thường ở vùng sóng yếu khi giao hàng" -->

- **Decision-Making Pattern**: <!-- Họ quyết định như thế nào khi gặp tính năng mới? VD: "Thử ngay nếu có hướng dẫn ngắn gọn. Từ bỏ nếu mất hơn 3 phút chưa hiểu." Nếu chưa rõ → ghi "TBD" -->

- **Frustration Threshold**: <!-- VD: "Gặp lỗi 2 lần → gọi support. Gặp 3 lần → không dùng nữa." -->

- **Success Signals**: <!-- Dấu hiệu persona này thực sự đang thành công với product. VD: "Hoàn thành báo cáo tháng trước 12h trưa ngày 5 mà không cần hỏi đồng nghiệp" -->

- **Accessibility / Device Notes**: <!-- Yêu cầu đặc thù. VD: "Hay dùng phone trong ánh sáng ngoài trời → cần contrast cao. Ngón tay to → touch target ≥ 48px." -->

- **Related Epics / Stories**: <!-- EP-XXX, US-XXX -->

<!-- Repeat for each persona. -->

## 3. Anti-Personas / Excluded Audiences

| Audience | Why They Are Out Of Scope | Notes |
|----------|---------------------------|-------|
| | | |

## 4. Research Gaps

| Persona / Segment | Missing Insight | Impact | Next Step |
|-------------------|-----------------|--------|----------|
| | | | |

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`
- [ ] Primary và secondary personas phân biệt rõ ràng
- [ ] Mỗi persona có Tech Level được mô tả theo tiêu chí cụ thể — không chỉ "High/Medium/Low"
- [ ] Mỗi persona có Mindset/Quote thể hiện mental model thực tế — hoặc ghi "TBD — cần interview"
- [ ] Goals liệt kê ≥ 3 mục cụ thể và ưu tiên — không generic
- [ ] Pain Points liệt kê ≥ 3 mục cụ thể với context (thời gian mất, tần suất)
- [ ] Usage Context có: tần suất, môi trường, device ưu tiên, offline/connectivity
- [ ] Decision-Making Pattern và Frustration Threshold được mô tả — hoặc ghi "TBD"
- [ ] Success Signals đo được — biết khi nào persona thực sự satisfied
- [ ] Persona details align với the relevant `/docs/product/epics/EP-NNN-{slug}.md` files (User Stories section)
- [ ] Research gaps được ghi nhận explicitly ở §4
