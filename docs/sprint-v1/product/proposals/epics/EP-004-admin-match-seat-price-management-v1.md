---
status: APPROVED
version: v1
sprint: 1
phase: product
sprint_id: sprint-v1
created: 2026-06-08
updated: 2026-06-08 04:25
approved_by: user
approved_at: 2026-06-08T04:25:15Z
applied_to_living: true 8225310878e8569297961fcc0ec8090f2034566d (sealed 2026-06-08 22:21)
---

# EP-004 Admin Match Seat Price Management Proposal — Sprint v1

## New

<!-- ID: EP-004 -->
### EP-004: Admin Match Seat Price Management

**Priority**: Must
**Affected personas**: PERSONA-002
**KPI contribution**: Admin can configure sellable inventory for the demo.

#### Bối cảnh

- **Bối cảnh hiện tại**: Matches, seats, and prices need admin setup before users can buy.
- **Mục tiêu cụ thể**: Let admin manage match status, generate seats, set prices, and configure default transfer QR.
- **Đối tượng hưởng lợi**: Ticket sales admin.
- **Tính cấp thiết**: Required setup for all user purchase flows.

#### Vấn đề cần giải quyết

- Admin needs sale inventory and price controls.
- Updated prices must apply only to future purchases.

#### Giá trị mang lại

**Cho người dùng**:
- Sees accurate seat options and prices.

**Cho tổ chức**:
- Can demonstrate match setup, seat setup, and pricing operations.

#### Tiêu chí nghiệm thu cấp Epic

- [ ] Admin can manage match list, create match, update match, and change match status.
- [ ] Admin can create/update seats by section/floor/VIP.
- [ ] Admin can update prices and preserve existing order price snapshots.
- [ ] Admin can configure multiple transfer QR records and choose one default active QR.

#### Phụ thuộc & Ghi chú

| Loại | Item | Ghi chú |
|---|---|---|
| Respects BR | BR-004, BR-008 | Price snapshot and lifecycle |

#### Product Traceability Map

| Epic | FR | Related US | Priority / Coverage | Notes |
|---|---|---|---|---|
| EP-004 | FR-006 | US-006 | Must / covered | |
| EP-004 | FR-007 | US-007 | Must / covered | |

<!-- ID: FR-006 -->
<!-- EPIC: EP-004 -->
**FR-006 — Admin match management**

- Phạm vi: Admin must manage match list, create matches, update matches, and set match state to `OPEN_FOR_SALE`, `SOLD_OUT`, `CANCELLED`, or `CLOSED`.
- Trace:
  - Covered by US: US-006
  - Verifies KPI: Admin task coverage
- Ghi chú: Draft state is not required in v1.

<!-- ID: FR-007 -->
<!-- EPIC: EP-004 -->
**FR-007 — Admin seat, price, and transfer QR management**

- Phạm vi: Admin must generate/manage seats by section/floor/VIP, update active prices, and configure the default transfer QR.
- Trace:
  - Covered by US: US-007
  - Verifies KPI: Admin task coverage
- Ghi chú: Active price applies only to future checkout starts.

<!-- ID: US-006 -->
<!-- EPIC: EP-004 -->
### US-006: Manage matches and sale status

> Với tư cách là **PERSONA-002 Ticket sales admin**,
> Tôi muốn **tạo và cập nhật trận đấu cùng trạng thái bán vé**,
> Để **kiểm soát trận nào đang được bán trên app**.

**Priority**
Must

**Persona**
PERSONA-002

**Covers FR**
FR-006

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-008

**Design Reference**
Chưa có design

**Scope**
IN: match list, create match, update match details, change state among `OPEN_FOR_SALE`, `SOLD_OUT`, `CANCELLED`, `CLOSED`.

**Out of Scope**
Competition standings, team roster management, match content CMS.

**Testability**
Verify admin state changes control whether match can be bought by users.

<!-- ID: AC-011 -->
<!-- US: US-006 -->
**AC-011 (Happy Path)**
Given admin creates a match and sets it to `OPEN_FOR_SALE`, when user opens match list, then the match is available for seat selection.

<!-- ID: AC-012 -->
<!-- US: US-006 -->
**AC-012 (Error/Edge)**
Given admin sets a match to `CANCELLED` or `CLOSED`, when user tries to buy that match, then new purchase is blocked.

> **Assumption**: Match starts directly from `OPEN_FOR_SALE` in v1.
> **Validate**: Product Owner confirms no `DRAFT` state is needed.
> **Change trigger**: If admin needs pre-sale staging, add `DRAFT` later.

<!-- ID: US-007 -->
<!-- EPIC: EP-004 -->
### US-007: Configure seats, prices, and default transfer QR

> Với tư cách là **PERSONA-002 Ticket sales admin**,
> Tôi muốn **tạo ghế, cập nhật giá vé và chọn QR chuyển khoản mặc định**,
> Để **người dùng thấy đúng ghế, đúng giá và đúng QR khi thanh toán**.

**Priority**
Must

**Persona**
PERSONA-002

**Covers FR**
FR-007

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-004

**Design Reference**
Chưa có design

**Scope**
IN: generate/update seats by section/floor/VIP, set active price versions, configure multiple QR records, choose one default QR.

**Out of Scope**
Per-user QR, per-order bank transfer content, discount campaigns.

**Testability**
Verify new checkout uses latest active price and existing checkout keeps old snapshot price.

<!-- ID: AC-013 -->
<!-- US: US-007 -->
**AC-013 (Happy Path)**
Given admin updates a seat price, when a user starts checkout after the update, then the order uses the new price.

<!-- ID: AC-014 -->
<!-- US: US-007 -->
**AC-014 (Edge)**
Given a user already started checkout before admin updates price, when the admin updates price, then the existing order keeps its original snapshot price.

> **Assumption**: Only one transfer QR is active as default at a time.
> **Validate**: Product Owner confirms before Design.
> **Change trigger**: If per-match QR is required, revise admin QR scope.

## Updated

## Removed

