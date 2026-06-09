---
status: DRAFT
version: v1
sprint: 1
phase: architecture
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# API Specifications — {{PROJECT_NAME}}

<!-- Living Truth root for API specs. Each endpoint is a mergeable anchored block. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each API-NNN endpoint block in §2 MUST be preceded by `<!-- ID: API-NNN -->` on its own line
     above the `### API-NNN: {METHOD PATH}` heading.
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type API`
     Strict format: `API-\d{3,}` (zero-padded ≥3 digits). -->

<!-- PRISM:LT-SKELETON-END -->

## 1. Global Conventions

<!-- Tham chiếu bắt buộc: `prism/core/standards/coding-standards-backend.md` -->
<!-- Mọi quyết định naming/format dưới đây PHẢI nhất quán với coding standards. -->

| Convention | Value | Standards Reference |
|---|---|---|
| Base URL | `{{API_BASE_URL}}/api/v1` | URL phải có version prefix |
| Protocol | HTTPS only | TLS 1.2+ |
| Authentication | Bearer token / session / other | coding-standards-backend.md §Auth |
| Response field naming | **camelCase** | coding-standards-backend.md §3.6 |
| Date / time format | **ISO 8601 UTC** (VD: `2026-04-19T10:00:00Z`) | coding-standards-backend.md §3.6 |
| Error response format | `{ "code": "ERROR_CODE", "message": "...", "details": [] }` | coding-standards-backend.md §3.6 |
| Pagination | Cursor-based cho large datasets (> 10k records); offset-based cho nhỏ hơn | |
| Standard HTTP status codes | 200 OK / 201 Created / 204 No Content / 400 Bad Request / 401 Unauthorized / 403 Forbidden / 404 Not Found / 409 Conflict / 422 Unprocessable / 429 Too Many Requests / 500 Internal Server Error | |

> **Assumption**: <!-- Giả định về auth model, versioning strategy. VD: "Dùng Bearer JWT, single version /api/v1. Nếu cần v2 → new sprint + breaking change." --><br>
> **Validate**: <!-- Ai xác nhận? --><br>
> **Change trigger**: <!-- VD: "Nếu thêm API key auth cho partners → revisit Global Conventions." -->

## 2. Endpoints (anchored, mergeable)

<!-- One anchored block per endpoint. Group by domain via H2 (Domain: ...) but each endpoint is independently anchored. -->

### Domain: {{DOMAIN_NAME}}

<!-- ID: API-NNN -->
### API-NNN: `{{METHOD}} {{PATH}}`

| Attribute | Value |
|---|---|
| Auth | Required / Optional |
| Roles | |
| Idempotent | Yes / No |
| Rate limit | |

#### Query Parameters (for collection endpoints)

| Capability | Supported? | Format / Allowed values |
|---|---|---|
| Filter | Yes / No | |
| Sort | Yes / No | |
| Field selection | Yes / No | |
| Pagination | Cursor / offset / none | |

#### Request Body Schema

<!-- BẮTBUỘC: Không được để placeholder JSON đơn giản — phải có field-level detail. -->
<!-- Placeholder JSON `{ "field": "value" }` là KHÔNG ĐỦ để developer viết DTO và validation. -->

| Field | Type | Required | Validation | Default | Example |
|---|---|---|---|---|---|
| `name` | string | Có | maxLength=100, không chứa ký tự HTML | — | `"Nguyen Van A"` |
| `email` | string | Có | format=email, maxLength=255 | — | `"user@example.com"` |
| `status` | enum | Không | values=[ACTIVE, INACTIVE, PENDING] | `PENDING` | `"ACTIVE"` |
| `birthDate` | string | Không | format=ISO 8601 date (YYYY-MM-DD) | — | `"1990-01-15"` |
| `metadata` | object | Không | — | `{}` | `{"key": "value"}` |
| `metadata.key` | string | Có (nếu metadata present) | maxLength=50 | — | `"theme"` |
| `metadata.value` | string | Có (nếu metadata present) | maxLength=200 | — | `"dark"` |

```json
{
  "name": "Nguyen Van A",
  "email": "user@example.com",
  "status": "PENDING",
  "birthDate": "1990-01-15",
  "metadata": { "key": "theme", "value": "dark" }
}
```

#### Response Body Schema

| Field | Type | Always Present | Description |
|---|---|---|---|
| `data` | object / array | Có | Payload chính |
| `data.id` | string (UUID) | Có | ID duy nhất |
| `data.createdAt` | string (ISO 8601) | Có | Thời điểm tạo |
| `meta` | object | Với collection endpoints | Pagination info |
| `meta.total` | number | Có (collection) | Tổng số records |
| `meta.nextCursor` | string / null | Có (cursor pagination) | Cursor cho page tiếp theo |

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Nguyen Van A",
    "email": "user@example.com",
    "status": "PENDING",
    "createdAt": "2026-04-19T10:00:00Z"
  }
}
```

#### Errors

