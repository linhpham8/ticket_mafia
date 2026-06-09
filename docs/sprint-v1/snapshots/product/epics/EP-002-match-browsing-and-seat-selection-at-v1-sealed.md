---
id: EP-002
title: Match Browsing And Seat Selection
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

<!-- ID: EP-002 -->
### EP-002: Match Browsing And Seat Selection

**Priority**: Must
**Affected personas**: PERSONA-001
**KPI contribution**: User can discover matches and select concrete seats.

#### Bối cảnh

- **Bối cảnh hiện tại**: Users buy tickets offline and cannot choose seats online.
- **Mục tiêu cụ thể**: Show matches on sale and let users pick generated seat codes by section/floor/VIP area.
- **Đối tượng hưởng lợi**: Football fan buyer.
- **Tính cấp thiết**: Seat choice is the core purchase input.

#### Vấn đề cần giải quyết

- User must know which matches are available for online sale.
- User must select concrete available seats before checkout.

#### Giá trị mang lại

**Cho người dùng**:
- Clear visibility into sections, floors, VIP area, seat codes, and price.

**Cho tổ chức**:
- Online seat state can prevent duplicate sale.

#### Tiêu chí nghiệm thu cấp Epic

- [ ] User sees only matches open for sale.
- [ ] User sees seat sections/floors/VIP area and available seat codes.
- [ ] User can select at most 5 available seats.

#### Phụ thuộc & Ghi chú

| Loại | Item | Ghi chú |
|---|---|---|
| Depends-on | EP-004 | Admin configures matches, seats, and prices |
| Respects BR | BR-003, BR-008 | Max seats and lifecycle rules |

#### Product Traceability Map

| Epic | FR | Related US | Priority / Coverage | Notes |
|---|---|---|---|---|
| EP-002 | FR-002 | US-002 | Must / covered | |
| EP-002 | FR-003 | US-003 | Must / covered | |

<!-- ID: FR-002 -->
<!-- EPIC: EP-002 -->
**FR-002 — Match list on sale**

- Phạm vi: System must show users a list of matches whose status allows ticket sale.
- Trace:
  - Covered by US: US-002
  - Verifies KPI: End-to-end demo completion
- Ghi chú: Closed, sold-out, and cancelled matches are not purchasable.

<!-- ID: FR-003 -->
<!-- EPIC: EP-002 -->
**FR-003 — Concrete seat selection**

- Phạm vi: System must show generated seat codes by section and floor, including section A VIP where configured, and allow up to 5 available seats per checkout.
- Trace:
  - Covered by US: US-003
  - Verifies KPI: End-to-end demo completion
- Ghi chú: Seat code generation details move to Architecture.

<!-- ID: US-002 -->
<!-- EPIC: EP-002 -->
### US-002: View matches currently selling tickets

> Với tư cách là **PERSONA-001 Football fan buyer**,
> Tôi muốn **xem danh sách trận đấu đang bán vé**,
> Để **chọn trận mà tôi muốn mua vé**.

**Priority**
Must

**Persona**
PERSONA-001

**Covers FR**
FR-002

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-008

**Design Reference**
Chưa có design

**Scope**
IN: list matches with `OPEN_FOR_SALE` state and visible sale information needed to enter seat selection.

**Out of Scope**
Marketing pages, team statistics, waitlist, membership priority.

**Testability**
Verify that open matches appear and non-purchasable matches cannot start purchase.

<!-- ID: AC-003 -->
<!-- US: US-002 -->
**AC-003 (Happy Path)**
Given a match is `OPEN_FOR_SALE`, when the user opens the match list, then the match appears and can be opened for seat selection.

<!-- ID: AC-004 -->
<!-- US: US-002 -->
**AC-004 (Error/Edge)**
Given a match is `SOLD_OUT`, `CANCELLED`, or `CLOSED`, when the user opens the match list, then the match is not available for new purchase.

> **Assumption**: Admin-created match data is available before users browse.
> **Validate**: Product Owner confirms demo data setup before Design.
> **Change trigger**: If users must see non-selling matches for information, revise scope.

<!-- ID: US-003 -->
<!-- EPIC: EP-002 -->
### US-003: Select up to 5 available seat codes

> Với tư cách là **PERSONA-001 Football fan buyer**,
> Tôi muốn **chọn ghế cụ thể theo mã ghế**,
> Để **mua đúng vị trí mong muốn trong khu và tầng đã chọn**.

**Priority**
Must

**Persona**
PERSONA-001

**Covers FR**
FR-003

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-001, BR-003, BR-008

**Design Reference**
Chưa có design

**Scope**
IN: show section A/B/C/D, two floors per section, section A VIP where configured, seat codes, availability, and selected seat count.

**Out of Scope**
Automatic best-seat assignment and custom irregular stadium layout editor.

**Testability**
Verify available seats can be selected, unavailable seats cannot, and the sixth selected seat is blocked.

<!-- ID: AC-005 -->
<!-- US: US-003 -->
**AC-005 (Happy Path)**
Given the user is logged in and opens an `OPEN_FOR_SALE` match, when the user selects up to 5 `AVAILABLE` seat codes, then the app shows those seats as selected with the correct current price.

<!-- ID: AC-006 -->
<!-- US: US-003 -->
**AC-006 (Error)**
Given the user has already selected 5 seats, when the user selects another seat, then the app blocks the action and keeps the selected seat count at 5.

> **Assumption**: Seat availability is refreshed enough for demo use.
> **Validate**: Architecture confirms seat state conflict handling.
> **Change trigger**: If production concurrent sale is required, revisit NFR and hold mechanics.
