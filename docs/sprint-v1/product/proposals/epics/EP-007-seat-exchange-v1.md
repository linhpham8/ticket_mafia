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

# EP-007 Seat Exchange Proposal — Sprint v1

## New

<!-- ID: EP-007 -->
### EP-007: Seat Exchange

**Priority**: Must
**Affected personas**: PERSONA-001, PERSONA-002
**KPI contribution**: User can change an issued ticket to an equal-or-higher priced available seat.

#### Bối cảnh

- **Bối cảnh hiện tại**: User may need to change selected seat after ticket issuance.
- **Mục tiêu cụ thể**: Support exchange to available equal-or-higher priced seat with manual confirmation for price difference.
- **Đối tượng hưởng lợi**: Football fan buyer and ticket sales admin.
- **Tính cấp thiết**: Explicit v1 user requirement.

#### Vấn đề cần giải quyết

- Exchange must not downgrade to cheaper seats.
- Existing ticket must remain valid until new ticket is confirmed.

#### Giá trị mang lại

**Cho người dùng**:
- Can change seat without losing current valid ticket before confirmation.

**Cho tổ chức**:
- Preserves payment and seat state rules during exchange.

#### Tiêu chí nghiệm thu cấp Epic

- [ ] User can start exchange from an issued ticket.
- [ ] User can select only available equal-or-higher priced seats.
- [ ] Higher priced exchange requires manual transfer confirmation for difference.
- [ ] Admin confirmation issues new ticket and marks old ticket exchanged.

#### Phụ thuộc & Ghi chú

| Loại | Item | Ghi chú |
|---|---|---|
| Depends-on | EP-003, EP-005, EP-006 | Reuses checkout and confirmation concepts |
| Respects BR | BR-007 | Exchange rule |

#### Product Traceability Map

| Epic | FR | Related US | Priority / Coverage | Notes |
|---|---|---|---|---|
| EP-007 | FR-011 | US-012 | Must / covered | |
| EP-007 | FR-012 | US-012 | Must / covered | |

<!-- ID: FR-011 -->
<!-- EPIC: EP-007 -->
**FR-011 — Start seat exchange**

- Phạm vi: System must let user start exchange from an issued ticket and select an available equal-or-higher priced seat.
- Trace:
  - Covered by US: US-012
  - Verifies KPI: End-to-end demo completion
- Ghi chú: Cheaper-seat exchange is blocked.

<!-- ID: FR-012 -->
<!-- EPIC: EP-007 -->
**FR-012 — Confirm exchange and retire old ticket**

- Phạm vi: System must process exchange through a checkout-like hold and admin confirmation flow; after confirmation, issue new ticket and mark old ticket `EXCHANGED`.
- Trace:
  - Covered by US: US-012
  - Verifies KPI: End-to-end demo completion
- Ghi chú: Old ticket remains valid until exchange confirmation.

<!-- ID: US-012 -->
<!-- EPIC: EP-007 -->
### US-012: Exchange issued ticket to equal-or-higher priced seat

> Với tư cách là **PERSONA-001 Football fan buyer**,
> Tôi muốn **đổi ghế sang ghế trống có giá bằng hoặc cao hơn**,
> Để **thay đổi vị trí ngồi mà vẫn tuân thủ quy tắc thanh toán**.

**Priority**
Must

**Persona**
PERSONA-001

**Covers FR**
FR-011, FR-012

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-001, BR-007, BR-008

**Design Reference**
Chưa có design

**Scope**
IN: choose eligible replacement seat, hold new seat for 10 minutes, show QR for price difference when needed, admin confirms exchange, issue new ticket, mark old ticket exchanged, release old seat.

**Out of Scope**
Downgrade exchange, refund difference, transfer ticket to another user.

**Testability**
Verify lower-priced seats are blocked, equal-priced exchange requires no extra payment amount, higher-priced exchange requires confirmation, and old ticket remains valid until confirmation.

<!-- ID: AC-023 -->
<!-- US: US-012 -->
**AC-023 (Happy Path)**
Given the user has an `ISSUED` ticket, when the user selects an available higher-priced seat for exchange and admin confirms the difference payment, then the system issues the new ticket, marks the old ticket `EXCHANGED`, and releases the old seat.

<!-- ID: AC-024 -->
<!-- US: US-012 -->
**AC-024 (Error)**
Given the user selects a cheaper seat or an unavailable seat for exchange, when the user attempts to continue, then the system blocks the exchange before checkout.

> **Assumption**: Exchange confirmation uses the same admin confirmation behavior as purchase.
> **Validate**: Product Owner confirms before Architecture.
> **Change trigger**: If refund or downgrade exchange is required, revisit Product scope.

## Updated

## Removed

