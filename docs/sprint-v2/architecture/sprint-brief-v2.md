---
status: APPROVED
version: v2
sprint: 2
phase: architecture
sprint_id: sprint-v2
created: 2026-06-09
updated: 2026-06-09 14:03
approved_by: user
---

# Architecture Sprint Brief — Sprint v2

## 1. Scope

Sprint v2 keeps the approved v1 modular-monolith architecture and updates the architecture package for the Product/Design v2 UI and runtime-resilience scope.

## 2. Architecture Direction

| Area | Decision |
|---|---|
| Architecture style | Keep Java Spring Boot modular monolith with PostgreSQL. |
| User/Admin clients | Keep Next.js + Tailwind user web and admin web. |
| API surface | Keep REST `/api/v1`; enrich read DTOs for marketplace UI where needed. |
| Local fallback | Allow user web local/dev fallback data only for match list and seat map display. |
| Mutation safety | Checkout, payment completion, admin decision, ticket issuance, scan, and exchange still require backend availability and DB state guards. |
| Production readiness | No payment gateway, queue/waiting-room, anti-bot layer, broker, production IAM, CI/CD, or cloud deployment in Sprint v2. |

## 3. Industry Lens

Industry vertical = ticketing / football ticket sales. Confirmed Sprint v2 concerns:

| Tag | Concern | Architecture Handling |
|---|---|---|
| `[common]` | Inventory holds | unchanged v1 transaction and idempotency contract |
| `[common]` | Marketplace read experience | richer match/seat read DTOs, optional presentation fields |
| `[common]` | Local demo confidence | local fallback read-only display path |
| `[industry-standard]` | Anti-bot / waiting room | out of scope; recorded as production-readiness trigger |
| `[industry-standard]` | Payment reconciliation | out of scope; manual transfer remains admin-confirmed |

## 4. Reviewer Notes

- The fallback path is explicitly a client-side local/dev resilience behavior, not a backend production behavior.
- Optional presentation fields on `matches` support ticket marketplace UI without changing purchase lifecycle rules.
- Draw.io/XML C4 and DFD sources are generated for Sprint v2 under `assets/`.
