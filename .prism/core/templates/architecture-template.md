---
status: DRAFT
version: v1
sprint: 1
phase: architecture
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# System Architecture Overview — {{PROJECT_NAME}}

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Per-item architecture sections carry stable IDs (ARCH-COMP-NNN for §6 Component Boundaries,
     ARCH-NNN for §7 Architecture Decisions). Each is preceded by an HTML-comment anchor on its own line:
         <!-- ID: ARCH-COMP-NNN -->
         ### Component: PaymentService
         ...
     Tables (§2 Package Index, §5 Tech Stack) remain non-anchored narrative.
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type {ARCH-COMP|ARCH}`.
     NB: `ARCH-COMP` is split from the former `COMP` prefix to disambiguate from `DS-COMP` (design system UI components).
     (Guided seal only) The anchors make §6 / §7 blocks mergeable by `apply_proposal.py` at sprint seal, and the
     §1 narrative is the singleton `ARCH-OVERVIEW-001` block (`## New` sprint 1, `## Updated` later) — Freedom has
     no seal / no overview singleton; it still issues the IDs above and keeps the anchors. -->

File này là **entrypoint tổng quan** của architecture package. Nó tóm tắt hình dạng hệ thống và links đến các companion files chuyên biệt.

`project-reference.md` là companion file ghi rõ code-facing structure, module / package organization, public entrypoints, dependency boundaries, và naming conventions downstream phases phải cùng follow.

**Không** gộp toàn bộ vào file này. Sequence flows chi tiết, ERD, ADRs, data-flow, API contracts, event contracts, và NFR tables thuộc về các companion files riêng.

<!-- PRISM:LT-SKELETON-END -->

<!-- AUTHORING NOTE (everything below this line is reference only — stripped from the Living
     Truth skeleton at bootstrap). Emit the narrative below (§1 Executive Summary: style,
     runtime, key trade-offs, system-wide shape) as ONE anchored block
     `<!-- ID: ARCH-OVERVIEW-001 -->` + `### Architecture Overview` in
     `architecture/proposals/architecture-v{X}.md` — `## New` in sprint 1, `## Updated`
     (replace in place, ID fixed) later. `ARCH` / `ARCH-COMP` remain separate anchored items. -->

## 1. Executive Summary

- **Architecture style**: <!-- VD: Modular Monolith, Service-based, Microservices -->
- **Primary runtime**: <!-- VD: NextJS + Java Spring Boot + PostgreSQL -->
- **Primary deployment shape**: <!-- VD: Web + API server + background workers trên Kubernetes -->
- **Key trade-off**: <!-- Tối ưu cho điều gì, đánh đổi điều gì -->
- **Primary risks**: <!-- Top 2–3 rủi ro mà downstream teams phải biết -->

## 2. Architecture Package Index

| File | Purpose | Status / Notes |
|---|---|---|
| `sequence.md` | Core runtime flows and error paths (SEQ-NNN anchored) | |
| `erd.md` | Data model, schema notes, indexes, migrations (ENT-NNN anchored) | |
| `adr.md` | Decision rationale and trade-offs (ADR-NNN anchored) | |
| `data-flow.md` | Data movement, ownership, consistency, retention (FLOW-NNN anchored) | |
| `api-specs.md` | HTTP / RPC contract surface (API-NNN anchored) | |
| `events.md` | Event-driven contracts and delivery semantics (EVT-NNN anchored) | |
| `nfr.md` | Measurable non-functional targets and budgets (NFR-NNN anchored) | |
| `project-reference.md` | Project engineering contract: module map, source tree, boundaries, naming, stable code surfaces (PR-NNN anchored) | |
| `assets/` | Draw.io / XML C4 + DFD sources and supporting diagrams; authored in the sprint and copied into Living Truth `architecture/assets/` at seal so the `assets/...` references here resolve | |

## 3. C4 Model

Dùng text mà reviewer có thể đọc trực tiếp, đi kèm Draw.io/XML source lưu tại `assets/` để chỉnh sửa. Mermaid không bắt buộc cho C4; trọng tâm là model source chỉnh sửa được và khớp với phần text-readable.

### 3.1 System Context

| Actor / External System | Quan hệ với {{PROJECT_NAME}} | Ghi chú |
|---|---|---|
| End user | Sử dụng UI / API chính | |
| Admin / Operator | Thực hiện các workflow vận hành / admin | |
| External service | Cung cấp hoặc tiêu thụ business capability | |

