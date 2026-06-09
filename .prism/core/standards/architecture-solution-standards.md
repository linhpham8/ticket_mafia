# Architecture Solution Standards

> Tiêu chuẩn bắt buộc khi thiết kế kiến trúc giải pháp.
> AI đọc file này khi: thiết kế hệ thống mới, chọn architecture style, định nghĩa integration, viết NFR scenarios.

---

## 1. Quality Requirements Standard (NFR)

Mỗi thuộc tính chất lượng ưu tiên **BẮT BUỘC** có ít nhất một Architecturally Significant Scenario với `format`:

| Trường | Ý nghĩa | Ví dụ |
|--------|---------|-------|
| **Context** | Tình huống thực tế, có số liệu cụ thể | "Dựa trên lịch sử, khối lượng giao dịch tăng 10% mỗi quý" |
| **System Response** | Hệ thống phải phản ứng như thế nào | "Hệ thống duy trì response time và availability không đổi" |
| **Metrics** | Chỉ số cụ thể, đo được để xác nhận | "Chi phí cloud tăng không quá 10%; p95 latency không tăng quá 5%" |

**Quy tắc bổ sung:**
- Khi **Availability/Reliability** là ưu tiên → thêm scenario cho tải tới hạn (peak load), thể hiện yêu cầu Performance dưới tải cao
- Khi **Scalability** là ưu tiên → thêm scenario cho lộ trình scale (roadmap) hoặc sự kiện scale (event-based); thể hiện yêu cầu về chi phí, Availability, Performance

---

## 1b. Significant Architecture Decisions — Tiêu chí xác định

Một quyết định được coi là **Architecturally Significant** khi thỏa mãn ÍT NHẤT MỘT trong các điều kiện sau:

| Điều kiện | Ví dụ |
|-----------|-------|
| **Đảo ngược khó hoặc không thể** — chi phí thay đổi sau khi triển khai rất cao | Design approach (Domain-oriented vs Process-oriented); Architectural pattern (Monolith vs Microservices); Buy vs Build vs Buy-and-Build; Communication mechanism (RPC vs Message-based, Point-to-Point vs Topic-based); Database technology (NoSQL vs RDBMS, shared vs dedicated DB) |
| **Giải pháp cho quality attributes quan trọng** | Các lựa chọn cho Performance, Resilience, Scalability có ảnh hưởng lớn đến thiết kế |
| **Khác với nguyên tắc hoặc tiêu chuẩn đã đề ra** | Đặc biệt khi khác với chuẩn về Infrastructure hoặc Bảo mật |
| **Chi phí cao so với các lựa chọn khác** | Cần phân tích trade-off rõ ràng |
| **Kiến trúc sư hoặc Tech Lead nhận định cần đánh giá chi tiết** | |

Với mỗi significant decision, **bắt buộc phải có**:
- Phân tích pros/cons cho từng option
- Đánh giá trade-offs chi tiết
- Hướng xử lý cụ thể cho consequences của lựa chọn

> AI: khi phát hiện quyết định thỏa mãn bất kỳ điều kiện nào trên, phải viết ADR tương ứng vào sprint proposal `architecture/proposals/adr-v{X}.md` (route vào `/docs/architecture/adr.md` lúc seal) và cập nhật bảng Significant Decisions qua `architecture/proposals/architecture-v{X}.md`. KHÔNG sửa `/docs/architecture/*.md` trực tiếp — pre-commit chặn (xem `phase-architecture.md`).

---

## 2. Logical Architecture Standard

Thiết kế logic **BẮT BUỘC** dùng **C4 Model** (ít nhất C1 và C2), thể hiện các layers kiến trúc.

### 2.1 Standard Architecture Layers

| Layer | Vai trò |
|-------|---------|
| **Experience Layer** | Web, Mobile, Mini-app — giao diện với end user |
| **API / BFF Layer** | API Gateway, BFF (Backend for Frontend) — điều phối và tối ưu data cho từng loại client |
| **Domain / Application Layer** | Business logic lõi — tách biệt hoàn toàn với UI và Infrastructure |
| **Integration Layer** | Trung gian tích hợp giữa các hệ thống — middleware, ESB, Kafka |
| **Data Layer** | OLTP và OLAP — đảm bảo data reliability, consistency, sạch, đầy đủ |
| **AI / Automation Layer** | ML models, Agents, Rules engine — nằm trên Data Layer, tích hợp sâu với Application Layer |
| **Platform & Ops Layer** | CI/CD, Observability, Security controls — phủ ngang toàn bộ các layer khác |

### 2.2 Architecture Styles

#### Modular Monolith
**Khi nào dùng:**
- Quy mô hệ thống trung bình, chưa ở mức Netflix/Uber
- Đội ngũ và quy trình chưa đủ trưởng thành cho Microservices
- Chuẩn bị cho kiến trúc mục tiêu là Service-based hoặc Microservices

**Bắt buộc có:**
- Phân tích business subdomains, bounded contexts, context map
- Data ownership matrix (master/consume giữa các bounded context)

