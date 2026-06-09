---
status: APPROVED
version: v2
sprint: 2
phase: product
sprint_id: sprint-v2
created: 2026-06-09
updated: 2026-06-09 11:42
approved_by: user
applied_to_living: false
---

# PRD Proposal — Sprint v2

## New

## Updated

<!-- ID: PRD-OVERVIEW-001 -->
### Product Overview

#### 1. Executive Summary

`ticket_mafia` is a demo app for selling football tickets online in Vietnam. It serves football fans who want to buy tickets before arriving at the stadium and ticket administrators who need to create matches, manage seat inventory, set prices, and confirm manual transfer payments.

The product replaces on-site ticket purchase with an app-based flow: users log in, browse matches, select up to 5 concrete seats, hold those seats for 10 minutes, scan a configured bank-transfer QR, submit payment completion, and receive QR/e-tickets after admin confirmation. Gate usage is modeled through an API call that marks a ticket as scanned once.

Sprint v2 keeps the v1 business flow intact and makes the demo product feel like a real ticketing marketplace. The user web match list, seat selection, checkout QR, ticket history, and ticket detail screens must present match media, pricing, section/seat context, status, and actions clearly. The admin web must feel like an operational console with summary metrics, clear tables, inventory tabs, and payment-confirmation controls. The local user web must also avoid a blank or indefinitely loading match list when the local backend is unavailable or unseeded.

#### 2. Problem Statement

**Ai đang gặp vấn đề này?** Football fan buyers and ticket sales admins can complete the v1 demo flow, but the current screens do not communicate the football-ticketing domain strongly enough for a stakeholder demo. Developers and reviewers can also hit a blank/loading match page when the local backend is down or has no seeded match data.

**Cách xử lý hiện tại (workaround) là gì?** Users and reviewers rely on sparse functional pages and must manually infer the intended ticketing experience. Developers need to run/seed backend data correctly before the match list becomes useful.

**Chi phí của việc KHÔNG giải quyết?** The product appears unfinished even when the core API flow exists, stakeholder review can stall on visual quality, and local demo setup issues can be mistaken for a broken match-browsing product.

#### 3. Goals & Success Metrics

##### 3.1 Business Goals

| Mục tiêu | KPI | Baseline | Target | Cách đo lường |
|---|---|---|---|---|
| Demonstrate online ticket purchase | End-to-end demo completion | Offline purchase only | User can complete login, seat selection, payment submission, admin confirmation, and ticket viewing in one demo flow | Manual demo script |
| Demonstrate admin sales management | Admin task coverage | No defined admin flow | Admin can create/update match, configure seats/prices, and confirm/reject pending purchases | Manual demo script |
| Improve demo confidence for ticketing UI | Demo screen readiness | Sparse white UI in user/admin pages | Reviewer can identify match list, seat detail, checkout, ticket detail, and admin queue purpose without explanation | Manual stakeholder review |
| Avoid blank local match browsing | Local match-list render resilience | Backend unavailable/unseeded can leave match browsing unusable | Match list renders useful demo state within 2 seconds in local dev even when backend data is unavailable | Local browser check and automated UI test |

##### 3.2 User Goals

| Mục tiêu | KPI | Baseline | Target | Cách đo lường |
|---|---|---|---|---|
| Buy football tickets without going to the stadium | Purchase flow availability | Stadium purchase only | User can reserve seats and submit payment evidence in app/web | Manual observation |
| Access issued tickets | Ticket retrieval | Physical/offline handling | User can open purchase history and view QR/e-ticket | Manual observation |
| Understand available tickets quickly | Match discovery clarity | Plain match list | User can see marketplace-style match cards grouped by date with visible price and ticket signals | Manual observation / screenshot review |
| Operate admin workflows clearly | Admin workflow clarity | Plain admin tables/forms | Admin sees dashboard-style list, inventory, and confirmation screens with clear status/action hierarchy | Manual observation / screenshot review |

#### 4. Business & Process Flows

##### 4.1 Current State (AS-IS)

**Các bên liên quan:** Football fan, ticket sales admin, developer/reviewer running local demo.

**Các bước chính:**
1. Fan opens a plain list of matches and proceeds to seat selection.
2. Fan selects seats and completes manual QR checkout.
3. Admin uses basic screens to configure matches/inventory and confirm payment.
4. Developer/reviewer may need backend and seed data working before the match list shows useful content.

**Điểm đau / Bottleneck:**
- The user-facing pages look unfinished for a football-ticket product.
- Admin screens lack operational hierarchy and quick-read status context.
- Local API unavailability or empty data can make match browsing look broken during demo setup.

##### 4.2 Future State (TO-BE)

**Các bên liên quan:** Football fan, ticket sales admin, developer/reviewer running local demo.

**Các bước chính:**
1. User opens a football-ticket marketplace-style match list with hero media, search/filter affordances, date grouping, event cards, ticket signals, and visible starting price.
2. User opens a match detail / seat selection view with event banner, availability summary, seat grid, legend, selected-seat summary, and checkout CTA.
3. User sees a clearer manual QR checkout and pending-confirmation state.
4. User opens ticket history and ticket detail screens with e-ticket styling and obvious QR validity status.
5. Admin uses dashboard-style match, inventory, and confirmation screens with metrics, tabs, status chips, and clear action priority.
6. Local dev/demo match browsing renders a useful fallback state when backend is unavailable, while real checkout/payment actions still require backend.

