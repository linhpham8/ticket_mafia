# Coding Standards — Backend & API

> Tiêu chuẩn kỹ thuật cho backend development và API design.
> AI đọc file này khi: thiết kế API, thiết kế database, chọn backend framework, gen code backend.

---

## 1. General Principles

### 1.1 Foundational rules

- **Object-oriented and clean-architecture mindset** — separate domain, application, infrastructure, and delivery layers; dependencies point inward.
- **Clean Code** and **Secure Coding** — apply OWASP Top 10.
- **Minimum unit-test coverage** — declared in NFR (default: **line ≥ 90%** per `quality_profile.coverage_min_new_code` **AND branch ≥ 90%** per `coverage_branch_min_new_code`, region for Swift — see `unit-test-standards.md`).
- **Repo test delta quality** — generated unit / integration tests follow `unit-test-standards.md` (technique discipline, 90% branch coverage on new code, deterministic; mutation optional/suggested; `CODE-3a..3d`).
- Important business logic lives in the backend; the frontend never makes the final decision.

### 1.2 Software design principles (apply to every language)

These principles are non-negotiable. `validate implementation --mode quality` checks them via rule IDs `CODE-4..CODE-9` in `core/phase-quality-standards.md`.

- **SOLID**
  - **S — Single Responsibility**: every class / function / module has one reason to change. Mixing HTTP parsing, business rules, and persistence in the same class is a `CODE-4` fail signal.
  - **O — Open / Closed**: extend behavior via new types, interfaces, or strategy plug-ins; do not reopen a stable class to add a new branch.
  - **L — Liskov Substitution**: subtypes must respect the parent contract; no surprise exceptions, no narrower argument types.
  - **I — Interface Segregation**: prefer many small, role-specific interfaces over one fat interface.
  - **D — Dependency Inversion**: high-level modules depend on abstractions, not on concrete database / HTTP / SDK classes. Inject the abstraction; resolve the concrete implementation only at the composition root.