### 3.2 Container View

| Container | Trách nhiệm | Công nghệ | Sở hữu Data? | Interfaces chính |
|---|---|---|---|---|
| Web / App UI | | | Không | |
| API / Backend | | | Một phần | |
| Worker / Async processor | | | Một phần | |
| Database | | | Có | |
| Cache / Queue / Search | | | Không | |

### 3.3 Component View

<!-- Required. C4 output must cover at least 3 levels: System Context, Container View, and Component View. -->

| Component / Module | Trách nhiệm | Input | Output | Upstream / Downstream |
|---|---|---|---|---|
| | | | | |

### 3.4 C4 Source Asset

- **Draw.io/XML asset path**: `assets/c4-model.drawio` hoặc `assets/c4-model.drawio.xml`
- **Status**: <!-- present / generated / blocker: missing source asset -->
- **Required views in source**: System Context + Container View + Component View
- **Connector routing**: connectors must not cut across or run through containers / boundaries; avoid crossings where possible; if a crossing is unavoidable, use arc line jumps (`jumpStyle=arc`) and keep labels readable.
- **Ghi chú**: <!-- cách source asset liên kết với text-readable summary; actors / containers / components phải khớp nhau -->

## 3b. Architecture Traceability Map

<!-- Đây là map ở phía Architecture để nối Product xuống companion files và downstream phases. -->
<!-- Mỗi Must Have FR nên xuất hiện ở đây. Nếu một FR không cần thay đổi kiến trúc, phải ghi rõ vì sao. -->

| FR / US | Primary Components / Contexts | APIs / Events | Sequence / Data Ownership Refs | Special Obligations / Notes |
|---|---|---|---|---|
| FR-NNN / US-NNN | <!-- VD: Orders Context, PaymentService --> | <!-- VD: POST /orders, order.created --> | <!-- VD: sequence.md §SEQ-001, Orders owns Order aggregate --> | <!-- VD: audit log, idempotency, PII masking --> |
| | | | | |

## 4. Bounded Contexts And Context Map

<!-- Bắt buộc khi architecture style là Modular Monolith, Service-based hoặc Microservices.
     Bỏ qua section này (ghi "N/A — [lý do]") chỉ khi là monolith đơn giản không có domain phân chia.
     Xem thêm: prism/core/standards/architecture-solution-standards.md — mục 2.2 -->

### 4.1 Business Subdomains

| Subdomain | Loại (Core / Supporting / Generic) | Mô tả |
|-----------|-----------------------------------|----|
| | Core | <!-- Core domain = lợi thế cạnh tranh cốt lõi --> |
| | Supporting | <!-- Hỗ trợ core, nhưng không phải differentiator --> |
| | Generic | <!-- Commodity, có thể mua/dùng off-the-shelf --> |

### 4.2 Bounded Contexts

| Context | Subdomain | Trách nhiệm | Upstream (nhận từ) | Downstream (cung cấp cho) |
|---------|-----------|-------------|-------------------|--------------------------|
| | | | | |

### 4.3 Context Map

<!-- Mermaid diagram hoặc link tới file diagram thể hiện relationships giữa các contexts.
     VD: Customer Context ——[Conformist]——> Order Context ——[ACL]——> Payment Context -->

```
[Điền Context Map tại đây — Mermaid hoặc mô tả dạng text]
```

## 5. Technology Stack

<!-- Cột "On Approved List?" — check xem tech có trong `coding-standards-backend.md` / `coding-standards-frontend.md` không. -->
<!-- Nếu không có trong approved list → BẮT BUỘC có ADR Reference giải thích lý do chọn. -->
<!-- Nếu không có ADR mà tech cũng không trong approved list → đây là architecture risk cần xử lý. -->

