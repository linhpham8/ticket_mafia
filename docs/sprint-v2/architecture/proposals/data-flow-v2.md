---
status: APPROVED
version: v2
sprint: 2
phase: architecture
sprint_id: sprint-v2
created: 2026-06-09
updated: 2026-06-09 14:03
approved_by: user
applied_to_living: false
---

# Data Flow Proposal — Sprint v2

## New

<!-- ID: FLOW-004 -->
### FLOW-004: Local Demo Match Browsing Fallback Data Flow

#### External Actors / Systems

| Actor / System | Boundary | Role in flow |
|---|---|---|
| Football Fan | external | Opens match list or seat map in local/dev demo |
| User Website | internal client | Attempts backend read; decides whether fallback display is allowed |
| Backend API | internal | Authoritative match/seat source when available |
| Local Demo Dataset | internal client asset | Display-only fallback source |

#### Processes

| Process | Responsibility | Owner / bounded context | Related FR / US / API |
|---|---|---|---|
| Fetch match/seat read data | request API-003 or API-004 through typed service | User Web Match API Client | FR-002, FR-003, API-003, API-004 |
| Apply fallback gate | allow fallback only for local/dev read paths | User Website | AC-026, AC-028, ADR-004 |
| Render fallback state | show visible fallback banner and demo data | User Website | SCREEN-002, SCREEN-003 |

#### Data Stores

| Data store | Stored data | Source of truth? | Owner / consistency model |
|---|---|---|---|
| PostgreSQL | authoritative matches, seats, prices | yes | Backend ACID transactions |
| Local Demo Dataset | static/demo match and seat rows | no | bundled display-only data |

#### Data Flows

| # | From | To | Data / action label | Mode | Notes |
|---|---|---|---|---|---|
| 1 | Football Fan | User Website | open match list / seat map | sync | local/dev UI |
| 2 | User Website | Backend API | GET matches or seats | sync | authoritative read path |
| 3 | Backend API | User Website | read DTO or error/empty response | sync | empty usable backend data can trigger local fallback in dev |
| 4 | User Website | Local Demo Dataset | fallback read request | sync | read-only; no business mutation |
| 5 | Local Demo Dataset | User Website | demo rows + fallback flag | sync | renders `matches-demo-fallback` / `seat-map-demo-fallback` |

#### Draw.io/XML Source

- **Asset path**: `assets/dfd-local-fallback-v2.drawio`
- **Required notation check**: external actors are rectangles; processes are circles; data stores use open-ended rectangle data-store shape; every arrow has a data/action label; connectors are routed around shapes and use `jumpStyle=arc`.
- **Trace**: FR-002, FR-003, AC-026, AC-028, ADR-004.
- **User group split**: customer local/dev browse flow.

## Updated

<!-- ID: FLOW-001 -->
### FLOW-001: Customer Ticket Purchase Data Flow

#### External Actors / Systems

| Actor / System | Boundary | Role in flow |
|---|---|---|
| Football Fan | external | Browse, select seats, submit payment completion |
| Bank transfer QR | external manual rail | User transfers outside system |
| Backend API | internal | Processes holds/orders/tickets |
| PostgreSQL | internal data store | Source of truth |
| Local Demo Dataset | internal client asset | Optional local/dev display-only fallback for browsing before checkout |

#### Processes

| Process | Responsibility | Owner / bounded context | Related FR / US / API |
|---|---|---|---|
| Browse matches and seats | read available sale inventory; user web may fallback in local/dev display only | Match & Inventory / User Web Match API Client | FR-002, FR-003, API-003, API-004 |
| Hold seats and create order | reserve seats and snapshot price | Order & Payment | FR-004, API-005 |
| Submit payment completion | move order to pending admin confirmation | Order & Payment | FR-005, API-006 |

#### Data Stores

| Data store | Stored data | Source of truth? | Owner / consistency model |
|---|---|---|---|
| PostgreSQL | users, sessions, matches, seats, orders, order_items, tickets | yes | ACID transactions |
| Local Demo Dataset | demo matches/seats for user web fallback | no | local/dev read-only display |

#### Data Flows

| # | From | To | Data / action label | Mode | Notes |
|---|---|---|---|---|---|
| 1 | Fan | Backend | match/seat query | sync | authenticated required before checkout |
| 2 | Backend | PostgreSQL | available seats/prices | sync | read committed |
| 3 | Fan | Backend | checkout selected seats + Idempotency-Key | sync | creates hold; backend-required |
| 4 | Backend | PostgreSQL | order/order_items/seat hold writes | sync | transaction |
| 5 | Fan | Backend | payment completed | sync | pending admin confirm; backend-required |
| 6 | User Website | Local Demo Dataset | fallback match/seat display read | sync | local/dev only; cannot feed checkout |

#### Draw.io/XML Source

- **Asset path**: `assets/dfd-ticketing-core.drawio` and `assets/dfd-local-fallback-v2.drawio`
- **Required notation check**: actor rectangles, process circles, open-ended data store, labeled arrows.
- **Trace**: FR-002, FR-003, FR-004, FR-005, AC-026, AC-028.
- **User group split**: customer flow.

## Removed
