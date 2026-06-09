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

# Architecture Proposal — Sprint v1

## New

<!-- ID: ARCH-OVERVIEW-001 -->
### Architecture Overview

#### 1. Executive Summary

- **Architecture style**: Modular Monolith backend in a monorepo.
- **Primary runtime**: Java Spring Boot API, PostgreSQL, Next.js + Tailwind web/admin, Flutter mobile.
- **Primary deployment shape**: Docker Compose for local demo: backend API, PostgreSQL, user website, admin web, Flutter app connecting to API.
- **Key trade-off**: Optimizes for demo speed and simpler operations; trades off independent service scaling and production IAM/payment automation.
- **Primary risks**: demo-only auth/security exceptions; no CI/CD; manual payment confirmation; no queue/waiting-room.

#### 2. Architecture Package Index

| File | Purpose | Status / Notes |
|---|---|---|
| `architecture.md` | System overview, C4, components, traceability | Approved v1 proposal target |
| `project-reference.md` | Code-facing module/source tree contract | Approved v1 proposal target |
| `api-specs.md` | REST API contract catalog | Approved v1 proposal target |
| `erd.md` | PostgreSQL data model | Approved v1 proposal target |
| `sequence.md` | Core runtime flows | Approved v1 proposal target |
| `data-flow.md` | DFD and data ownership | Approved v1 proposal target |
| `events.md` | In-process domain event notes | Approved v1 proposal target |
| `nfr.md` | Demo NFR/security/observability targets | Approved v1 proposal target |
| `adr.md` | Significant decisions and exceptions | Approved v1 proposal target |
| `assets/c4-model.drawio` | Editable C4 source | Generated |
| `assets/dfd-ticketing-core.drawio` | Editable DFD source | Generated |

#### 3. C4 Model

##### 3.1 System Context

| Actor / External System | Relationship | Notes |
|---|---|---|
| PERSONA-001 Football fan buyer | Uses iOS/Android/Web to browse, buy, view, and exchange tickets | External user |
| PERSONA-002 Ticket sales admin | Uses Admin Web to configure matches/prices and confirm payments | Internal operator |
| PERSONA-003 Gate scan operator / consumer | Calls scan update behavior | Scanner UI out of scope; API behavior in scope |
| Bank transfer QR | External manual payment rail | No gateway integration; QR is configured by admin |

##### 3.2 Container View

| Container | Responsibility | Technology | Owns Data? | Interfaces |
|---|---|---|---|---|
| User Website | User web flow for browse/buy/history/exchange | Next.js + Tailwind | No | REST `/api/v1` |
| Admin Web | Match/inventory/QR/payment confirmation operations | Next.js + Tailwind | No | REST `/api/v1/admin` |
| Mobile App | iOS/Android user app | Flutter | No | REST `/api/v1` |
| Backend API | Business rules, transactions, auth, scheduler, QR token generation | Java Spring Boot | Yes, via PostgreSQL | REST, scheduled jobs |
| PostgreSQL | Transactional source of truth | PostgreSQL | Yes | SQL |

##### 3.3 Component View

| Component / Module | Responsibility | Input | Output | Upstream / Downstream |
|---|---|---|---|---|
| ARCH-COMP-001 Auth Module | Mock OTP login, sessions, auth guards | identifier, OTP | session token | Clients -> Backend |
| ARCH-COMP-002 Match & Inventory Module | Match status, seat generation, active price | admin config, user browse | matches, seats, price snapshots | Admin/User clients, DB |
| ARCH-COMP-003 Order & Payment Module | Seat hold, checkout, pending confirmation, expiry scheduler | selected seats, payment completion, admin decision | orders, issued tickets | Inventory, Ticket, Audit |
| ARCH-COMP-004 Ticket & Scan Module | QR/e-ticket generation, scan atomic update, exchange | issued tickets, scan request, exchange request | ticket status | Order, Inventory, Audit |
| ARCH-COMP-005 Audit Module | Immutable audit records for admin-sensitive actions | domain action context | audit log records | All backend modules |