- **Loose coupling, high cohesion**: classes within a module collaborate tightly; cross-module collaboration goes through a small, named public surface declared in `/docs/architecture/project-reference.md`. Direct reach into another module's internals is a `CODE-5` fail.
- **DRY** (Don't Repeat Yourself): copy-pasted business logic across two or more places is a `CODE-9` fail. Extract a shared helper, policy, or domain service. Trivial duplication (e.g. test fixtures) is allowed.
- **KISS & YAGNI**: build for the requirement that exists, not the one you imagine. No speculative abstractions, no toggles for features nobody asked for.
- **Layered architecture (default backend shape)**:
  - `controller / handler` — HTTP / event boundary, request validation, error envelope. No business decisions.
  - `application service / use case` — orchestrates the flow, owns transactions.
  - `domain` — entities, value objects, domain services, invariants. Pure logic, no framework imports.
  - `infrastructure / repository / gateway` — persistence, external APIs, message brokers. Implements interfaces defined in the domain or application layer.
  - Dependency direction: `controller → application → domain ← infrastructure`. The domain never imports framework or infrastructure types.
- **Design pattern guidance** — apply the smallest pattern that fits, do not retrofit. Common useful patterns:
  - Repository / Gateway for persistence and outbound integration boundaries.
  - Strategy for swappable business rules (e.g. multiple pricing rules).
  - Factory / Builder when object construction is non-trivial.
  - Decorator / Middleware for cross-cutting concerns (logging, auth, retry).
  - Adapter when adapting an external SDK to the project's domain interface.
  - Observer / Domain Event for decoupled side-effects.
  - Saga / Process Manager for multi-step workflows with compensation.
  - Anti-patterns to avoid: God class, anemic domain mixed with transactional script that hides invariants, Singleton holding mutable state, Service Locator hiding dependencies.
- **Error handling**: throw / return typed domain errors at the domain layer; translate to the standardized error envelope (see §6) only at the controller boundary.
- **Immutability where practical**: prefer immutable value objects and pure functions for domain logic; reserve mutability for entities with intentional lifecycle state.

### 1.3 Testability rules

- Every public function in the application + domain layer must be reachable by a unit test without spinning up the framework. If a function cannot be unit-tested without a real DB / HTTP / clock, that is a `CODE-8` (test-seam) fail.
- Inject `Clock`, `IdGenerator`, `Random`, and other non-deterministic sources behind an interface so tests can stub them.
- No `static` business logic that hides state; static is only acceptable for pure utilities.

---

## 2. Language & Framework Standards

| Ngôn ngữ | Framework | Build | Unit Test | Ưu tiên & Điều kiện |
|----------|-----------|-------|-----------|---------------------|
| **Java** | Spring Boot | Maven | JUnit / Mockito | **Ưu tiên đầu tiên** — mọi backend mới |
| **Go** | Gin | (built-in) | (built-in) testing | Khi: kiến trúc cần polyglot, hoặc system/tool đơn giản không có định hướng mở rộng |
| **Python** | FastAPI / Flask | Poetry | Pytest | **Chỉ cho AI/ML services** — không dùng cho business logic thông thường. FastAPI ưu tiên cho inference/serving API (khớp §8 idioms + `coding-standards-ai.md`) |

> AI hỏi user để xác nhận ngôn ngữ nếu chưa được khai báo trong PRD hoặc prism-config.

---

## 3. API Design Standards

### 3.1 Giao thức & Format
- Giao thức: **RESTful**, format **JSON**, encoding **UTF-8**
- Documentation: **OpenAPI** (bắt buộc)
- Transport: **HTTPS** bắt buộc

### 3.2 Authentication
- Header: `Authorization: Bearer <token>`
- Backend-to-backend (M2M): theo chuẩn M2M của Central IAM — xem `security-standards.md`

### 3.3 URL Design

```
✅ /api/v1/products           — danh từ số nhiều, chữ thường, có version
✅ /api/v1/user-profiles      — kebab-case
✅ /api/v1/products/{id}/items — sub-resource

❌ /api/getProducts           — không dùng động từ trong URL
❌ /api/v1/ProductList        — không PascalCase
❌ /products                  — không có version
```

### 3.4 HTTP Methods
| Method | Dùng cho |
|--------|----------|
| GET | Đọc dữ liệu — idempotent |
| POST | Tạo mới resource |
| PUT | Thay thế toàn bộ resource |
| PATCH | Cập nhật một phần resource |
| DELETE | Xóa resource |

### 3.5 HTTP Status Codes Chuẩn
| Code | Khi nào |
|------|---------|
| 200 | Thành công (chung) |
| 201 | Tạo mới thành công |
| 204 | Thành công, không có body (DELETE) |
| 400 | Bad request — dữ liệu đầu vào sai |
| 401 | Chưa authenticated |
| 403 | Authenticated nhưng không có quyền |
| 404 | Resource không tìm thấy |
| 409 | Conflict — state hiện tại không cho phép action |
| 422 | Unprocessable entity — validation lỗi với detail |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

### 3.6 Response Format

**JSON body field naming:** `camelCase`

**Error response** — bắt buộc dùng standardized error envelope (định nghĩa canonical ở §6.3). Payload luôn nằm dưới `error`; `details` là **array** cho field-level validation errors, hoặc **object** code-specific cho các lỗi khác:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Mô tả lỗi cho developer",
    "request_id": "req-uuid",
    "trace_id": "abc123",
    "details": [
      { "field": "email", "message": "Không đúng định dạng email" }
    ]
  }
}
```

**Date/time:** ISO 8601 — `YYYY-MM-DDThh:mm:ssZ`, múi giờ **UTC**

### 3.7 Collection Querying & Pagination
- **Filtering**: collection endpoints phải document rõ filter nào được support và format query parameter tương ứng
- **Sorting**: phải document field allowlist và chiều sort, ví dụ `sort=-createdAt,name`
- **Field selection**: khi payload lớn hoặc client chỉ cần một phần dữ liệu, document sparse fieldsets, ví dụ `fields=id,name,status`
- **Pagination**: **bắt buộc** cho mọi endpoint trả về danh sách; mặc định ưu tiên cursor-based pagination cho large datasets
- Mọi query conventions trên phải được thể hiện rõ trong OpenAPI / API specs

---

## 4. Database Design Standards

### 4.1 Nguyên tắc thiết kế

- Tuân thủ **ACID** — đảm bảo tính toàn vẹn và nhất quán dữ liệu
- Thiết kế bảng đạt **3NF** — trừ khi có lý do rõ ràng và có ADR
- Mỗi bảng **bắt buộc có Primary Key**
- Quan hệ giữa bảng **bắt buộc có Foreign Key Constraint** — ngoại lệ phải có ADR được SA phê duyệt
- **Transaction scope** phải ngắn gọn — không gọi external service bên trong transaction
- **Index** phải được đánh giá kỹ trước khi deploy — dùng `EXPLAIN` để kiểm tra
- **Column data type** phải phù hợp với nhu cầu và tối ưu dung lượng

### 4.2 Database & Cache Technology Standards

| Loại | Giải pháp | Khi nào dùng |
|------|-----------|-------------|
| **Cache** | Redis | Mặc định cho mọi caching |
| **RDBMS (ưu tiên)** | MySQL / InnoDB | Mặc định cho transactional data |
| **RDBMS (nâng cao)** | PostgreSQL | ACID nghiêm ngặt; dữ liệu hỗn hợp (structured + semi-structured); JOIN phức tạp, Window Functions, Recursive Queries; GIS |
| **RDBMS đặc thù** | Oracle | Chỉ khi có yêu cầu đặc thù (legacy, enterprise contract) |
| **NoSQL** | MongoDB | Dữ liệu document-based: hợp đồng, văn bản phi cấu trúc |
| **NewSQL** | TiDB | Cần ACID + horizontal scaling + HA; kết hợp OLTP và OLAP |

> Công nghệ ngoài danh sách trên cần được phê duyệt kiến trúc (ADR + DAB approval).

### 4.3 Data Governance Requirements

- **Data Owner / Steward** phải được xác định rõ cho mỗi domain
- **Single Source of Truth** — mỗi entity được master bởi đúng một context
- **PII và dữ liệu nhạy cảm** phải được identify và có encryption/masking plan — xem `security-standards.md`
- **Master Data Management** để loại bỏ data silos và duplicate

### 4.4 Database Modeling Patterns

- **RDBMS default 3NF**; denormalize chỉ khi đo được performance need.
- **Sharding** khi single shard > 100M rows hoặc > 1TB; chọn shard key tránh hot-spot.
- **Indexing:** composite index theo query pattern thật; tránh over-index (write penalty); review qua `EXPLAIN`.
- **Time-series** → TimescaleDB / InfluxDB / ClickHouse — không stuff vào RDBMS thường.
- **NoSQL document (MongoDB):** model theo access pattern, không theo entity. Embed cho 1-N nhỏ; reference cho 1-N lớn / N-N.
- **Consistency:** strong (RDBMS default) vs eventual (multi-region / NoSQL) — document trade-off trong ADR.
- **Soft delete vs hard delete:** policy rõ; soft delete có expiry job xóa vĩnh viễn theo data retention.

### 4.5 Database Migration Standard

Tooling theo language:
- Java/Kotlin → Flyway hoặc Liquibase
- Node.js → Prisma migrate / Knex / TypeORM migrations
- Python → Alembic
- Go → golang-migrate
- Ruby → ActiveRecord migrations

Bắt buộc:
- **Versioned migrations** trong repo, applied via CI/CD (không apply tay).
- **Rollback (down) script** cho mỗi migration; zero-downtime pattern: expand → migrate-data → contract.
- **Backward-compatible** trong cùng release (deploy code mới vẫn chạy với schema cũ trong window migrate).
- **Dry-run** trên staging với prod-like data trước khi apply prod.
- **Audit log:** ghi who/when applied; lock table chống concurrent run.
- **Data migration > 10M rows:** batch + checkpoint + resume; avoid table lock dài.

---

## 5. API Versioning & Deprecation

- **URL versioning** mặc định: `/api/v1/`, `/api/v2/`. Header versioning chỉ dùng khi rõ benefit.
- **Lifecycle:** stable → deprecated (notify 6 tháng) → sunset → retired.
- **Sunset header** ([RFC 8594](https://datatracker.ietf.org/doc/html/rfc8594)) trên endpoint deprecated.
- **Breaking change policy:** bắt buộc bump major version; thông báo qua release notes + email partner.
- **Backward compatibility:** thêm field optional ≠ breaking; remove / rename field = breaking.
- **Changelog:** `CHANGELOG.md` per service liệt kê thay đổi mỗi version.

---

## 6. Error Code Catalog (bắt buộc)

Mỗi backend service phải có catalog error codes tập trung. Frontend / partner integrate dựa trên catalog này.

### 6.1 File catalog — `errors.yml` ở root mỗi service

```yaml
version: 1
service: payment-service
codes:
  - code: PAYMENT_DECLINED
    http_status: 402
    message_key: errors.payment.declined          # i18n key
    description: "Payment processor rejected the transaction"
    retryable: false
    category: payment

  - code: PAYMENT_GATEWAY_TIMEOUT
    http_status: 504
    message_key: errors.payment.gateway_timeout
    description: "Upstream payment gateway timed out"
    retryable: true
    retry_after_seconds: 5
    category: payment

  - code: RATE_LIMIT_EXCEEDED
    http_status: 429
    message_key: errors.rate_limit
    description: "Too many requests"
    retryable: true
    retry_after_header: true
    category: throttling