#### Service-based
**Khi nào dùng:**
- Modular Monolith không đáp ứng tốc độ scale
- Cần ACID per service nhưng chưa cần Saga/distributed transactions
- Đội ngũ 15–30 người, ổn định về năng lực và quy trình

**Bắt buộc có:**
- Phân tích business subdomains, bounded contexts, context map
- Data ownership matrix

#### Microservices
**Khi nào dùng:**
- Service-based không còn đáp ứng tốc độ tăng trưởng
- Cần scale độc lập từng service với quy mô cực lớn
- Cần polyglot technology
- Đội ngũ 50–100+ người, ổn định về năng lực và quy trình

**Bắt buộc có:**
- Phân tích business subdomains, bounded contexts, context map
- Data ownership matrix
- Cơ chế Eventual Consistency
- Distributed Tracing trưởng thành
- Idempotency cho mọi operation (nếu applicable)

#### Event-Driven Architecture (EDA)
**Khi nào dùng (hạn chế — chỉ khi thực sự cần):**
- Cần real-time response mà kiến trúc khác không đáp ứng được
- Cần scale/throughput cực cao mà các kiến trúc khác không đáp ứng

> EDA thường kết hợp với Microservices → tăng đáng kể độ phức tạp

**Bắt buộc có:**
- Phân tích business subdomains, bounded contexts, context map
- Data ownership matrix
- Cơ chế Eventual Consistency
- Distributed Tracing trưởng thành
- Idempotency bắt buộc cho mọi consumer

---

## 3. Integration Architecture Standard

Tất cả tích hợp **BẮT BUỘC** thuộc một trong ba nhóm dưới đây. Không tích hợp tùy tiện.

### 3.1 Nguyên tắc chung (áp dụng cho mọi loại tích hợp)

1. **Không gọi chéo DB** trực tiếp giữa các hệ thống
2. **`API-first` và `event-first`** — hạn chế tích hợp `point-to-point`
3. **Event là immutable** sau khi publish
4. **`Retry`, `circuit breaker`, và `idempotency`** là bắt buộc — dùng `Idempotency-Key` header để đảm bảo retry an toàn
5. **`Zero Trust`**: authentication/authorization rõ ràng, không có implicit trust
6. **`Observability`**: logging + metrics + end-to-end tracing cho mọi tích hợp
7. Mọi tích hợp bên ngoài phải được phân loại vai trò: `provider`, `listener`, hoặc `bi-directional`

### 3.1a External Integration Roles

- `provider`: hệ thống bên ngoài cung cấp khả năng nghiệp vụ hoặc dữ liệu cho hệ thống nội bộ. Nếu có nhiều provider cho cùng một khả năng nghiệp vụ, hoặc logic auth / mapping / retry khác nhau đáng kể, tách qua **`Partner Integration / Outbound Gateway`** để cô lập adapter, mapping, auth, rate limiting, retry, và failover policy.
- `listener`: hệ thống bên ngoài nhận state changes từ hệ thống nội bộ. Nếu dùng push qua HTTP, phải định nghĩa rõ **`webhook / callback contract`**: auth (API key, signature, hoặc mTLS), idempotency / dedup key, retry contract, timestamp tolerance / replay protection, và semantics 2xx / 4xx / 5xx.
- `bi-directional`: mô tả hai chiều như hai contract riêng, không gộp thành một integration entry mơ hồ.

### 3.2 Synchronous Integration
- Phù hợp cho: phản hồi tức thời, quan hệ nghiệp vụ rõ ràng
- Chuẩn: **REST API (HTTP/JSON)** — mặc định
- Chuẩn: **gRPC (HTTP/2, Protobuf)** — khi backend-to-backend, cần low latency, high throughput

### 3.3 Asynchronous Integration
- Phù hợp cho: decoupling, scale, data-centric & AI sẵn sàng
- **Đây là hình thức ưu tiên (event-first)** để giảm phụ thuộc
- Chuẩn streaming: **Kafka**
- Event schema: JSON Schema (đơn giản), Avro/Protobuf (khuyến nghị cho streaming)
- Với luồng publish / consume event, bắt buộc định nghĩa: retry / backoff, có cần replay hay không, replay trigger, replay window / TTL, max delivery / replay attempts, và đội chịu trách nhiệm cho DLQ / manual replay.
- Khi không chấp nhận mất event, dùng **persistent outbox / store-forward** trước khi publish lên message bus.

### 3.4 Batch Integration
- Phù hợp cho: data warehouse/lake, reporting, BI, AI training, legacy integration
- **Không dùng** cho nghiệp vụ realtime
- Dùng khi: đồng bộ dữ liệu lớn theo chu kỳ, ETL/ELT

---

## 4. Deployment Architecture Standard

### 4.1 Cloud Strategy
- Ưu tiên **`Multi-Cloud-Ready`** — tránh vendor lock-in
- **GCP-specific** cho phép khi: hệ thống không có kế hoạch mở rộng ra ngoài hoặc tính năng GCP đặc thù thực sự cần thiết
- **Private Cloud / On-prem** khi: yêu cầu data sovereignty, tuân thủ pháp lý

### 4.2 Deployment Model — Phần ảnh hưởng đến code design

