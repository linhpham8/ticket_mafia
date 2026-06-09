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

# NFR Proposal — Sprint v2

## New

## Updated

<!-- ID: NFR-001 -->
### NFR-001: Demo API Responsiveness

- **Category**: Performance
- **Target**: p95 backend API response <= 800ms under 50 concurrent demo users on local/dev-like environment; user web local match list and seat-map display should render useful populated or fallback state within 2 seconds when backend read data is unavailable.
- **Source**: Product demo scope open risk; AC-026; AC-028.
- **Priority**: Should have
- **Verification**: Basic API smoke/load check, frontend fallback unit tests, and Playwright browser check for `matches-demo-fallback` / `seat-map-demo-fallback`.
- **Applies to**: API-003, API-004, user web match list, user web seat map.

Architecturally Significant Scenario: During a local stakeholder demo, backend is down or has no useful seed data. User Website should render the match list or seat map with visible fallback copy within 2 seconds, while checkout remains blocked until backend is available.

#### Implementation Configuration Mapping

| Config key | Recommended value | Owner |
|---|---|---|
| `server.tomcat.threads.max` | `100` | Backend |
| `spring.datasource.hikari.maximumPoolSize` | `20` | Backend |
| `NEXT_PUBLIC_TICKET_MAFIA_API_BASE_URL` | `http://127.0.0.1:8080` for local default | User Website |
| `ticketing.userWeb.readFallbackTimeoutMs` | `2000` | User Website |

<!-- ID: NFR-005 -->
### NFR-005: Local Docker Compose Self-Test

- **Category**: Operations
- **Target**: local Docker Compose starts backend, PostgreSQL, website, and admin web with health checks; user web can still show local fallback match/seat display when backend is intentionally stopped during UI demo, but mutation smoke tests require backend running.
- **Source**: User confirmed Docker Compose; CODE-10 downstream; Sprint v2 local runtime issue.
- **Priority**: Mandatory for implementation runtime scope.
- **Verification**: `docker compose up` + health endpoint + happy-path smoke commands + UI fallback browser check.
- **Applies to**: full runtime.

Architecturally Significant Scenario: New developer runs the local demo. Services must start and expose documented URLs without cloud dependencies. If backend is not ready, user web browsing shows demo fallback state; admin and all mutations show explicit backend error/retry.

#### Implementation Configuration Mapping

| Config key | Recommended value | Owner |
|---|---|---|
| `docker.compose.profile` | `local` | Dev |
| `spring.profiles.active` | `local` | Backend |
| `NEXT_PUBLIC_TICKET_MAFIA_API_BASE_URL` | `http://127.0.0.1:8080` | User/Admin Web |

## Removed