```

### 6.2 Naming convention

- `<DOMAIN>_<REASON>`, UPPER_SNAKE_CASE.
- Domain = subdomain trong service (`PAYMENT`, `INVENTORY`, `AUTH`, `ORDER`).
- Cấm generic số (`ERROR_001`, `E1234`) — khó nhớ, mất context.

### 6.3 Standardized error envelope

```json
{
  "error": {
    "code": "PAYMENT_DECLINED",
    "message": "Thanh toán bị từ chối",
    "request_id": "req-uuid",
    "trace_id": "abc123",
    "details": { "decline_reason": "insufficient_funds" }
  }
}
```

- `code` = exact match trong `errors.yml`.
- `message` = resolve theo locale từ `message_key`.
- `request_id` / `trace_id` = phục vụ tra log.
- `details` = optional. **array** cho field-level validation errors (`[{ "field", "message" }]`, xem §3.6), hoặc **object** code-specific payload cho các lỗi khác. §3.6 và §6.3 dùng chung envelope này.

### 6.4 Code generation từ catalog (gen-time)

- Build script gen typed enum / const từ `errors.yml`:
  - Java/Kotlin → `enum class ErrorCode`
  - TS → `export const ErrorCode = { PAYMENT_DECLINED: 'PAYMENT_DECLINED', ... } as const;`
  - Python → `class ErrorCode(str, Enum)`
- Source code KHÔNG hardcode string — chỉ dùng `ErrorCode.PAYMENT_DECLINED`.

### 6.5 OpenAPI sync (gen-time)

Build script đọc `errors.yml` → emit vào OpenAPI:
- `components/schemas/ErrorEnvelope` — shape chung.
- `components/responses/<Code>` — 1 response object per code.
- Mỗi endpoint khai `responses` reference các code có thể trả ra.

OpenAPI là source of truth cho client SDK gen → frontend / partner tự động có code list.

### 6.6 Versioning rule

- **Add code mới:** không breaking, OK trong cùng major version.
- **Remove / rename code:** breaking → bump major API version.
- **Đổi semantic code (cùng tên nhưng nghĩa khác):** TUYỆT ĐỐI cấm. Phải code mới + deprecate code cũ.
- **Đổi `http_status`:** breaking nếu client phụ thuộc status. Đối xử như rename.

---

## 7. Code Quality Thresholds & Traceability

These thresholds are enforced by `validate implementation --mode quality` against rules `CODE-4..CODE-9`. They apply to every backend language (Java, Kotlin, Go, Python, Node.js, etc.). Project-specific overrides go in `prism-config.md` under `quality_profile.code_thresholds`.

### 7.1 Size and complexity thresholds

| Metric | Threshold (default) | Rule | Severity | Exception |
|--------|--------------------|----- |----------|-----------|
| Function / method length | ≤ 80 effective lines (excluding blank + comment + annotation) | `CODE-6` | warn at 80, blocker at 120 | Generated code, switch dispatch on a sealed enum |
| File length | ≤ 500 lines | `CODE-6` | warn at 500, blocker at 800 | Generated code, large config maps |
| Class length | ≤ 300 lines | `CODE-6` | warn | Generated code |
| Cyclomatic complexity per function | ≤ 10 | `CODE-7` | warn at 10, blocker at 15 | Parser / state-machine with explicit rationale in a comment |
| Parameter count per function | ≤ 5 | `CODE-6` | warn at 5, blocker at 7 | DTO-style constructor in a value object |
| Nesting depth | ≤ 3 | `CODE-6` | warn | — |
| Public API surface per module | Minimal — only what `/docs/architecture/project-reference.md` lists as `public_entrypoints` | `CODE-5` | blocker | — |

Functions that breach `blocker`-level numbers must be refactored before `approve implement` unless an ADR explicitly accepts the deviation.

### 7.2 Code traceability comment (CODE-1 marker)

Every new or materially changed API handler, service, job, migration, or non-trivial business function MUST carry a concise traceability comment that lets a reviewer trace the code back to the approved scope without leaving the file.

```java
// Sprint: v2 | Feature: FR-018 | US: US-042 | Task Group: 2.1 Retry failed payment
// Contract: /docs/architecture/api-specs.md §API-018 POST /payments/authorize | Project: /docs/architecture/project-reference.md §PR-005
// Pack: v2.3.8-fix-payment | Ticket: PAY-114
public PaymentAuthorizationResult authorize(...) { ... }
```

Rules:
- Omit `Pack:` when the scope is not from a change pack.
- Omit `Ticket:` when no approved ticket / task ID exists. Never invent one.
- Do not spray boilerplate markers across trivial helpers — `CODE-2` flags noise.
- When `feedback:` revises the scope, update the marker so it still describes the delivered slice.
- Inline comments inside the function body should explain *why* (non-obvious constraints, invariants, performance / security trade-offs), not *what* (the code already says what).

### 7.3 Dependency direction and module boundaries

- The dependency graph between layers (`controller → application → domain ← infrastructure`) MUST be acyclic and one-directional. Cyclic dependencies between modules are a `CODE-5` blocker.
- A task group's allowed code zone is declared by Plan as `code_ownership_zones`. Code that strays outside the declared zone without an approved plan change is a `CODE-5` blocker (see `phase-plan.md` and the plan template).
- Cross-module imports go through the module's public entrypoint declared in `/docs/architecture/project-reference.md`. Reaching into another module's internal package is a blocker.

### 7.4 Test seams

- Domain and application services accept their dependencies via constructor (or framework DI). No `new SomeClient()` inside business logic.
- Time, randomness, and external IDs come from injected interfaces (`Clock`, `IdGenerator`, `Random`) so tests can stub them. Hardcoded `LocalDateTime.now()` / `UUID.randomUUID()` inside business code is a `CODE-8` warn.
- Side effects (DB, HTTP, message bus) are isolated behind repository / gateway interfaces so the unit test of the business rule does not touch I/O.

### 7.5 Self-check before claiming implementation done

Before declaring a task group done, the developer / AI MUST mentally walk these questions:

1. Does every new public function have a single, named responsibility? (`CODE-4`)
2. Are dependencies pointing in the declared direction with zero cycles? (`CODE-5`)
3. Is every function ≤ 80 lines, cyclomatic ≤ 10? Run the configured linter if available. (`CODE-6`, `CODE-7`)
4. Are time / randomness / IDs / external I/O injected, not hardcoded? (`CODE-8`)
5. Is there any duplicated business logic across files that should become a shared helper? (`CODE-9`)
6. Does every business-facing function carry the `CODE-1` traceability comment?
7. Does the change stay within `code_ownership_zones` declared by the plan?

A "no" on any of the above is a blocker for `approve implement` until resolved.

---

## 8. Framework Idioms — Note

Generated backend code MUST follow the idiomatic patterns of the chosen language and framework (Spring Boot, Go + Gin, Python / FastAPI / Flask, Node.js, etc.). PRISM intentionally does NOT enumerate every framework idiom in this file — the list would bloat fast and drift with ecosystem updates.

How the AI applies this:

- At code-gen time, draw from model training knowledge of the chosen stack's well-known conventions (dependency injection style, error handling, transaction placement, logging, async patterns, test layering, etc.).
- When training knowledge is uncertain or the framework has shipped a relevant change since cutoff, consult the official framework documentation. This is a **narrow exception** to `INDEX.md` rule "never load standards from web / training data" — that rule applies to **PROJECT standards** (security, compliance, architecture, naming, etc.). General **framework idioms** are public ecosystem knowledge, not project standards.
- Do not paste idioms from one ecosystem into another (no Java patterns inside Go code, no Spring annotations inside Node.js, etc.).
- When in genuine doubt, ask the user via `feedback:` rather than guess.

`validate implementation --mode quality` checks idiom adherence against the chosen stack's conventions. Drift surfaces as `warn`; defects from drift (measurable perf hit, memory leak, security gap, contract mismatch) escalate to `blocker`.