| Layer | Công nghệ | Version | Lý do lựa chọn | ADR Reference | On Approved List? |
|-------|-----------|---------|----------------|---------------|-------------------|
| Frontend | {{FRONTEND_TECH}} | | | ADR-xxx / N/A | Yes / No |
| Backend | {{BACKEND_TECH}} | | | ADR-xxx / N/A | Yes / No |
| Database | {{DATABASE_TECH}} | | | ADR-xxx / N/A | Yes / No |
| Messaging | {{QUEUE_TECH}} | | | ADR-xxx / N/A | Yes / No |
| Cache | {{CACHE_TECH}} | | | ADR-xxx / N/A | Yes / No |
| Search | {{SEARCH_TECH}} | | | ADR-xxx / N/A | Yes / No |
| Infrastructure | {{INFRA_TECH}} | | | ADR-xxx / N/A | Yes / No |
| Security | {{SECURITY_TOOLS}} | | | ADR-xxx / N/A | Yes / No |
| CI/CD | {{CICD_TECH}} | | | ADR-xxx / N/A | Yes / No |
| Monitoring | {{MONITORING_TECH}} | | | ADR-xxx / N/A | Yes / No |
| Test (Unit) | {{UNIT_TEST_FRAMEWORK}} | | | ADR-xxx / N/A | Yes / No |
| Test (Integration) | {{INTEGRATION_TEST_FRAMEWORK}} | | | ADR-xxx / N/A | Yes / No |
| Test (E2E) | {{E2E_TEST_FRAMEWORK}} | | | ADR-xxx / N/A | Yes / No |
| Test (Contract) | {{CONTRACT_TEST_TOOL}} | | | ADR-xxx / N/A | Yes / No |
| Mocking | {{MOCKING_TOOL}} | | | ADR-xxx / N/A | Yes / No |
| Frontend error tracking | {{FRONTEND_ERROR_TRACKING}} | | | ADR-xxx / N/A | Yes / No |

## 6. Component Boundaries

<!-- ID: ARCH-COMP-NNN -->
### Component: {{COMPONENT_NAME}}

- **Trách nhiệm**: <!-- một trách nhiệm rõ ràng duy nhất -->
- **Sở hữu**: <!-- data / process / domain area -->
- **Phơi ra**: <!-- API, event, internal interface -->
- **Tiêu thụ từ**: <!-- upstream API, event, DB, queue -->
- **Scaling strategy**: <!-- horizontal / vertical / async / batch -->
- **Failure mode**: <!-- điều gì xảy ra khi component này bị degraded -->

## 6b. Component Interaction Overview

<!-- Mô tả tổng quan (dạng narrative) về cách các cấu phần tương tác với nhau.
     Đây KHÔNG phải sequence diagram — đây là mô tả cấp cao về luồng tổng thể và cơ chế giao tiếp.
     Trả lời: cấu phần nào là "điều phối viên" trung tâm? Synchronous hay async chủ yếu?
     Có pattern đặc biệt không (facade, event backbone, async polling)? -->

<!-- VD: "Tất cả tương tác từ frontend đi qua UI Service — service này đóng vai trò facade cho toàn bộ domain services.
         Các domain services giao tiếp với nhau qua REST (synchronous) cho các tác vụ cần kết quả ngay.
         Tác vụ xử lý lâu (VD: import tài liệu, OCR) dùng cơ chế async: caller nhận ID ngay, poll trạng thái sau.
         Không có service nào gọi trực tiếp database của service khác." -->

## 7. Significant Architecture Decisions

<!-- Tập hợp các quyết định then chốt theo tiêu chí "significant decision".
     Tiêu chí đầy đủ tại: prism/core/standards/architecture-solution-standards.md — mục 1b.
     Tóm tắt: quyết định khó đảo ngược, liên quan đến quality attributes, khác chuẩn, hoặc chi phí cao.
     Chi tiết trade-off, pros/cons và consequences tại adr.md. -->

| ADR | Quyết định | Các lựa chọn đã đánh giá | Lựa chọn | Lý do cốt lõi |
|-----|-----------|--------------------------|----------|---------------|
| ADR-001 | | | | |

## 8. Deployment And Runtime Topology

<!-- Mô tả deployment ở mức ảnh hưởng đến quyết định code và security.
     AI hỏi user để xác nhận các điểm trong bảng dưới — chúng ảnh hưởng trực tiếp đến design.
     Xem thêm: prism/core/standards/architecture-solution-standards.md — mục 4.2 -->

### 8.1 Deployment Context (ảnh hưởng đến code design)

| Câu hỏi | Trả lời | Ảnh hưởng đến code |
|---------|---------|-------------------|
| Service này `internal-only` hay `public-facing`? | <!-- Internal / Public / Mixed --> | <!-- VD: `internal-only` → có thể dùng mTLS / basic auth; `public-facing` → OAuth 2.0, rate limiting --> |
| Single instance hay multi-instance? | <!-- Single / Multi --> | <!-- VD: Multi → code phải stateless, shared cache, distributed locks --> |
| Container / Serverless / VM? | <!-- Kubernetes / Lambda / v.v. --> | <!-- VD: Serverless → cold start awareness, connection pooling --> |
| Có API Gateway / Reverse proxy phía trước? | <!-- Có / Không --> | <!-- VD: Có → không cần TLS termination ở app level --> |
| Database shared hay dedicated per service? | <!-- Shared / Dedicated --> | <!-- VD: Shared → phải có ADR; Dedicated → bounded context rõ ràng --> |

