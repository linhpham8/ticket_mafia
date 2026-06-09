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

# Sequence Proposal — Sprint v2

## New

## Updated

<!-- ID: SEQ-002 -->
### SEQ-002: Admin Match Inventory Setup And User Browsing

Reference: FR-002, FR-003, FR-006, FR-007; API-003, API-004, API-010, API-011, API-012.

```mermaid
sequenceDiagram
    participant A as Admin
    participant AdminWeb as Admin Web
    participant UserWeb as User Website
    participant API as Backend API
    participant DB as PostgreSQL
    participant Fallback as Local Demo Dataset

    A->>AdminWeb: Create match / set presentation fields / generate seats / set prices
    AdminWeb->>API: POST admin match/seat/price endpoints
    Note over API: [IDEMPOTENT: key=Idempotency-Key]
    Note over API: [TX BEGIN]
    API->>DB: INSERT/UPDATE matches, seats, price_versions
    API->>DB: INSERT audit_logs
    Note over API: [TX COMMIT]
    API-->>AdminWeb: updated config

    UserWeb->>API: GET /api/v1/matches
    alt Backend returns usable open matches
      API->>DB: Read OPEN_FOR_SALE matches with presentation fields
      API-->>UserWeb: match cards DTO
    else Local/dev backend unavailable or unseeded
      Note over UserWeb,Fallback: [TO: 2000ms] read fallback only in local/dev
      UserWeb->>Fallback: Load bundled demo matches
      Fallback-->>UserWeb: demo match cards + fallback flag
    end

    UserWeb->>API: GET /api/v1/matches/{matchId}/seats
    alt Backend returns seat map
      API->>DB: Read seats and current prices
      API-->>UserWeb: seat map DTO
    else Local/dev backend unavailable for read path
      Note over UserWeb,Fallback: [TO: 2000ms] read fallback only in local/dev
      UserWeb->>Fallback: Load bundled demo seats
      Fallback-->>UserWeb: demo seat map + fallback flag
    end
```

Notes:
- Local fallback is read-only and owned by User Website service layer.
- Fallback does not create holds, orders, tickets, payment state, audit logs, or idempotency records.
- Checkout from fallback seat map is disabled or returns explicit backend-required UI copy.

<!-- ID: SEQ-003 -->
### SEQ-003: Checkout Hold And Payment Completion

Reference: FR-004, FR-005, FR-011; API-005, API-006, API-014.

```mermaid
sequenceDiagram
    participant U as User
    participant C as Client
    participant API as Backend API
    participant DB as PostgreSQL
    U->>C: Select 1-5 backend-backed seats and tap checkout
    C->>API: POST /api/v1/orders/checkout + Idempotency-Key
    Note over API: [IDEMPOTENT: key=scope+Idempotency-Key]
    Note over API: [TX BEGIN]
    API->>DB: Lock seats FOR UPDATE
    API->>DB: Verify AVAILABLE and active price
    API->>DB: INSERT orders/order_items/idempotency_records
    API->>DB: UPDATE seats -> HELD
    Note over API: [TX COMMIT]
    API-->>C: orderId, holdExpiresAt, QR, total
    U->>C: Transfer manually and tap completed
    C->>API: POST /orders/{orderId}/payment-completed + Idempotency-Key
    Note over API: [IDEMPOTENT: key=scope+Idempotency-Key]
    Note over API: [TX BEGIN]
    API->>DB: Verify order HELD and not expired
    API->>DB: UPDATE order -> PENDING_ADMIN_CONFIRM
    API->>DB: UPDATE seats -> PENDING_ADMIN_CONFIRM
    Note over API: [TX COMMIT]
    API-->>C: pending, adminConfirmExpiresAt
```

Error path: expired hold rolls back payment completion and requires a new order; duplicate idempotency key returns prior result for same request hash. No fallback path is allowed for checkout or payment completion.

## Removed
