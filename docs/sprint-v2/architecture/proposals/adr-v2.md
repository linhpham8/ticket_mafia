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

# ADR Proposal — Sprint v2

## New

<!-- ID: ADR-004 -->
### ADR-004 — Keep Local Demo Fallback In User Web Read Layer Only

#### Context

Sprint v2 product/design requires the user match list and seat map to stop appearing blank when the local backend is unavailable or unseeded. The same sprint does not authorize new business lifecycle rules, production queueing, payment gateway integration, or backend-generated fake data.

#### Options Considered

| Option | Pros | Cons |
|---|---|---|
| Backend seed data only | Keeps all responses authoritative | Still blank when backend is stopped or failed; does not solve local API issue |
| User Web read-layer fallback for matches/seats | Fast demo resilience; no DB mutation risk; visible fallback state can be tested | Must be carefully isolated from checkout/payment |
| Backend fallback/fake data | Same API shape for all clients | Risks masking backend/data failures and polluting business semantics |

#### Decision

Implement local/dev fallback only in the User Website typed match API client for API-003 and API-004 display data. The fallback must set visible UI state and must not be accepted by checkout, payment completion, admin decision, ticket issuance, ticket scan, or exchange flows.

#### Consequences

| Positive | Negative |
|---|---|
| Match browsing demo remains usable when local backend is unavailable | User web has a demo-only branch that tests must constrain |
| Backend remains source of truth for business state | Production readiness later needs stronger API availability instead of fallback |

#### Reversibility

- **Cost**: Low.
- **Revisit trigger**: Production deployment, shared demo environments, or requirement that all UI data be backend-authoritative.

#### Follow-up

- **Artifacts affected**: architecture, project-reference, sequence, data-flow, api-specs, nfr, implementation plan, frontend tests.
- **Revisit trigger**: Add queue/waiting room, anti-bot, production CDN/cache, or backend seed-data service.

## Updated

## Removed