**Thay đổi so với AS-IS:**
- The product feels ticket-specific at first glance.
- Demo reviewers can understand the core flows without extra explanation.
- Local runtime setup issues no longer make the match list appear blank or permanently loading.

#### 5. Product Scope

##### 5.1 In Scope

- EP-002 marketplace-style match browsing and visual seat-selection upgrade.
- EP-003 clearer manual QR checkout and pending-confirmation presentation.
- EP-004 admin match / inventory management UI upgrade.
- EP-005 admin confirmation queue UI upgrade.
- EP-006 purchase history and e-ticket detail UI upgrade.
- Local user web API routing and fallback behavior for match browsing and seat map display.

##### 5.2 Out of Scope

- Integrated payment gateway or automatic bank reconciliation.
- Peak-load queue/waiting-room.
- Fan club priority, membership, season tickets, discounts, or whitelist.
- Full gate scanner app UX.
- Refund flow.
- Transfer/resale of tickets between users.
- Complex real-stadium map editor.
- New order, ticket, exchange, or payment lifecycle rules beyond the v1 business rules.

#### 6. Assumptions & Constraints

##### 6.1 Assumptions

| Giả định | Rủi ro nếu sai |
|---|---|
| v2 is allowed to change presentation without changing v1 business states | If stakeholders expect new business capabilities, Product v2 scope must be expanded before Design/Plan |
| Demo fallback data is acceptable for local match browsing only | If fallback is mistaken for production behavior, Architecture/Test must explicitly separate local demo resilience from production API behavior |
| Existing personas remain valid | If new admin/reviewer personas are needed, Personas proposal must be updated before approval |

##### 6.2 Constraints & Target Platform

**Target Platform:** User Web and Admin Web for sprint-v2 scope; existing iOS/Android remain in the broader product but are not materially changed by this sprint.

**Min Browser / OS:** Demo baseline; exact browser matrix deferred to Design/Architecture.

**Language:** Vietnamese primary UI language with ticketing terms readable in English where already present.

**Currency:** VND.

##### 6.3 Open Risks

| Risk | Why It Matters | Owner / Validator | Deadline / Trigger | Placeholder |
|---|---|---|---|---|
| Production NFR targets are still not defined | Architecture cannot size peak-load, uptime, or latency for production | Product Owner / Tech Lead | Before production-readiness sprint | Demo only; no queue/waiting-room |
| v2 UI is inspired by marketplace ticketing patterns, not a copied third-party site contract | Design must produce original UI patterns that fit `ticket_mafia` while using familiar ticket marketplace structure | Product Owner / Design owner | During Design v2 | Ticombo-like list/detail direction, not pixel copy |
| Local fallback must not mask real API failure in production | Test/Architecture must ensure fallback is a local demo behavior and real checkout/payment still requires backend | Tech Lead | Before Implement approval | Fallback only for match list / seat map local resilience |

#### 7. Industry-Common Surfaces

| Tag | Surface | Product Decision | Trace |
|---|---|---|---|
| `[common]` | Ticket marketplace list and event cards | Confirmed for sprint-v2 user web match browsing. | FR-002, US-002, AC-025 |
| `[common]` | Ticket detail / availability context | Confirmed for sprint-v2 match detail and seat selection. | FR-003, US-003, AC-027 |
| `[common]` | Checkout QR and pending state clarity | Confirmed for sprint-v2 manual transfer checkout UI. | FR-005, US-005, AC-029 |
| `[common]` | Admin operational dashboard patterns | Confirmed for sprint-v2 admin match, inventory, and confirmation pages. | FR-006, FR-007, FR-008, US-006, US-007, US-008 |
| `[common]` | E-ticket card and QR validity presentation | Confirmed for sprint-v2 ticket history/detail. | FR-009, US-009, US-010 |
| `[common]` | Local demo resilience | Confirmed for local match list and seat map rendering only. | FR-002, FR-003, US-002, US-003 |

#### 8. Cross-Epic Dependencies

| Source Epic | Depends On | Reason |
|---|---|---|
| EP-003 Manual transfer checkout | EP-001, EP-002, EP-004 | Checkout requires login, selected seats, active match, active prices, and default transfer QR |
| EP-005 Admin confirmation | EP-003 | Admin confirms pending orders created by checkout |
| EP-006 Ticket detail and scan | EP-005 | Tickets only exist after admin confirmation |
| Sprint-v2 UI polish | EP-002, EP-003, EP-004, EP-005, EP-006 | UI improvements span existing user and admin surfaces without changing lifecycle rules |

## Removed

### Self-Review Checklist

- [x] `PROP-1`: Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`
- [x] `PROP-2`: Frontmatter required keys all present and well-formed
- [x] `PROP-3`: `status` is DRAFT and `applied_to_living: false`
- [x] `PROP-4`: `version` matches `v2`
- [x] `PROP-5`: Updated item starts with ID anchor
- [x] `PROP-17`: PRD proposal contains only `PRD-OVERVIEW` item
