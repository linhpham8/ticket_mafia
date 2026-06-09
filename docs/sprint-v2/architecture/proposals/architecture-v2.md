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

# Architecture Overview Proposal — Sprint v2

## New

## Updated

<!-- ID: ARCH-OVERVIEW-001 -->
### Architecture Overview

#### 1. Executive Summary

- **Architecture style**: Modular Monolith backend in a monorepo.
- **Primary runtime**: Java Spring Boot API, PostgreSQL, Next.js + Tailwind user/admin web, Flutter mobile carried forward.
- **Primary deployment shape**: Docker Compose local demo: backend API, PostgreSQL, user website, admin web, and optional Flutter app connecting to API.
- **Sprint v2 architecture change**: enrich ticket marketplace read contracts and add client-side local/dev fallback for user web match list and seat-map display only.
- **Key trade-off**: improves local demo confidence without adding production-scale queueing, anti-bot, payment gateway, broker, or cloud runtime.
- **Primary risks**: demo-only auth/security exceptions, no production anti-bot/waiting-room, no CI/CD, and local fallback must not mask failed checkout/payment/admin mutations.

#### 2. Architecture Package Index

| File | Purpose | Status / Notes |
|---|---|---|
| `architecture.md` | System overview, C4, components, traceability | Updated by Sprint v2 proposal |
| `project-reference.md` | Code-facing module/source tree contract | Updated for local fallback and API rewrite |
| `api-specs.md` | REST API contract catalog | Updated for richer match/seat read DTOs |
| `erd.md` | PostgreSQL data model | Updated for optional match presentation fields |
| `sequence.md` | Core runtime flows | Updated to separate local fallback reads from backend-required mutations |
| `data-flow.md` | DFD and data ownership | Updated with local demo fallback flow |
| `events.md` | In-process domain event notes | No broker added; event model remains in-process |
| `nfr.md` | Demo NFR/security/observability targets | Updated with local fallback render target |
| `adr.md` | Significant decisions and exceptions | Updated with local fallback ADR |
| `assets/c4-model-v2.drawio` | Editable C4 source | Generated |
| `assets/dfd-local-fallback-v2.drawio` | Editable DFD source | Generated |

#### 3. C4 Model

##### 3.1 System Context

| Actor / External System | Relationship | Notes |
|---|---|---|
| PERSONA-001 Football fan buyer | Uses User Website to browse, buy, view tickets, and exchange tickets | External user |
| PERSONA-002 Ticket sales admin | Uses Admin Web to configure matches/prices and confirm payments | Internal operator |
| PERSONA-003 Gate scan operator / consumer | Calls scan update behavior | Scanner UI out of scope; API behavior in scope |
| Bank transfer QR | External manual payment rail | No payment gateway integration; QR configured by admin |
| Local demo fallback dataset | User Website bundled/static fallback source | Local/dev display-only source for match list and seat map when backend read data is unavailable |

##### 3.2 Container View

| Container | Responsibility | Technology | Owns Data? | Interfaces |
|---|---|---|---|---|
| User Website | User web browse/buy/history/exchange UI, Next.js rewrite from `/api/v1/*` to backend, local/dev read fallback for matches/seats | Next.js + Tailwind | No | REST `/api/v1`; local fallback dataset for read display only |
| Admin Web | Match/inventory/QR/payment confirmation operations | Next.js + Tailwind | No | REST `/api/v1/admin` |
| Mobile App | iOS/Android user app | Flutter | No | REST `/api/v1` |
| Backend API | Business rules, transactions, auth, scheduler, QR token generation, ticketing REST contracts | Java Spring Boot | Yes, via PostgreSQL | REST, scheduled jobs, in-process events |
| PostgreSQL | Transactional source of truth | PostgreSQL | Yes | SQL |

##### 3.3 Component View

| Component / Module | Responsibility | Input | Output | Upstream / Downstream |
|---|---|---|---|---|
| ARCH-COMP-001 Auth Module | Mock OTP login, sessions, auth guards | identifier, OTP | session token | Clients -> Backend |
| ARCH-COMP-002 Match & Inventory Module | Match status, presentation fields, seat generation, active price | admin config, user browse | matches, seats, price snapshots | Admin/User clients, DB |
| ARCH-COMP-003 Order & Payment Module | Seat hold, checkout, pending confirmation, expiry scheduler | selected seats, payment completion, admin decision | orders, issued tickets | Inventory, Ticket, Audit |
| ARCH-COMP-004 Ticket & Scan Module | QR/e-ticket generation, scan atomic update, exchange | issued tickets, scan request, exchange request | ticket status | Order, Inventory, Audit |
| ARCH-COMP-005 Audit Module | Immutable audit records for admin-sensitive actions | domain action context | audit log records | All backend modules |
| User Web Match API Client | Typed client for match list/seat map, API timeout, local/dev fallback decision | `/api/v1/matches`, `/api/v1/matches/{id}/seats` | UI DTOs and fallback flag | User Website -> Backend / fallback dataset |

##### 3.4 C4 Source Asset