### 8.2 Environment Overview

| Môi trường | Topology | Services quan trọng | Ghi chú scaling |
|------------|---------|---------------------|-----------------|
| Development | | | |
| Staging | | | |
| Production | | | |

### 8.3 Component Deployment Matrix

<!-- Mỗi component/service: nơi deploy, cơ chế scale/HA, volume/traffic, và cơ chế security.
     Cột Security giúp AI biết auth model cần code cho từng component.
     VD: `internal-only` → mTLS / service mesh; `public-facing` → OAuth 2.0 + rate limiting -->

| # | Component | Deployment | Scalability / Availability | Volume / Traffic | Security |
|---|-----------|-----------|---------------------------|-----------------|----------|
| 1 | | <!-- VD: Kubernetes cluster A --> | <!-- VD: Auto-scale / HA (2+ replicas) --> | | <!-- VD: mTLS internal, OAuth 2.0 external --> |

### 8.4 Integration Deployment Matrix

<!-- Mỗi kết nối giữa 2 hệ thống/service: giao thức, cơ chế scale/HA, volume/traffic, và security.
     Phân loại vai trò integration: `provider` / `listener` / `bi-directional`.
     Nếu dùng webhook / callback, ghi rõ auth/signature, retry, replay protection, và idempotency.
     Cột Security giúp AI biết auth/encryption cần implement cho integration đó.
     VD: "internal service-to-service" → basic auth hoặc mTLS; "3rd party" → API key + TLS -->

<!-- Cột "SLA Partner" — availability đảm bảo bao nhiêu % từ phía đối tác/service ngoài. -->
<!-- Cột "Fallback Behavior" — khi integration này down, hệ thống xử lý thế nào? Ảnh hưởng đến circuit breaker config và fallback code. -->

| # | Tích hợp (A → B) | Vai trò | Giao thức | Scalability / Availability | Volume / Traffic | Security | SLA Partner | Fallback Behavior |
|---|-----------------|--------|----------|---------------------------|-----------------|----------|-------------|-------------------|
| 1 | | <!-- provider / listener / bi-directional --> | <!-- REST / gRPC / Kafka / SFTP / HTTPS webhook --> | | <!-- VD: 10.000 req/ngày --> | <!-- VD: API key + TLS 1.3 --> | <!-- VD: 99.5% uptime SLA / không có SLA / TBD --> | <!-- VD: Circuit breaker → return cached data / return error 503 / queue for retry --> |

### 8.5 Runtime Notes

- **Request path**: <!-- từ ingress đến business handler chính -->
- **Async path**: <!-- queues, workers, retry logic -->
- **Stateful components**: <!-- DB, cache, search, object store -->
- **HA / DR**: <!-- RTO/RPO targets, cơ chế failover -->

## 9. Security And Trust Boundaries

<!-- Xem chi tiết security standards tại: prism/core/standards/security-standards.md -->

| Boundary | Control | Ghi chú |
|----------|---------|---------|
| User → frontend | | |
| Frontend → backend | | |
| Backend → data stores | | |
| Internal async processing | | |
| External integrations | | |

## 10. Security Threat Model (STRIDE)

<!-- Bắt buộc — dùng STRIDE để đánh giá threats cho các cấu phần chính.
     Ít nhất phải cover Payment, Auth, và các service xử lý dữ liệu nhạy cảm.
     Chi tiết remediation ghi trong ADR hoặc ticket riêng. -->

| Loại Threat | Cấu phần | Mô tả threat | Phương án xử lý | ADR / Ticket |
|-------------|----------|-------------|-----------------|-------------|
| **Spoofing** | | <!-- Ai đó giả mạo identity để gửi request không hợp lệ --> | | |
| **Tampering** | | <!-- Ai đó sửa đổi data trong transit hoặc at rest --> | | |
| **Repudiation** | | <!-- Người dùng từ chối hành động đã thực hiện --> | | |
| **Information Disclosure** | | <!-- Dữ liệu nhạy cảm bị lộ --> | | |
| **Denial of Service** | | <!-- Làm hệ thống không phục vụ được --> | | |
| **Elevation of Privilege** | | <!-- Escalate quyền trái phép --> | | |

