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
---

# Architecture Sprint Brief — v1

## 1. Architecture Rationale

Architecture v1 translates the approved Product package into a demo-oriented but code-ready modular monolith. The chosen structure is a monorepo with `backend/`, `admins/`, `website/`, and `apps/`, where every client calls the backend API.

The backend is one Java Spring Boot application with internal modules for auth, match/inventory, orders/manual payment confirmation, tickets/scanning, admin operations, and audit. PostgreSQL is the transactional source of truth. Docker Compose is required for local development.

## 2. Confirmed Decisions

- Backend: Java Spring Boot.
- Database: PostgreSQL.
- User/Admin web: Next.js + Tailwind, custom Material-style components.
- Mobile: Flutter.
- Architecture style: Modular Monolith backend in a monorepo.
- Auth: mock/internal OTP for demo; no SMS/email provider.
- Admin MFA and Central IAM are demo-only exceptions.
- External `Idempotency-Key` header is required for checkout/payment-completed/admin-confirm/scan/exchange mutation endpoints.
- No Kafka/event bus for v1; use in-process domain events and scheduler jobs.
- Local dev uses Docker Compose; cloud and CI/CD are out of scope for demo.

## 3. Reviewer Notes

- Security-standard deviations are captured as ADR-002 and must be revisited before production.
- CI/CD is skipped for demo and captured as ADR-003 because DevSecOps standards normally require a pipeline.
- C4 and DFD Draw.io sources are generated under `architecture/assets/`.

