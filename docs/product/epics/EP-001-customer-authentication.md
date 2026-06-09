---
id: EP-001
title: Customer Authentication
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

<!-- ID: EP-001 -->
### EP-001: Customer Authentication

**Priority**: Must
**Affected personas**: PERSONA-001
**KPI contribution**: Enables end-to-end demo purchase.

#### Bối cảnh

- **Bối cảnh hiện tại**: Users need identity before purchase so history, tickets, and exchange are tied to an account.
- **Mục tiêu cụ thể**: Let customers authenticate simply by email or phone OTP.
- **Đối tượng hưởng lợi**: Football fan buyer.
- **Tính cấp thiết**: Required before any purchase or exchange.

#### Vấn đề cần giải quyết

- Purchase must not be anonymous in v1.
- User history and issued e-tickets need a stable user identity.

#### Giá trị mang lại

**Cho người dùng**:
- Can access purchase history and e-tickets across sessions.

**Cho tổ chức**:
- Admin can associate pending and issued tickets with a user.

#### Tiêu chí nghiệm thu cấp Epic

- [ ] User can request OTP by email or phone.
- [ ] User can verify OTP and become logged in.
- [ ] Purchase and exchange actions require authenticated user.

#### Phụ thuộc & Ghi chú

| Loại | Item | Ghi chú |
|---|---|---|
| Respects BR | BR-001 | User must authenticate before purchase |

#### Product Traceability Map

| Epic | FR | Related US | Priority / Coverage | Notes |
|---|---|---|---|---|
| EP-001 | FR-001 | US-001 | Must / covered | |

<!-- ID: FR-001 -->
<!-- EPIC: EP-001 -->
**FR-001 — OTP login**

- Phạm vi: System must let users log in with email or phone number plus OTP.
- Trace:
  - Covered by US: US-001
  - Verifies KPI: End-to-end demo completion
- Ghi chú: Password login is out of scope for v1.

<!-- ID: US-001 -->
<!-- EPIC: EP-001 -->
### US-001: Log in with email or phone OTP

> Với tư cách là **PERSONA-001 Football fan buyer**,
> Tôi muốn **đăng nhập bằng email hoặc số điện thoại và OTP**,
> Để **mua vé và xem lại vé đã mua trong tài khoản của tôi**.

**Priority**
Must

**Persona**
PERSONA-001

**Covers FR**
FR-001

**Respects NFR**
Demo NFR targets are open risk in PRD-OVERVIEW-001 §6.3.

**Respects BR**
BR-001

**Design Reference**
Chưa có design

**Scope**
IN: request OTP, verify OTP, create authenticated session for purchase/history/exchange.

**Out of Scope**
Password login, social login, account profile management.

**Testability**
Manual or automated test can verify successful OTP login and blocked purchase action while unauthenticated.

<!-- ID: AC-001 -->
<!-- US: US-001 -->
**AC-001 (Happy Path)**
Given a user enters a valid email or phone number, when the user submits a valid OTP, then the app marks the user as logged in and allows purchase actions.

<!-- ID: AC-002 -->
<!-- US: US-001 -->
**AC-002 (Error)**
Given a user is not logged in, when the user tries to start checkout or exchange a ticket, then the app requires login before continuing.

> **Assumption**: OTP delivery mechanism is demo-capable and does not need vendor selection in Product.
> **Validate**: Architecture confirms OTP delivery approach.
> **Change trigger**: If production identity is required, revisit authentication scope.