Deployment context ảnh hưởng trực tiếp đến các quyết định code — AI cần hỏi user để xác định:

| Câu hỏi | Tại sao quan trọng cho code                                                                                             |
|---------|-------------------------------------------------------------------------------------------------------------------------|
| Service này là `internal-only` hay `public-facing`? | `internal-only` → có thể dùng basic auth / mTLS / service mesh; `public-facing` → cần OAuth 2.0, API key, rate limiting |
| Service chạy đơn lẻ (`single instance`) hay `multi-instance`? | `multi-instance` → code phải stateless, shared cache, distributed locks                                                 |
| Container hay serverless? | Serverless → cần chú ý cold start, small bundle, và connection pooling phù hợp                                          |
| Có reverse proxy / API Gateway phía trước không? | Có → không cần TLS termination ở app level; không có → app phải tự handle                                               |
| Database có phải shared (nhiều service cùng dùng) không? | Shared DB là vi phạm bounded context — cần ADR nếu exception                                                            |

### 4.3 Bắt buộc thể hiện trong architecture doc

- Các môi trường: Dev / SIT / UAT / Prod
- Cơ chế HA và DR: RTO/RPO requirements
- Cách các component giao tiếp (`network topology` — ảnh hưởng auth model)
- Scaling model: auto-scale, manual scale, hay `single instance`

---

## 5. Caching Strategy

Phase Architecture quyết định **layer nào cache, cache bằng gì, invalidation thế nào**. Không để mỗi layer tự quyết.

| Layer | Khi nào | Tooling |
|-------|---------|---------|
| Browser cache | Static assets | `Cache-Control: max-age, immutable`; ETag |
| **CDN (BẮT BUỘC cho asset)** | Image / video / static JS / CSS / font | CloudFront / Cloudflare / Fastly / Akamai |
| Edge cache | API có thể cache (read-heavy, low-personalization) | Varnish / Cloudflare Workers |
| Server-side cache | Hot DB query, computed result | Redis / Memcached |
| DB query cache | Aggregations, slow joins | Materialized view |
| Application memory | Reference data ít đổi | In-process LRU |

Rule:
- **Image / static asset BẮT BUỘC qua CDN** (không serve trực tiếp từ origin).
- HTTP caching headers: `Cache-Control`, `ETag`, `Last-Modified` — set rõ ràng.
- Invalidation: TTL + event-based (purge khi data đổi).
- Cache key: include version để rotate khi schema đổi.

---

## 6. Background Jobs & Queues

Chọn queue tech theo nhu cầu:

| Tech | Throughput | Ordering | Persistence | Use case |
|------|-----------|----------|-------------|----------|
| Redis (Streams / Pub-Sub) | High | Partial | Optional | Real-time, light job |
| RabbitMQ | Mid-high | FIFO per queue | Yes | Complex routing, RPC |
| AWS SQS | High | FIFO option | Yes | Simple decouple |
| Kafka | Very high | Strict per partition | Yes | Event sourcing, log |

Bắt buộc:
- **Retry:** exponential backoff (1s, 2s, 4s...), max 5 retries.
- **DLQ (Dead Letter Queue):** mọi persistent job phải có DLQ; alert khi DLQ depth > N.
- **Idempotency key:** mọi job có business effect phải idempotent (duplicate delivery không gây side effect lặp).
- **Visibility timeout / ack timeout:** match thời gian xử lý dài nhất; không infinite.
- **Monitoring:** queue depth, processing latency, error rate, DLQ depth — push lên metrics.

---

## 7. Resilience Patterns

Bắt buộc cho mọi outbound call (DB / cache / API / queue):
- **Timeout:** mặc định 5s; never infinite; per-call configurable.
- **Retry:** exponential backoff với jitter; max 3 retries; chỉ retry idempotent ops.
- **Circuit breaker:** threshold (vd 50% failure trong 30s) → open; half-open thử lại sau 60s.
- **Bulkhead:** thread pool / connection pool isolated per dependency để 1 service chậm không kéo cả app.
- **Graceful degradation:** fallback response (cached / static / error UX) khi dependency down — không 500.
- **Load shedding:** trả 503 + `Retry-After` khi vượt capacity; không queue vô hạn.

Tooling: Resilience4j (Java), Polly (.NET), opossum (Node), tenacity (Python).

---

## 8. Notification Channels

| Channel | Provider gợi ý |
|---------|---------------|
| Email | SendGrid / AWS SES / Mailgun / Postmark |
| SMS | Twilio / AWS SNS / local provider (Vietnam: VMG / Viettel) |
| Push (mobile) | FCM (cross) + APNs (iOS direct) |
| In-app | Service riêng + WebSocket / SSE |

Bắt buộc:
- **Template management** trong code repo, versioned, có fallback lang.
- **Consent / preference:** user có thể opt-out per channel; respect Do-Not-Disturb.
- **Retry + DLQ** cho send failure (transient); permanent failure → mark bounce, không retry.
- **Rate limiting** per recipient (chống spam, comply CASL / CAN-SPAM).
- **Tracking:** delivered, opened, clicked, bounced.
- **PII:** redact trong log; template không leak data đến third-party email service.
