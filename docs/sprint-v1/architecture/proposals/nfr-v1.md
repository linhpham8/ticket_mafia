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

# NFR Proposal — Sprint v1

## New

<!-- ID: NFR-001 -->
### NFR-001: Demo API Responsiveness

- **Category**: Performance
- **Target**: p95 API response <= 800ms under 50 concurrent demo users on local/dev-like environment.
- **Source**: Product demo scope open risk.
- **Priority**: Should have
- **Verification**: Basic API smoke/load check in Plan/Test.
- **Applies to**: all API endpoints.

Architecturally Significant Scenario: During a demo, up to 50 concurrent users browse matches and seats. System should keep p95 <= 800ms for successful requests, excluding first container cold start.

#### Implementation Configuration Mapping

| Config key | Recommended value | Owner |
|---|---|---|
| `server.tomcat.threads.max` | `100` | Backend |
| `spring.datasource.hikari.maximumPoolSize` | `20` | Backend |

<!-- ID: NFR-002 -->
### NFR-002: Seat Hold Consistency

- **Category**: Reliability
- **Target**: Zero double-active holds for the same seat in local/demo tests.
- **Source**: BR-002, BR-003, BR-004.
- **Priority**: Mandatory
- **Verification**: concurrent checkout integration tests with PostgreSQL/Testcontainers.
- **Applies to**: FR-003, FR-004.

Scenario: Two requests attempt to hold the same seat. System must allow only one active hold/order item through transaction, state guard, and unique constraint.

#### Implementation Configuration Mapping

| Config key | Recommended value | Owner |
|---|---|---|
| `ticketing.hold.duration` | `PT10M` | Backend |
| `ticketing.scheduler.release-expired-holds.cron` | every 1 minute | Backend |

<!-- ID: NFR-003 -->
### NFR-003: Session Security Baseline

- **Category**: Security
- **Target**: user/admin sessions expire after 15 minutes inactive; no passwords; no PII in ticket QR token.
- **Source**: Security standards + user confirmation.
- **Priority**: Mandatory
- **Verification**: auth/session tests and QR payload inspection.
- **Applies to**: auth, ticket detail, scan.

Scenario: An inactive user returns after 15 minutes. System requires re-authentication before protected action.

#### Implementation Configuration Mapping

| Config key | Recommended value | Owner |
|---|---|---|
| `security.session.inactive-timeout` | `PT15M` | Backend |
| `ticketing.qr.signing.alg` | `HMAC-SHA256` or stronger | Backend |

<!-- ID: NFR-004 -->
### NFR-004: Observability Demo Baseline

- **Category**: Observability
- **Target**: structured JSON logs include `request_id`, `trace_id`, `user_id` where available, operation, status, duration, and error code.
- **Source**: DevSecOps standards.
- **Priority**: Should have
- **Verification**: log sample review in local demo.
- **Applies to**: backend API and scheduler.

Scenario: Admin confirmation fails. Logs must allow tracing the request, order ID, admin user, and error code without exposing secrets/PII.

#### Implementation Configuration Mapping

| Config key | Recommended value | Owner |
|---|---|---|
| `logging.format` | `json` | Backend |
| `management.endpoints.web.exposure.include` | `health,metrics` | Backend |

<!-- ID: NFR-005 -->
### NFR-005: Local Docker Compose Self-Test

- **Category**: Operations
- **Target**: local Docker Compose starts backend, PostgreSQL, website, and admin web with health checks.
- **Source**: User confirmed Docker Compose; CODE-10 downstream.
- **Priority**: Mandatory for implementation runtime scope.
- **Verification**: `docker compose up` + health endpoint + happy-path smoke commands.
- **Applies to**: full runtime.

Scenario: New developer runs local demo. Services must start and expose documented URLs without cloud dependencies.

#### Implementation Configuration Mapping

| Config key | Recommended value | Owner |
|---|---|---|
| `docker.compose.profile` | `local` | Dev |
| `spring.profiles.active` | `local` | Backend |

## Updated

## Removed