##### 3.4 C4 Source Asset

- **Draw.io/XML asset path**: `assets/c4-model.drawio`
- **Status**: generated
- **Required views in source**: System Context + Container View + Component View are represented in one editable source.
- **Connector routing**: source uses explicit connectors with `jumpStyle=arc`.

#### 3b. Architecture Traceability Map

| FR / US | Primary Components / Contexts | APIs / Events | Sequence / Data Ownership Refs | Special Obligations / Notes |
|---|---|---|---|---|
| FR-001 / US-001 | ARCH-COMP-001 | API-001, API-002 | SEQ-001; ENT-001 owns users/sessions | Mock OTP; session timeout 15m |
| FR-002 / US-002 | ARCH-COMP-002 | API-003 | SEQ-002; ENT-002 owns matches | Only `OPEN_FOR_SALE` purchasable |
| FR-003 / US-003 | ARCH-COMP-002 | API-004 | SEQ-002; ENT-003 owns seats | Max 5 selected seats |
| FR-004 / US-004 | ARCH-COMP-003 | API-005 | SEQ-003; ENT-004/ENT-005 own orders/order_items | Transaction + locks + Idempotency-Key |
| FR-005 / US-005 | ARCH-COMP-003 | API-006 | SEQ-003; ENT-004 owns pending order | Manual QR; pending admin confirm |
| FR-006 / US-006 | ARCH-COMP-002 | API-010 | SEQ-002; ENT-002 owns match status | Admin audit |
| FR-007 / US-007 | ARCH-COMP-002 | API-011, API-012 | SEQ-002; ENT-003/ENT-006/ENT-007 own inventory/price/QR | Price snapshot rule |
| FR-008 / US-008 | ARCH-COMP-003, ARCH-COMP-005 | API-007 | SEQ-004; ENT-004/ENT-008 own order/ticket/audit | Idempotency-Key; audit log |
| FR-009 / US-009, US-010 | ARCH-COMP-004 | API-008, API-009 | SEQ-005; ENT-008 owns tickets | QR signed opaque token |
| FR-010 / US-011 | ARCH-COMP-004 | API-013 | SEQ-005; ENT-008 owns ticket status | Atomic `ISSUED -> USED_SCANNED` |
| FR-011 / US-012 | ARCH-COMP-004, ARCH-COMP-002 | API-014 | SEQ-003; ENT-003/ENT-008 | Eligible equal-or-higher seats only |
| FR-012 / US-012 | ARCH-COMP-004, ARCH-COMP-003 | API-015 | SEQ-004; ENT-004/ENT-008 | Old ticket valid until exchange confirm |

#### 4. Bounded Contexts And Context Map

| Context | Subdomain | Responsibility | Upstream | Downstream |
|---|---|---|---|---|
| Auth | Generic | Mock OTP login and sessions | Clients | All protected APIs |
| Match & Inventory | Core | Match, seat, price, default QR config | Admin | Order, Ticket, clients |
| Order & Payment Confirmation | Core | Holds, orders, manual payment completion, admin confirmation, expiry | Auth, Inventory | Ticket, Audit |
| Ticket & Scan | Core | Issued tickets, QR token, scan, exchange | Order, Inventory | Clients, scan consumer |
| Audit | Supporting | Admin and sensitive action logs | All modules | Admin review / security evidence |

Context map: clients call Backend API; Backend modules communicate in-process through application services and domain events. No direct cross-module DB access outside repositories owned by the module.

#### 5. Technology Stack