<!-- BẮTBUỘC: Liệt kê đầy đủ error codes có thể xảy ra cho endpoint này — không phải chỉ "200/400". -->

| Status | Code | Condition | Details |
|---|---|---|---|
| 400 | `VALIDATION_ERROR` | Request body có field không hợp lệ | `details` array chứa per-field errors |
| 401 | `UNAUTHORIZED` | Token thiếu hoặc invalid | |
| 403 | `FORBIDDEN` | Token hợp lệ nhưng không có quyền | |
| 404 | `NOT_FOUND` | Resource không tồn tại | |
| 409 | `{{DOMAIN_CONFLICT_CODE}}` | VD: EMAIL_DUPLICATE, USERNAME_TAKEN | Domain-specific |
| 422 | `INVALID_STATE` | Business rule violation | VD: không thể cancel DELIVERED order |
| 429 | `RATE_LIMIT_EXCEEDED` | Vượt rate limit | Header `Retry-After: <seconds>` |
| 500 | `INTERNAL_ERROR` | Lỗi hệ thống không xác định | Không expose internal error details |

---

## 3. Error Code Catalog

<!-- Centralized list — tất cả error codes dùng trong toàn API (không chỉ per endpoint). -->
<!-- Dùng để generate ErrorCode enum / constants trong code. -->
<!-- NAMING CONVENTION: SCREAMING_SNAKE_CASE, prefix theo domain. -->
<!-- Mỗi code map tới một entry trong backend `errors.yml` (coding-standards-backend.md §6.1) với
     đầy đủ field: `message_key`, `retryable`, `retry_after_seconds`, `category`. Bảng này là TÀI LIỆU
     — hiển thị `Retryable` + `Category` để người đọc hiểu hành vi từng lỗi. Error RESPONSE runtime
     (§4 / coding-standards-backend §3.6, §6.3) có thể gọn hơn: KHÔNG bắt buộc trả `retryable`/`category`
     cho client (chúng là metadata catalog, không phải payload bắt buộc của response). -->

### Authentication & Authorization

| Code | HTTP Status | Condition | Retryable | Category |
|---|---|---|---|---|
| `UNAUTHORIZED` | 401 | Token missing, invalid, hoặc expired | No | Auth |
| `FORBIDDEN` | 403 | Token valid nhưng không có quyền với resource này | No | Auth |
| `TOKEN_EXPIRED` | 401 | JWT đã hết hạn — client cần refresh | No (refresh token trước) | Auth |
| `INSUFFICIENT_PERMISSIONS` | 403 | Role không đủ quyền cho action | No | Auth |

### Validation

| Code | HTTP Status | Condition | Retryable | Category |
|---|---|---|---|---|
| `VALIDATION_ERROR` | 400 | Request body / params vi phạm validation rules | No | Validation |
| `INVALID_FORMAT` | 400 | Field có type/format sai (VD: không phải UUID, không phải email) | No | Validation |
| `MISSING_REQUIRED_FIELD` | 400 | Required field bị thiếu | No | Validation |

### Business Rules

| Code | HTTP Status | Condition | Retryable | Category |
|---|---|---|---|---|
| `NOT_FOUND` | 404 | Resource không tồn tại hoặc user không có quyền xem | No | Business |
| `CONFLICT` | 409 | Duplicate key hoặc business rule conflict | No | Business |
| `INVALID_STATE` | 422 | Business rule violation (invalid state transition) | No | Business |
| <!-- VD: `EMAIL_DUPLICATE` --> | 409 | <!-- Email đã được đăng ký --> | No | Business |
| <!-- VD: `ORDER_ALREADY_CANCELLED` --> | 422 | <!-- Không thể cancel order đã cancelled --> | No | Business |

### System

| Code | HTTP Status | Condition | Retryable | Category |
|---|---|---|---|---|
| `RATE_LIMIT_EXCEEDED` | 429 | Vượt rate limit — xem header `Retry-After` | Yes (sau `Retry-After`) | System |
| `SERVICE_UNAVAILABLE` | 503 | Downstream dependency tạm thời không available | Yes (backoff) | System |
| `INTERNAL_ERROR` | 500 | Lỗi hệ thống không xác định — không expose internal details | No | System |

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ARCH-1`
- [ ] Global Conventions nhất quán với `coding-standards-backend.md` (camelCase, ISO 8601, error envelope)
- [ ] Mọi externally visible endpoint đều được cover
- [ ] Auth và rate limits được spec
- [ ] Collection endpoints document filtering, sorting, field selection, pagination
- [ ] Mỗi Request Body có Field Schema table: type, required, validation, default, example — KHÔNG phải chỉ placeholder JSON
- [ ] Mỗi Response Body có Field Schema table với types rõ ràng
- [ ] Error section per endpoint liệt kê ít nhất 1 happy path + 2 error scenarios
- [ ] Error Code Catalog centralized và đủ để generate ErrorCode enum
- [ ] Assumption blocks đã được viết cho các quyết định API design quan trọng
