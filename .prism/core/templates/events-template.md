---
status: DRAFT
version: v1
sprint: 1
phase: architecture
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# Event Contracts — {{PROJECT_NAME}}

<!-- Living Truth root for event contracts. Each event is a mergeable anchored block. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each EVT-NNN block in §2 MUST be preceded by `<!-- ID: EVT-NNN -->` on its own line
     above the `### EVT-NNN: {EventName}` heading.
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type EVT`
     Strict format: `EVT-\d{3,}` (zero-padded ≥3 digits). -->

<!-- PRISM:LT-SKELETON-END -->

## 1. Event Catalog

<!-- Bảng index — mỗi row đối ứng 1 EVT-NNN block ở §2. -->

| Event ID | Event | Publisher | Consumers | Trigger |
|---|---|---|---|---|
| EVT-NNN | | | | |

## 2. Event Specifications (anchored, mergeable)

<!-- ID: EVT-NNN -->
### EVT-NNN: {{EVENT_NAME}} *(VD: OrderPlaced)*

- **Purpose**: <!-- Tại sao event này tồn tại, bối cảnh business -->
- **Publisher**: <!-- Component/service phát ra event -->
- **Consumers**: <!-- Component/service nào consume event này -->
- **Delivery guarantee**: <!-- at-least-once / at-most-once / exactly-once intent -->
- **Ordering requirement**: <!-- Yes (per partition_key) / No — quan trọng với Kafka partition -->
- **Idempotency expectation**: <!-- Consumer phải idempotent vì delivery guarantee là at-least-once -->

### Payload Schema

<!-- BẮTBUỘC: `"data": {}` là KHÔNG ĐỦ để viết consumer. Phải có field-level types. -->
<!-- Tương tự api-specs — mỗi field phải có type, required, description. -->

| Field | Type | Required | Description | Example |
|---|---|---|---|---|
| `event_id` | UUID | Có | Unique ID của event — dùng cho idempotency check | `"550e8400-..."` |
| `occurred_at` | string (ISO 8601 UTC) | Có | Thời điểm event xảy ra (không phải thời điểm publish) | `"2026-04-19T10:00:00Z"` |
| `version` | string | Có | Schema version — consumer cần check để handle backward compat | `"1.0"` |
| `trace_id` | string | Có | Trace ID xuyên suốt để correlate với logs (OpenTelemetry) — bắt buộc per `devsecops-standards.md §2.3` | `"abc123"` |
| `request_id` | string | Có | Request ID khởi nguồn chuỗi xử lý — correlate với API logs | `"req-550e8400"` |
| `data.order_id` | UUID | Có | ID của order | |
| `data.user_id` | UUID | Có | ID của user đặt hàng | |
| `data.total_amount` | decimal | Có | Tổng giá trị đơn hàng — precision (10,2) | `150000.00` |
| `data.status` | enum | Có | Trạng thái order lúc event xảy ra | `"PENDING"` |
| `data.items` | array | Có | minItems=1 — danh sách sản phẩm | |
| `data.items[].product_id` | UUID | Có | | |
| `data.items[].quantity` | integer | Có | min=1 | |
| `data.items[].unit_price` | decimal | Có | precision (10,2) | |

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "occurred_at": "2026-04-19T10:00:00Z",
  "version": "1.0",
  "trace_id": "abc123",
  "request_id": "req-550e8400",
  "data": {
    "order_id": "order-uuid",
    "user_id": "user-uuid",
    "total_amount": 150000.00,
    "status": "PENDING",
    "items": [
      { "product_id": "prod-uuid", "quantity": 2, "unit_price": 75000.00 }
    ]
  }
}
```

### Kafka Contract

<!-- Điền nếu dùng Kafka. Ghi "N/A — [messaging system khác]" nếu không dùng Kafka. -->

| Attribute | Value | Lý do |
|---|---|---|
| **Topic name** | `{domain}.{entity}.{event}` VD: `orders.order.placed` | Naming convention: lowercase, dấu chấm phân cách domain |
| **Partition key** | `order_id` | Đảm bảo ordering: các events của cùng 1 order đến cùng partition |
| **Consumer group** | `{service}-{env}-consumer` VD: `notification-prod-consumer` | Mỗi service có consumer group riêng để consume độc lập |
| **Serialization** | JSON *(default)* / Avro + Schema Registry | Avro khi cần strict schema evolution |
| **Schema Registry** | <!-- Confluent Schema Registry URL nếu dùng Avro --> | |
| **Retention** | `7 days` *(default)* / `{{RETENTION_DAYS}} days` | Đủ cho replay trong trường hợp consumer down |
| **Replication factor** | `3` *(production)* | HA requirement |

> **Assumption**: <!-- VD: "Dùng JSON serialization. Nếu cần schema evolution strict → migrate sang Avro + Schema Registry." -->  
> **Change trigger**: <!-- VD: "Nếu thêm consumer mới cần backward compat → bump version field, đừng break existing fields." -->

### Failure Handling

- **Publish failure persistence**: <!-- outbox pattern / store-forward / best-effort -->
- **Retry policy**: <!-- VD: 3 retries, exponential backoff 100ms/200ms/400ms -->
- **Replay required**: <!-- Yes/No và trigger scenario -->
- **Replay window / TTL**: <!-- VD: 7 ngày — khớp với Kafka retention -->
- **Max delivery / replay attempts**: <!-- VD: 5 attempts per event -->
- **Dead-letter behavior**: <!-- DLQ topic name, alert threshold, manual replay process -->

**DLQ Contract:**
- DLQ topic: `{original_topic}.dlq` VD: `orders.order.placed.dlq`
- DLQ message envelope: gồm original payload + `{ "error_reason": "...", "retry_count": N, "failed_at": "..." }`
- Alert owner: <!-- Team / Slack channel -->
- Alert trigger: <!-- VD: DLQ message count > 10 trong 5 phút -->

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ARCH-1`
- [ ] Mọi async integration event đều được list trong §1 Event Catalog
- [ ] Publisher / consumer ownership explicit
- [ ] Delivery semantics documented (at-least-once là default với Kafka)
- [ ] Mỗi event có Payload Schema với field-level types — không có `"data": {}` trống
- [ ] Kafka Contract đầy đủ: topic name, partition key, consumer group, serialization, retention
- [ ] DLQ Contract defined: DLQ topic name, envelope format, alert owner
- [ ] Replay contract defined: required scenarios, TTL, max attempts
- [ ] Failure handling defined
- [ ] Assumption blocks cho quyết định messaging design quan trọng
