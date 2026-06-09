---
id: EP-003
title: Manual Transfer Checkout
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

<!-- ID: EP-003 -->
### EP-003: Manual Transfer Checkout

**Priority**: Must
**Affected personas**: PERSONA-001
**KPI contribution**: User can submit a manual transfer purchase for admin confirmation.

#### Bối cảnh

- **Bối cảnh hiện tại**: Demo does not need a payment gateway.
- **Mục tiêu cụ thể**: Hold seats, show default transfer QR, and let user submit payment completion.
- **Đối tượng hưởng lợi**: Football fan buyer and ticket sales admin.
- **Tính cấp thiết**: Checkout connects seat selection to admin confirmation.

#### Vấn đề cần giải quyết

- Selected seats must be protected while user transfers money.
- User needs a clear way to tell admin that payment was made.

#### Giá trị mang lại

**Cho người dùng**:
- Can pay by QR transfer and know the order is waiting for confirmation.

**Cho tổ chức**:
- Can demonstrate payment workflow without gateway integration.

#### Tiêu chí nghiệm thu cấp Epic

- [ ] Checkout starts a 10-minute seat hold.
- [ ] Checkout uses price snapshot at payment step.
- [ ] User sees default transfer QR.
- [ ] User can submit payment completion and create pending admin confirmation.

#### Phụ thuộc & Ghi chú

| Loại | Item | Ghi chú |
|---|---|---|
| Depends-on | EP-001, EP-002, EP-004 | Requires login, seat selection, active price, default QR |
| Respects BR | BR-002, BR-004, BR-005 | Hold, price snapshot, admin confirmation |

#### Product Traceability Map

| Epic | FR | Related US | Priority / Coverage | Notes |
|---|---|---|---|---|
| EP-003 | FR-004 | US-004 | Must / covered | |
| EP-003 | FR-005 | US-005 | Must / covered | |

<!-- ID: FR-004 -->
<!-- EPIC: EP-003 -->
**FR-004 — Start checkout with seat hold and price snapshot**

- Phạm vi: System must hold selected seats for 10 minutes and snapshot each seat price when the user starts checkout.
- Trace:
  - Covered by US: US-004
  - Verifies KPI: End-to-end demo completion
- Ghi chú: Hold starts when user taps payment/checkout.

<!-- ID: FR-005 -->
<!-- EPIC: EP-003 -->
**FR-005 — Submit manual payment completion**

- Phạm vi: System must show the active default transfer QR and let the user mark payment as completed, creating a pending admin confirmation record.
- Trace:
  - Covered by US: US-005
  - Verifies KPI: End-to-end demo completion
- Ghi chú: No payment gateway verification in v1.

<!-- ID: US-004 -->
<!-- EPIC: EP-003 -->
### US-004: Start checkout and hold selected seats

> Với tư cách là **PERSONA-001 Football fan buyer**,
> Tôi muốn **bấm thanh toán sau khi chọn ghế**,
> Để **ghế của tôi được giữ trong khi tôi chuyển khoản**.

**Priority**
Must

**Persona**
PERSONA-001

**Covers FR**
FR-004

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-002, BR-003, BR-004

**Design Reference**
Chưa có design

**Scope**
IN: create order, hold seats for 10 minutes, snapshot prices, show countdown and total amount.

**Out of Scope**
Payment gateway redirect, card payment, bank API reconciliation.

**Testability**
Verify selected seats become held for the user, unavailable to others, and keep checkout-time price.

<!-- ID: AC-007 -->
<!-- US: US-004 -->
**AC-007 (Happy Path)**
Given the logged-in user selected 1 to 5 available seats, when the user taps checkout, then the system creates an order, holds the seats for 10 minutes, and snapshots the price for each seat.

<!-- ID: AC-008 -->
<!-- US: US-004 -->
**AC-008 (Edge)**
Given the 10-minute checkout hold expires before payment completion, when the timer ends, then the order is expired and its seats return to `AVAILABLE`.

> **Assumption**: Countdown precision suitable for demo is acceptable.
> **Validate**: Architecture confirms expiration job or equivalent mechanism.
> **Change trigger**: If production traffic is required, revisit concurrency and expiry reliability.

<!-- ID: US-005 -->
<!-- EPIC: EP-003 -->
### US-005: Submit payment completion after transfer

> Với tư cách là **PERSONA-001 Football fan buyer**,
> Tôi muốn **xem QR chuyển khoản và bấm kết thúc thanh toán sau khi chuyển khoản**,
> Để **admin có thể xác nhận và trả vé cho tôi**.

**Priority**
Must

**Persona**
PERSONA-001

**Covers FR**
FR-005

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-005

**Design Reference**
Chưa có design

**Scope**
IN: show active default transfer QR, show order amount, user confirms transfer completion, create pending admin confirmation.

**Out of Scope**
Uploading transfer receipt, automatic payment matching.

**Testability**
Verify payment completion creates `PENDING_ADMIN_CONFIRM` order and starts admin confirmation window.

<!-- ID: AC-009 -->
<!-- US: US-005 -->
**AC-009 (Happy Path)**
Given the checkout hold is still active, when the user taps payment completion, then the order moves to `PENDING_ADMIN_CONFIRM` and waits for admin decision.

<!-- ID: AC-010 -->
<!-- US: US-005 -->
**AC-010 (Error)**
Given the checkout hold has expired, when the user tries to complete payment, then the app rejects the action and requires the user to create a new order.

> **Assumption**: One active default QR is enough for all users in v1.
> **Validate**: Product Owner confirms before Design.
> **Change trigger**: If per-order transfer content is required, revise checkout and admin confirmation.
