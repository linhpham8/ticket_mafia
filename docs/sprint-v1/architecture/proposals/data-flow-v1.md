---
status: APPROVED
version: v1
sprint: 1
phase: architecture
sprint_id: sprint-v1
created: 2026-06-08
updated: 2026-06-08 05:24
approved_by: user
approved_at: 2026-06-08T05:24:02Z
applied_to_living: true 8225310878e8569297961fcc0ec8090f2034566d (sealed 2026-06-08 22:21)
---

# Data Flow Proposal — Sprint v1

## New

<!-- ID: FLOW-001 -->
### FLOW-001: Customer Ticket Purchase Data Flow

#### External Actors / Systems

| Actor / System | Boundary | Role in flow |
|---|---|---|
| Football Fan | external | Browse, select seats, submit payment completion |
| Bank transfer QR | external manual rail | User transfers outside system |
| Backend API | internal | Processes holds/orders/tickets |
| PostgreSQL | internal data store | Source of truth |

#### Processes

| Process | Responsibility | Owner / bounded context | Related FR / US / API |
|---|---|---|---|
| Browse matches and seats | read available sale inventory | Match & Inventory | FR-002, FR-003, API-003, API-004 |
| Hold seats and create order | reserve seats and snapshot price | Order & Payment | FR-004, API-005 |
| Submit payment completion | move order to pending admin confirmation | Order & Payment | FR-005, API-006 |

#### Data Stores

| Data store | Stored data | Source of truth? | Owner / consistency model |
|---|---|---|---|
| PostgreSQL | users, sessions, matches, seats, orders, order_items, tickets | yes | ACID transactions |

#### Data Flows

| # | From | To | Data / action label | Mode | Notes |
|---|---|---|---|---|---|
| 1 | Fan | Backend | match/seat query | sync | authenticated required before checkout |
| 2 | Backend | PostgreSQL | available seats/prices | sync | read committed |
| 3 | Fan | Backend | checkout selected seats + Idempotency-Key | sync | creates hold |
| 4 | Backend | PostgreSQL | order/order_items/seat hold writes | sync | transaction |
| 5 | Fan | Backend | payment completed | sync | pending admin confirm |

#### Draw.io/XML Source

- **Asset path**: `assets/dfd-ticketing-core.drawio`
- **Required notation check**: actor rectangles, process circles, open-ended data store, labeled arrows.
- **Trace**: FR-002, FR-003, FR-004, FR-005.
- **User group split**: customer flow.

<!-- ID: FLOW-002 -->
### FLOW-002: Admin Confirmation Data Flow

#### External Actors / Systems

| Actor / System | Boundary | Role in flow |
|---|---|---|
| Ticket Admin | internal operator | confirms/rejects pending transfers |
| Backend API | internal | applies state transition |
| PostgreSQL | internal data store | stores orders/tickets/audit |

#### Processes

| Process | Responsibility | Owner / bounded context | Related FR / US / API |
|---|---|---|---|
| Review pending order | load pending confirmation list | Order & Payment | FR-008, API-007 |
| Confirm/reject payment | issue ticket or release seats | Order & Payment, Ticket, Audit | FR-008, API-007 |

#### Data Stores

| Data store | Stored data | Source of truth? | Owner / consistency model |
|---|---|---|---|
| PostgreSQL | orders, seats, tickets, audit_logs, idempotency_records | yes | ACID transaction |

#### Data Flows

| # | From | To | Data / action label | Mode | Notes |
|---|---|---|---|---|---|
| 1 | Admin | Backend | pending filter/status query | sync | admin session |
| 2 | Admin | Backend | confirm/reject + Idempotency-Key | sync | state guard |
| 3 | Backend | PostgreSQL | order/ticket/seat/audit writes | sync | transaction |

#### Draw.io/XML Source

- **Asset path**: `assets/dfd-ticketing-core.drawio`
- **Trace**: FR-008.
- **User group split**: admin flow.

<!-- ID: FLOW-003 -->
### FLOW-003: Ticket Scan And Exchange Data Flow

#### External Actors / Systems

| Actor / System | Boundary | Role in flow |
|---|---|---|
| Football Fan | external | views ticket and starts exchange |
| Gate Scan Consumer | external/integration | submits scan update |
| Backend API | internal | validates ticket token and state |
| PostgreSQL | internal data store | stores tickets and audit |

#### Processes

| Process | Responsibility | Owner / bounded context | Related FR / US / API |
|---|---|---|---|
| View ticket | expose issued QR/e-ticket | Ticket & Scan | FR-009, API-009 |
| Scan ticket | atomic used/scanned update | Ticket & Scan | FR-010, API-013 |
| Exchange seat | select eligible replacement and confirm | Ticket & Scan, Order & Payment | FR-011, FR-012, API-014, API-015 |

#### Data Stores

| Data store | Stored data | Source of truth? | Owner / consistency model |
|---|---|---|---|
| PostgreSQL | tickets, scan_events, orders, seats, audit_logs | yes | ACID transaction |

#### Data Flows

| # | From | To | Data / action label | Mode | Notes |
|---|---|---|---|---|---|
| 1 | Fan | Backend | ticket detail request | sync | user-owned tickets only |
| 2 | Gate Scan Consumer | Backend | signed QR token + Idempotency-Key | sync | one-time scan |
| 3 | Fan | Backend | exchange request + replacement seat | sync | equal-or-higher price |
| 4 | Backend | PostgreSQL | ticket/seat/order updates | sync | transaction |

#### Draw.io/XML Source

- **Asset path**: `assets/dfd-ticketing-core.drawio`
- **Trace**: FR-009, FR-010, FR-011, FR-012.
- **User group split**: ticket/scan/exchange flow.

## Updated

## Removed

