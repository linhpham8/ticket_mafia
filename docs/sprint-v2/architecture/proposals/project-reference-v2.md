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

# Project Reference Proposal — Sprint v2

## New

## Updated

<!-- ID: PR-001 -->
### PR-001: Monorepo Source Tree Contract

- **Purpose**: Define code-facing folder boundaries.
- **Owns**: repository structure.
- **Public Entrypoints**: `backend/`, `admins/`, `website/`, `apps/`.
- **Allowed dependencies**: clients depend on API contracts only; backend does not import client code.
- **Companion Refs**: ADR-001, ADR-004, ARCH-OVERVIEW-001.

```text
backend/   # Java Spring Boot modular monolith API
admins/    # Next.js + Tailwind Admin Web
website/   # Next.js + Tailwind User Web; local/dev read fallback for matches/seats
apps/      # Flutter iOS/Android app
docker-compose.yml
```

<!-- ID: PR-003 -->
### PR-003: REST API Naming And Error Contract

- **Purpose**: Establish stable API conventions.
- **Owns**: public HTTP surface.
- **Public Entrypoints**: `/api/v1/**`.
- **Allowed dependencies**: all clients call API service layer; no direct DB access.
- **Companion Refs**: API-001..API-016, ADR-004.

Rules: kebab-case paths, JSON camelCase fields, UTC timestamps, standard error envelope with `error.code`, `error.message`, `requestId`, `traceId`. User Website may proxy same-origin `/api/v1/*` requests to the backend in local/dev, but the backend REST contract remains the source of truth.

<!-- ID: PR-004 -->
### PR-004: Frontend Feature Boundary Contract

- **Purpose**: Keep web/admin/mobile aligned with API and design.
- **Owns**: UI project structure.
- **Public Entrypoints**: feature folders and typed API clients.
- **Allowed dependencies**: feature code uses typed service layer; no direct fetch inside components.
- **Companion Refs**: DESIGN-OVERVIEW-001, coding-standards-frontend, ADR-004.

Feature folders: `auth`, `matches`, `checkout`, `orders`, `tickets`, `exchange`, `adminMatches`, `adminInventory`, `adminConfirmations`.

Sprint v2 local fallback rule: only `website` match browsing services may return bundled/demo fallback data for API-003 and API-004 in local/dev after backend read failure or unusable empty demo response. Fallback state must expose UI-visible flags/hooks (`matches-demo-fallback`, `seat-map-demo-fallback`). Mutation services for checkout, payment completion, admin decisions, ticket scan, and exchange must not fallback.

## Removed