| Layer | Technology | Version | Reason | ADR Reference | On Approved List? |
|---|---|---|---|---|---|
| Backend | Java Spring Boot | TBD | Standards-preferred backend for business logic | ADR-001 | Yes |
| Database | PostgreSQL | TBD | Strong ACID, constraints, transactional ticket inventory | ADR-001 | Yes |
| User/Admin Web | Next.js + Tailwind | TBD | User requested; material-style custom components | ADR-001 | Partial: React allowed; Next.js requires no backend business logic |
| Mobile | Flutter | TBD | User requested cross-platform mobile app | ADR-001 | Allowed by frontend standards |
| Messaging | N/A for Kafka; in-process domain events | N/A | Demo does not need broker | ADR-001 | Yes with ADR |
| Cache | None required v1 | N/A | Demo scale; DB consistency preferred | ADR-001 | N/A |
| Infrastructure | Docker Compose local | TBD | Demo local runtime | ADR-003 | N/A |
| CI/CD | Skipped for demo | N/A | User confirmed no CI/CD | ADR-003 | Exception |
| Unit test | JUnit 5 + Mockito; Flutter test; Vitest | TBD | User confirmed | N/A | Yes |
| Integration/e2e | Testcontainers; Playwright | TBD | User confirmed | N/A | Yes |
| Error tracking | Skipped for demo | N/A | User confirmed | ADR-003 | Exception |

<!-- ID: ARCH-COMP-001 -->
### ARCH-COMP-001: Auth Module

- **Responsibility**: mock/internal OTP login, session creation, auth guards, session timeout.
- **Owns**: users, OTP challenges, sessions.
- **Exposes**: API-001, API-002.
- **Consumes**: PostgreSQL.
- **Scaling strategy**: stateless API instances later; sessions backed by DB for demo.
- **Failure mode**: login unavailable blocks protected flows; existing sessions expire by policy.

<!-- ID: ARCH-COMP-002 -->
### ARCH-COMP-002: Match & Inventory Module

- **Responsibility**: matches, seat generation, seat state, active price versions, default transfer QR.
- **Owns**: matches, seats, price_versions, payment_qr_configs.
- **Exposes**: API-003, API-004, API-010, API-011, API-012.
- **Consumes**: PostgreSQL locks/constraints.
- **Scaling strategy**: single DB source of truth; no cache in v1.
- **Failure mode**: inventory API failure prevents browsing/checkout but preserves DB state.

<!-- ID: ARCH-COMP-003 -->
### ARCH-COMP-003: Order & Payment Confirmation Module

- **Responsibility**: checkout, seat hold, payment completion, admin confirm/reject, expiry scheduler.
- **Owns**: orders, order_items, idempotency_records for order operations.
- **Exposes**: API-005, API-006, API-007.
- **Consumes**: Inventory, Ticket, Audit in-process services.
- **Scaling strategy**: DB transaction and idempotency key guard for duplicate requests.
- **Failure mode**: failed transaction rolls back hold/order changes.

<!-- ID: ARCH-COMP-004 -->
### ARCH-COMP-004: Ticket & Scan Module

- **Responsibility**: issue QR/e-ticket, ticket detail, one-time scan, exchange flow.
- **Owns**: tickets, scan_events.
- **Exposes**: API-008, API-009, API-013, API-014, API-015.
- **Consumes**: Order, Inventory, Audit.
- **Scaling strategy**: atomic DB update for `ISSUED -> USED_SCANNED`.
- **Failure mode**: repeated scan rejected without state change.

<!-- ID: ARCH-COMP-005 -->
### ARCH-COMP-005: Audit Module

- **Responsibility**: immutable audit log records for admin confirm/reject, price changes, QR config changes, scan/exchange sensitive updates.
- **Owns**: audit_logs.
- **Exposes**: internal application service.
- **Consumes**: all modules publish audit intent in-process.
- **Scaling strategy**: synchronous DB insert inside same transaction where audit is required.
- **Failure mode**: critical audited action fails if audit log cannot be persisted.

<!-- ID: ARCH-001 -->
### ARCH-001: Component Interaction Overview

All clients call Backend API over REST. Backend controllers delegate to application services inside module boundaries. Application services own transactions and call domain services/repositories. Cross-module calls use public application interfaces only; direct repository access across module boundaries is forbidden. PostgreSQL constraints enforce seat uniqueness, state guards, idempotency, and ownership.

## Updated

## Removed
