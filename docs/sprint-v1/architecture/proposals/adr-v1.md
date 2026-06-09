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

# ADR Proposal — Sprint v1

## New

<!-- ID: ADR-001 -->
### ADR-001 — Use Monorepo Modular Monolith For Demo

#### Context

Product needs iOS/Android/Web/Admin clients plus an API for online football ticket sales. User requested `backend/`, `admins/`, `website/`, and `apps/` folders, with every client calling API. User initially said microservice, then confirmed option 1A: Modular Monolith backend.

#### Options Considered

| Option | Pros | Cons |
|---|---|---|
| Modular Monolith backend | Fast demo delivery, simpler local Docker Compose, one DB transaction boundary for seat holds | Cannot scale services independently |
| True microservices | Independent service deploy/scale, clear network boundaries | Too much complexity for demo, distributed consistency, observability burden |

#### Decision

Use one Java Spring Boot modular monolith backend in `backend/`, with internal modules and PostgreSQL. Keep clients in separate monorepo folders.

#### Consequences

| Positive | Negative |
|---|---|
| Strong transaction control for seat holds and ticket scan | Later migration to services requires boundary extraction |
| Simpler local setup | Module discipline must be enforced by package boundaries |

#### Reversibility

- **Cost**: Medium.
- **Revisit trigger**: Production scale, separate teams, or independent service deployment becomes required.

#### Follow-up

- **Affected artifacts**: architecture, project-reference, ERD, API specs, plan.
- **Revisit trigger**: Need to split `order_payment` or `ticket_scan` into deployable services.

<!-- ID: ADR-002 -->
### ADR-002 — Demo-Only Internal OTP And No Admin MFA

#### Context

Security standards prefer Central IAM/AuthOM/Keycloak and MFA for admin. User confirmed demo-only internal/mock OTP and no admin MFA.

#### Options Considered

| Option | Pros | Cons |
|---|---|---|
| Central IAM + MFA | Standards compliant, production ready | More setup than demo needs |
| Internal mock OTP, no admin MFA | Fast demo, simple integration | Not production compliant |

#### Decision

Use internal mock OTP for demo and no admin MFA, with 15-minute inactive session timeout. Record this as a demo-only exception.

#### Consequences

| Positive | Negative |
|---|---|
| Faster demo delivery | Must not be treated as production security |
| Simple local environment | Security rework required before production |

#### Reversibility

- **Cost**: Medium.
- **Revisit trigger**: Any production or external pilot deployment.

#### Follow-up

- **Affected artifacts**: API, NFR, project-reference.
- **Revisit trigger**: Need real SMS/email OTP, Central IAM, or admin MFA.

<!-- ID: ADR-003 -->
### ADR-003 — Demo Local Deployment, No CI/CD Or Error Tracking

#### Context

User confirmed Docker Compose for local/dev, no cloud provider, no CI/CD, and skip frontend error tracking for demo. DevSecOps standards normally require CI/CD, scans, observability, and error tracking.

#### Options Considered

| Option | Pros | Cons |
|---|---|---|
| Full CI/CD + Sentry | Standards aligned | Overhead for demo |
| Docker Compose only | Fast local verification | Not release-ready |

#### Decision

Use Docker Compose local deployment for v1 demo and document CI/CD/error-tracking as out of scope until productionization.

#### Consequences

| Positive | Negative |
|---|---|
| Easy local run | No automated deployment governance |
| Lower demo setup cost | Manual quality controls only |

#### Reversibility

- **Cost**: Low to medium.
- **Revisit trigger**: Handoff to delivery team or deployment beyond local demo.

#### Follow-up

- **Affected artifacts**: NFR, project-reference, plan.
- **Revisit trigger**: Non-demo environment required.

## Updated

## Removed

