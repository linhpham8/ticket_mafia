---
id: EP-005
title: Admin Payment Confirmation
status: APPROVED
created: 2026-06-08
updated: 2026-06-08 22:21
approved_by: user
version: v1
sprint: 1
phase: product
sprint_id: sprint-v1
---

<!-- This epic file was bootstrapped by `apply_proposal.py` at sprint seal.
     Content (EP block + FRs + User Stories + AC) is merged from the sprint's
     split epic proposal via anchor-based merge. See `epic-template.md` for
     the canonical structure. -->

<!-- ID: EP-005 -->
### EP-005: Admin Payment Confirmation

**Priority**: Must
**Affected personas**: PERSONA-002
**KPI contribution**: Admin can issue or reject tickets after manual transfer review.

#### Bối cảnh

- **Bối cảnh hiện tại**: v1 uses manual QR transfer, so admin must confirm payment before ticket issuance.
- **Mục tiêu cụ thể**: Provide pending transaction list and confirm/reject actions.
- **Đối tượng hưởng lợi**: Ticket sales admin and football fan buyer.
- **Tính cấp thiết**: Required to convert pending purchases into issued tickets.

#### Vấn đề cần giải quyết

- User payment completion needs an admin decision.
- Rejected or expired orders must release seats.

#### Giá trị mang lại

**Cho người dùng**:
- Receives e-ticket after admin confirms received payment.

**Cho tổ chức**:
- Keeps manual payment control in demo scope.

#### Tiêu chí nghiệm thu cấp Epic

- [ ] Admin sees pending confirmation records.
- [ ] Admin can confirm and issue tickets.
- [ ] Admin can reject if money is not received.
- [ ] Pending order expires if admin does not confirm within 10 minutes.

#### Phụ thuộc & Ghi chú

| Loại | Item | Ghi chú |
|---|---|---|
| Depends-on | EP-003 | Pending order comes from checkout |
| Respects BR | BR-005 | Confirmation window |

#### Product Traceability Map

| Epic | FR | Related US | Priority / Coverage | Notes |
|---|---|---|---|---|
| EP-005 | FR-008 | US-008 | Must / covered | |

<!-- ID: FR-008 -->
<!-- EPIC: EP-005 -->
**FR-008 — Confirm or reject pending purchase**

- Phạm vi: Admin must confirm payment to issue tickets or reject payment to cancel order and release seats.
- Trace:
  - Covered by US: US-008
  - Verifies KPI: Admin task coverage
- Ghi chú: User must create a new order after admin rejection.

<!-- ID: US-008 -->
<!-- EPIC: EP-005 -->
### US-008: Confirm or reject pending customer payment

> Với tư cách là **PERSONA-002 Ticket sales admin**,
> Tôi muốn **xác nhận hoặc từ chối giao dịch chờ xác nhận**,
> Để **trả vé cho khách đã chuyển tiền hoặc giải phóng ghế nếu chưa nhận được tiền**.

**Priority**
Must

**Persona**
PERSONA-002

**Covers FR**
FR-008

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-005, BR-008

**Design Reference**
Chưa có design

**Scope**
IN: pending order list, confirm payment, reject payment, ticket issuance, seat release on rejection/expiry.

**Out of Scope**
Partial payment, refund, receipt upload verification.

**Testability**
Verify confirm issues ticket and reject/expiry releases seats.

<!-- ID: AC-015 -->
<!-- US: US-008 -->
**AC-015 (Happy Path)**
Given an order is `PENDING_ADMIN_CONFIRM`, when admin confirms payment within 10 minutes, then tickets are issued to the user and selected seats are no longer available.

<!-- ID: AC-016 -->
<!-- US: US-008 -->
**AC-016 (Error/Edge)**
Given an order is `PENDING_ADMIN_CONFIRM`, when admin rejects payment or the 10-minute confirmation window expires, then the order is cancelled/rejected and its seats return to `AVAILABLE`.

> **Assumption**: Admin validates transfer outside the system.
> **Validate**: Product Owner confirms manual validation is enough for demo.
> **Change trigger**: If automated payment verification is required, revisit checkout and confirmation.
