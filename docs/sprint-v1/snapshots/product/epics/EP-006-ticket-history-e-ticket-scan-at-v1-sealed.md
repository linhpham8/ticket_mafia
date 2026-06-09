---
id: EP-006
title: Ticket History E Ticket Scan
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

<!-- ID: EP-006 -->
### EP-006: Ticket History E-ticket Scan

**Priority**: Must
**Affected personas**: PERSONA-001, PERSONA-003
**KPI contribution**: User can retrieve issued tickets and scan state can be updated once.

#### Bối cảnh

- **Bối cảnh hiện tại**: Online purchase must produce a digital ticket.
- **Mục tiêu cụ thể**: Let users view purchase history, open QR/e-ticket detail, and support one-time scan status update.
- **Đối tượng hưởng lợi**: Football fan buyer and gate scan operator.
- **Tính cấp thiết**: Ticket retrieval is the visible output of purchase.

#### Vấn đề cần giải quyết

- User needs to access issued tickets after admin confirmation.
- QR/e-ticket must not be reusable after scan.

#### Giá trị mang lại

**Cho người dùng**:
- Can open QR/e-ticket for stadium entry.

**Cho tổ chức**:
- Can demonstrate digital ticket lifecycle and one-time use.

#### Tiêu chí nghiệm thu cấp Epic

- [ ] User can view purchase history.
- [ ] User can open issued ticket detail and QR/e-ticket.
- [ ] Scan update marks ticket as scanned/used once.
- [ ] Repeated scan or invalid ticket cannot be accepted.

#### Phụ thuộc & Ghi chú

| Loại | Item | Ghi chú |
|---|---|---|
| Depends-on | EP-005 | Ticket exists after admin confirmation |
| Respects BR | BR-006 | One-time scan |

#### Product Traceability Map

| Epic | FR | Related US | Priority / Coverage | Notes |
|---|---|---|---|---|
| EP-006 | FR-009 | US-009, US-010 | Must / covered | |
| EP-006 | FR-010 | US-011 | Must / covered | API behavior only |

<!-- ID: FR-009 -->
<!-- EPIC: EP-006 -->
**FR-009 — Purchase history and e-ticket detail**

- Phạm vi: System must let users view purchase history and open issued QR/e-ticket details.
- Trace:
  - Covered by US: US-009, US-010
  - Verifies KPI: End-to-end demo completion
- Ghi chú: Only user-owned tickets are visible to the user.

<!-- ID: FR-010 -->
<!-- EPIC: EP-006 -->
**FR-010 — One-time ticket scan status update**

- Phạm vi: System must expose behavior that marks a valid issued ticket as scanned/used once and rejects repeated scan.
- Trace:
  - Covered by US: US-011
  - Verifies KPI: End-to-end demo completion
- Ghi chú: Full scanner app UI is out of scope.

<!-- ID: US-009 -->
<!-- EPIC: EP-006 -->
### US-009: View purchase history

> Với tư cách là **PERSONA-001 Football fan buyer**,
> Tôi muốn **xem lịch sử mua vé**,
> Để **biết các đơn và vé đã được xác nhận của tôi**.

**Priority**
Must

**Persona**
PERSONA-001

**Covers FR**
FR-009

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-001

**Design Reference**
Chưa có design

**Scope**
IN: show user's own orders/tickets and statuses relevant to pending, issued, cancelled/rejected, exchanged, and scanned.

**Out of Scope**
Admin reporting, finance reconciliation.

**Testability**
Verify user can only see their own purchase history and status changes after admin action.

<!-- ID: AC-017 -->
<!-- US: US-009 -->
**AC-017 (Happy Path)**
Given a logged-in user has at least one order or ticket, when the user opens purchase history, then the app shows the user's own records with current status.

<!-- ID: AC-018 -->
<!-- US: US-009 -->
**AC-018 (Error/Edge)**
Given a logged-in user has no purchases, when the user opens purchase history, then the app shows an empty state without showing another user's data.

> **Assumption**: Basic user ownership is available from authentication.
> **Validate**: Architecture confirms data ownership checks.
> **Change trigger**: If family/group purchase sharing is required, revisit history visibility.

<!-- ID: US-010 -->
<!-- EPIC: EP-006 -->
### US-010: View QR/e-ticket detail

> Với tư cách là **PERSONA-001 Football fan buyer**,
> Tôi muốn **mở chi tiết vé và QR/e-ticket**,
> Để **dùng vé khi vào cổng sân**.

**Priority**
Must

**Persona**
PERSONA-001

**Covers FR**
FR-009

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-006

**Design Reference**
Chưa có design

**Scope**
IN: issued ticket detail, match info, seat code, QR/e-ticket value, ticket status.

**Out of Scope**
PDF export, wallet integration, transfer to another user.

**Testability**
Verify issued tickets show QR detail and non-issued/cancelled tickets do not show usable QR.

<!-- ID: AC-019 -->
<!-- US: US-010 -->
**AC-019 (Happy Path)**
Given a ticket is `ISSUED`, when the user opens ticket detail, then the app shows match, seat code, status, and QR/e-ticket for entry.

<!-- ID: AC-020 -->
<!-- US: US-010 -->
**AC-020 (Error/Edge)**
Given a ticket is `CANCELLED`, `REJECTED`, or `EXCHANGED`, when the user opens ticket detail, then the app does not present it as a valid entry ticket.

> **Assumption**: QR content format is decided in Architecture.
> **Validate**: Architecture defines ticket token format.
> **Change trigger**: If external gate scanner requires a specific QR format, revise contract.

<!-- ID: US-011 -->
<!-- EPIC: EP-006 -->
### US-011: Mark ticket as scanned once

> Với tư cách là **PERSONA-003 Gate scan operator**,
> Tôi muốn **gửi trạng thái quét vé vào hệ thống**,
> Để **vé hợp lệ chỉ được dùng một lần khi vào cổng**.

**Priority**
Must

**Persona**
PERSONA-003

**Covers FR**
FR-010

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-006, BR-008

**Design Reference**
Chưa có design

**Scope**
IN: API-style behavior to update issued ticket to scanned/used and reject repeated or invalid scan.

**Out of Scope**
Dedicated scanner app UI and offline gate scanning.

**Testability**
Verify first valid scan succeeds and repeated scan fails.

<!-- ID: AC-021 -->
<!-- US: US-011 -->
**AC-021 (Happy Path)**
Given a ticket is `ISSUED` and not previously scanned, when the scan update is submitted, then the ticket status changes to `USED/SCANNED`.

<!-- ID: AC-022 -->
<!-- US: US-011 -->
**AC-022 (Error)**
Given a ticket is already `USED/SCANNED`, when another scan update is submitted, then the system rejects the scan and keeps the ticket as already scanned.

> **Assumption**: Scanner UI is out of Product v1; only status update behavior is needed.
> **Validate**: Product Owner confirms before Design.
> **Change trigger**: If a scanner app screen is required, start Design/Product change.