- **Draw.io/XML asset path**: `assets/c4-model-v2.drawio`
- **Status**: generated
- **Required views in source**: System Context, Container View, and Component View are represented in one editable source.
- **Connector routing**: source uses explicit connectors with `jumpStyle=arc`; connectors are routed around shapes.

#### 3b. Architecture Traceability Map

| FR / US | Primary Components / Contexts | APIs / Events | Sequence / Data Ownership Refs | Special Obligations / Notes |
|---|---|---|---|---|
| FR-001 / US-001 | ARCH-COMP-001 | API-001, API-002 | SEQ-001; ENT-001 owns users/sessions | Mock OTP; session timeout 15m |
| FR-002 / US-002 | ARCH-COMP-002, User Web Match API Client | API-003 | SEQ-002; ENT-002 owns matches | Local fallback allowed only for display; `OPEN_FOR_SALE` remains backend rule |
| FR-003 / US-003 | ARCH-COMP-002, User Web Match API Client | API-004 | SEQ-002; ENT-003 owns seats | Local fallback seat map is preview/display only; checkout requires backend |
| FR-004 / US-004 | ARCH-COMP-003 | API-005 | SEQ-003; ENT-004/ENT-005 own orders/order_items | Transaction + locks + Idempotency-Key |
| FR-005 / US-005 | ARCH-COMP-003 | API-006 | SEQ-003; ENT-004 owns pending order | Manual QR; pending admin confirm |
| FR-006 / US-006 | ARCH-COMP-002 | API-010 | SEQ-002; ENT-002 owns match status and optional presentation fields | Admin audit |
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
| Match & Inventory | Core | Match, presentation fields, seat, price, default QR config | Admin | Order, Ticket, clients |
| Order & Payment Confirmation | Core | Holds, orders, manual payment completion, admin confirmation, expiry | Auth, Inventory | Ticket, Audit |
| Ticket & Scan | Core | Issued tickets, QR token, scan, exchange | Order, Inventory | Clients, scan consumer |
| Audit | Supporting | Admin and sensitive action logs | All modules | Admin review / security evidence |

Context map: clients call Backend API; Backend modules communicate in-process through application services and domain events. User web local fallback is outside backend context, read-only, and cannot create business state. No direct cross-module DB access outside repositories owned by the module.

#### 5. Technology Stack

| Layer | Technology | Version | Reason | ADR Reference | On Approved List? |
|---|---|---|---|---|---|
| Backend | Java Spring Boot | TBD | Standards-preferred backend for business logic | ADR-001 | Yes |
| Database | PostgreSQL | TBD | Strong ACID, constraints, transactional ticket inventory | ADR-001 | Yes |
| User/Admin Web | Next.js + Tailwind | TBD | Existing user/admin surfaces and user-requested UI scope | ADR-001, ADR-004 | Partial: React allowed; Next.js business logic remains backend-owned |
| Mobile | Flutter | TBD | Existing broader product surface | ADR-001 | Allowed by frontend standards |
| Messaging | N/A for Kafka; in-process domain events | N/A | Demo does not need broker | ADR-001 | Yes with ADR |
| Cache | None required v2 | N/A | Local fallback is not production cache; DB remains source of truth | ADR-004 | N/A |
| Infrastructure | Docker Compose local | TBD | Demo local runtime | ADR-003 | N/A |
| CI/CD | Skipped for demo | N/A | User confirmed no CI/CD | ADR-003 | Exception |
| Unit test | JUnit 5 + Mockito; Flutter test; Vitest | TBD | Existing plan defaults | N/A | Yes |
| Integration/e2e | Testcontainers; Playwright | TBD | Verify backend contracts and UI fallback states | N/A | Yes |
| Error tracking | Skipped for demo | N/A | User confirmed | ADR-003 | Exception |

<!-- ID: ARCH-COMP-002 -->
### ARCH-COMP-002: Match & Inventory Module

- **Responsibility**: matches, optional match presentation fields, seat generation, seat state, active price versions, default transfer QR.
- **Owns**: matches, seats, price_versions, payment_qr_configs.
- **Exposes**: API-003, API-004, API-010, API-011, API-012.
- **Consumes**: PostgreSQL locks/constraints.
- **Scaling strategy**: single DB source of truth; no production cache in v2.
- **Failure mode**: inventory API failure prevents checkout; user web may display local fallback match/seat data only in local/dev browsing.

<!-- ID: ARCH-001 -->
### ARCH-001: Component Interaction Overview

All clients call Backend API over REST. User Website rewrites `/api/v1/*` to the backend API in local/dev so browser calls stay same-origin. Backend controllers delegate to application services inside module boundaries. Application services own transactions and call domain services/repositories. Cross-module calls use public application interfaces only; direct repository access across module boundaries is forbidden. PostgreSQL constraints enforce seat uniqueness, state guards, idempotency, and ownership. Local fallback data is isolated in the User Website typed match API client and cannot be used by checkout, payment completion, admin decision, ticket issuance, scan, or exchange mutation flows.

## Removed
