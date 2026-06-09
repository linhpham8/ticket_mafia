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

# Event Contracts Proposal — Sprint v2

## New

## Updated

<!-- ID: EVT-001 -->
### EVT-001: SeatHeld

- **Purpose**: In-process domain event emitted after backend-owned seats are held for an order.
- **Publisher**: Order & Payment Module.
- **Consumers**: Audit Module; optional future notification hook.
- **Delivery guarantee**: in-process within transaction for v2.
- **Ordering requirement**: Yes, per order.
- **Idempotency expectation**: consumer treats `orderId` as business idempotency key.
- **Sprint v2 note**: local fallback seat rows never emit this event because fallback cannot create holds or orders.

#### Payload Schema

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `eventId` | UUID | Yes | unique event ID | `"evt-uuid"` |
| `occurredAt` | ISO UTC datetime | Yes | business occurrence time | `"2026-06-08T05:12:00Z"` |
| `traceId` | string | Yes | trace correlation | `"trace-123"` |
| `requestId` | string | Yes | originating request ID | `"req-123"` |
| `orderId` | UUID | Yes | held order | `"order-uuid"` |
| `userId` | UUID | Yes | buyer | `"user-uuid"` |
| `seatIds[]` | UUID[] | Yes | held backend seats | `["seat-1"]` |
| `expiresAt` | ISO UTC datetime | Yes | hold expiry | `"2026-06-08T05:22:00Z"` |

#### Messaging Contract

Kafka Contract: N/A — no Kafka/event bus in v2 demo. Event is an in-process application event.

#### Failure Handling

| Field | Value |
|---|---|
| Publish failure persistence | Same transaction; no separate broker persistence |
| Retry policy | N/A — transaction rollback on critical consumer failure |
| Replay required | No for v2 |
| Replay window / TTL | N/A |
| Max delivery / replay attempts | 1 in-process attempt |
| DLQ behavior | N/A — no broker; failed audit write rolls back the seat hold |

## Removed