## 11. Assumptions

<!-- Những điều giả định là đúng nhưng chưa được xác nhận chắc chắn.
     Assumption có độ chắc chắn thấp → nguy cơ trở thành rủi ro nếu không được xác minh. -->

| # | Giả định | Hệ thống / Đội liên quan | Mức chắc chắn (High/Medium/Low) | Rủi ro nếu sai | Hành động cần thiết |
|---|---------|--------------------------|--------------------------------|----------------|---------------------|
| 1 | | | | | |

## 12. Risks And Open Questions

| # | Loại | Mô tả | Hệ thống | Khả năng xảy ra | Ảnh hưởng | Kế hoạch giảm thiểu |
|---|------|-------|----------|----------------|-----------|---------------------|
| 1 | Rủi ro | | | Cao/Trung bình/Thấp | | |
| 2 | Câu hỏi mở | | | | | |

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ARCH-1`, `ARCH-2`
- [ ] `architecture.md` là entrypoint tổng quan — không thế chỗ các companion files
- [ ] Architecture Package Index đã được điền, các companion files được tham chiếu rõ ràng
- [ ] `project-reference.md` đã được điền và link từ package index
- [ ] C4 text-readable summary tồn tại đủ ít nhất 3 tầng (System Context + Container View + Component View)
- [ ] C4 Draw.io/XML source asset path được ghi nhận cho required C4 views; nếu thiếu, ghi blocker/open issue trước approval
- [ ] C4 Draw.io/XML source khớp với text-readable summary về actors, containers, components, và relationships
- [ ] C4 Draw.io connector routing rõ ràng: không đi xuyên container / boundary; crossing bắt buộc dùng arc line jump (`jumpStyle=arc`)
- [ ] Architecture Traceability Map cover tất cả Must Have FR và key US, nối được tới component / API / sequence / data ownership
- [ ] Bounded Contexts section được điền (hoặc ghi N/A với lý do) cho Modular Monolith / Service-based / Microservices
- [ ] Component Boundaries rõ ràng, không chồng chéo
- [ ] Component Interaction Overview mô tả rõ cơ chế tổng thể (ai điều phối, sync/async, pattern đặc biệt)
- [ ] Significant Decisions tóm tắt các ADR theo đúng tiêu chí "significant" (khó đảo ngược, quality attributes, khác chuẩn, chi phí cao)
- [ ] Caching / Background Jobs / Resilience mechanics per `architecture-solution-standards.md §5–§7` (CDN, DLQ thresholds, circuit-breaker, timeout / retry defaults) đã được nêu hoặc ghi N/A với lý do
- [ ] Deployment Context đã trả lời 5 câu hỏi ảnh hưởng code design
- [ ] Component Deployment Matrix đã liệt kê security per component
- [ ] Technology Stack: mọi tech "Not on Approved List" đều có ADR Reference — không có tech không có ADR và không trong approved list
- [ ] Integration Deployment Matrix đã liệt kê security per integration
- [ ] Integration Deployment Matrix đã có SLA Partner và Fallback Behavior cho mọi external integration
- [ ] Security Trust Boundaries được document
- [ ] STRIDE Threat Model đã cover các component xử lý dữ liệu nhạy cảm
- [ ] Assumptions có mức độ chắc chắn và hành động xác nhận
- [ ] Risks có đủ: loại, mức độ, kế hoạch giảm thiểu
- [ ] Không có assumption ngầm về security, deployment hoặc compliance
- [ ] Planning-Ready Architecture Rule: mỗi Must Have FR trace tới component / API / sequence / data ownership; integrations có classification + contract reference; NFR §8 Config Mapping đã điền cho mỗi NFR ưu tiên; bounded contexts + data ownership matrix tồn tại khi style yêu cầu; companion artifacts cross-link với nhau và với entrypoint
- [ ] Đã chạy `validate architecture` và clear toàn bộ blocker ở cả 3 layers (`internal consistency`, `product fit`, `standards compliance`) trước khi đề xuất `approve arch`
- [ ] Each `### Component:` block in §6 starts with its `<!-- ID: ARCH-COMP-NNN -->` anchor line directly above the heading; each significant ADR in §7 uses anchored `<!-- ID: ARCH-NNN -->` + `### ARCH-NNN: Title` form so future sprints can merge updates via `apply_proposal.py`
