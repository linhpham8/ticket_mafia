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

# Sequence Proposal — Sprint v1

## New

<!-- ID: SEQ-001 -->
### SEQ-001: OTP Login

Reference: FR-001, API-001, API-002.

```mermaid
sequenceDiagram
    participant U as User
    participant C as Client
    participant API as Backend API
    participant DB as PostgreSQL
    U->>C: Enter email/phone
    C->>API: POST /api/v1/auth/otp/request
    API->>DB: Store mock OTP challenge
    API-->>C: challengeId, expiresAt
    U->>C: Enter OTP
    C->>API: POST /api/v1/auth/otp/verify
    API->>DB: Validate challenge
    API->>DB: Create session
    API-->>C: accessToken, user, expiresAt
```

Notes: mock OTP does not integrate SMS/email provider. Session inactive timeout is 15 minutes.

<!-- ID: SEQ-002 -->
### SEQ-002: Admin Match Inventory Setup And User Browsing

Reference: FR-002, FR-003, FR-006, FR-007; API-003, API-004, API-010, API-011, API-012.

```mermaid
sequenceDiagram
    participant A as Admin
    participant C as Admin Web
    participant API as Backend API
    participant DB as PostgreSQL
    A->>C: Create match / generate seats / set prices
    C->>API: POST admin match/seat/price endpoints
    Note over API: [IDEMPOTENT: key=Idempotency-Key]
    Note over API: [TX BEGIN]
    API->>DB: INSERT/UPDATE matches, seats, price_versions
    API->>DB: INSERT audit_logs
    Note over API: [TX COMMIT]
    API-->>C: updated config
    A->>C: Set default QR
    C->>API: configure payment_qr_configs
    C-->>A: config saved
```

Browsing path: user client calls `GET /matches` and `GET /matches/{id}/seats`; backend reads only open-for-sale matches and current prices.

<!-- ID: SEQ-003 -->
### SEQ-003: Checkout Hold And Payment Completion

Reference: FR-004, FR-005, FR-011; API-005, API-006, API-014.

```mermaid
sequenceDiagram
    participant U as User
    participant C as Client
    participant API as Backend API
    participant DB as PostgreSQL
    U->>C: Select 1-5 seats and tap checkout
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
    Note over API: [TX BEGIN]
    API->>DB: Verify order HELD and not expired
    API->>DB: UPDATE order -> PENDING_ADMIN_CONFIRM
    API->>DB: UPDATE seats -> PENDING_ADMIN_CONFIRM
    Note over API: [TX COMMIT]
    API-->>C: pending, adminConfirmExpiresAt
```

Error path: expired hold rolls back payment completion and requires new order; duplicate idempotency key returns prior result for same request hash.

<!-- ID: SEQ-004 -->
### SEQ-004: Admin Confirmation And Exchange Confirmation

Reference: FR-008, FR-012; API-007, API-015.

```mermaid
sequenceDiagram
    participant A as Admin
    participant C as Admin Web
    participant API as Backend API
    participant DB as PostgreSQL
    A->>C: Confirm or reject pending order
    C->>API: POST decision + Idempotency-Key
    Note over API: [IDEMPOTENT: key=scope+Idempotency-Key]
    Note over API: [TX BEGIN]
    API->>DB: Lock order and order_items
    alt Confirm purchase
      API->>DB: INSERT tickets
      API->>DB: UPDATE order -> ISSUED
      API->>DB: UPDATE seats -> ISSUED
    else Confirm exchange
      API->>DB: INSERT new ticket
      API->>DB: UPDATE old ticket -> EXCHANGED
      API->>DB: UPDATE old seat -> AVAILABLE
      API->>DB: UPDATE new seat -> ISSUED
    else Reject/expired
      API->>DB: UPDATE order -> REJECTED/CANCELLED
      API->>DB: UPDATE seats -> AVAILABLE
    end
    API->>DB: INSERT audit_logs
    Note over API: [TX COMMIT]
    API-->>C: decision result
```

Error path: non-pending order, expired confirmation, or mismatched request hash returns conflict; no ticket state changes.

<!-- ID: SEQ-005 -->
### SEQ-005: Ticket Detail And One-Time Scan

Reference: FR-009, FR-010; API-008, API-009, API-013.

```mermaid
sequenceDiagram
    participant U as User
    participant C as Client / Scanner
    participant API as Backend API
    participant DB as PostgreSQL
    U->>C: Open ticket detail
    C->>API: GET /api/v1/tickets/{ticketId}
    API->>DB: Load user-owned ticket
    API-->>C: QR/e-ticket if ISSUED
    C->>API: POST /api/v1/tickets/scan + Idempotency-Key
    Note over API: [IDEMPOTENT: key=scope+Idempotency-Key]
    Note over API: [TX BEGIN]
    API->>DB: Lock ticket FOR UPDATE
    API->>DB: Verify status ISSUED
    API->>DB: UPDATE ticket -> USED_SCANNED
    API->>DB: INSERT audit_logs
    Note over API: [TX COMMIT]
    API-->>C: scanned success
```

Error path: already scanned/exchanged/cancelled ticket returns 409 and no state change.

## Updated

## Removed

