---
status: DRAFT
version: v1
sprint: 1
phase: architecture
created: YYYY-MM-DD
updated: YYYY-MM-DD HH:MM
approved_by:
---

# Non-Functional Requirements — {{PROJECT_NAME}}

<!-- This file is the Living Truth root for NFRs (moved from product to architecture in Phase 9).
     Each NFR is a mergeable anchored block. Categories (Performance, Availability, etc.) are
     organizational headings only — not anchored.

     Mỗi thuộc tính chất lượng ưu tiên BẮT BUỘC có ít nhất 1 Architecturally Significant Scenario.
     Xem thêm: prism/core/standards/architecture-solution-standards.md — mục 1. -->

<!-- ## Stable ID Anchor Convention (Phase 9+)
     Each NFR-NNN block in §1.1 below MUST be preceded by `<!-- ID: NFR-NNN -->` on its own line.
     Atomic ID (all modes — Guided AND Freedom): `python .prism/core/tools/get_next_id.py --type NFR`
     Strict format: `NFR-\d{3,}` (zero-padded ≥3 digits).
     (Guided seal only) The anchor also lets `apply_proposal.py` merge this block at sprint seal — Freedom has no seal but still issues the ID above and keeps the anchor. -->

<!-- PRISM:LT-SKELETON-END -->

## 1. NFR Catalog

### 1.1 NFR Items (anchored, mergeable)

<!-- One anchored block per NFR. Add new NFRs via proposal `## New`; update existing via `## Updated`. -->

<!-- ID: NFR-NNN -->
### NFR-NNN: {{NFR Title — VD: API p95 latency}}

- **Category**: Performance | Availability | Scalability | Security | Observability | Cost | Compliance | Accessibility
- **Target**: <!-- VD: p95 < 200ms cho mọi read endpoint -->
- **Source**: <!-- PRD §3.1 / ADR-NNN / external compliance ref -->
- **Priority**: Bắt buộc | Nên có | Tuỳ chọn
- **Verification**: <!-- VD: Load test in staging — TC-NNN -->
- **Applies to**: <!-- all epics | EP-NNN, EP-NNN | specific service -->

<!-- ID: NFR-NNN -->
### NFR-NNN: {{Another NFR}}

<!-- Lặp lại block ở trên cho mỗi NFR. -->

### 1.2 NFR Summary View

<!-- Bảng này là VIEW của §1.1 cho stakeholder đọc nhanh. KHÔNG mergeable (re-derive khi cần). -->

| NFR | Category | Target | Source | Priority |
|---|---|---|---|---|
| NFR-NNN | Performance | | PRD | Bắt buộc |

## 2. Performance

| Metric | Target | Phạm vi | Cách đo lường |
|---|---|---|---|
| p95 latency | | | |
| Throughput | | | |

### Performance Scenarios

<!-- Mỗi scenario: tình huống thực tế có số liệu → phản ứng hệ thống → chỉ số đo lường cụ thể -->

#### Scenario P1: {{Tên scenario}}

| | Mô tả |
|---|---|
| **Context** | <!-- Tình huống thực tế, có số liệu cụ thể. VD: Dựa trên lịch sử, 500 user đồng thời submit form trong khung giờ cao điểm --> |
| **System Response** | <!-- Hệ thống phản ứng như thế nào. VD: Hệ thống xử lý đủ request, không có request bị từ chối --> |
| **Metrics** | <!-- Chỉ số đo được. VD: p95 response time ≤ 2s; error rate < 0.1% --> |

## 3. Availability And Resilience

| Yêu cầu | Target | Ghi chú |
|---|---|---|
| Availability | | |
| Recovery Time Objective (RTO) | | |
| Recovery Point Objective (RPO) | | |
| Backup / restore | | |

### Resilience Scenarios

<!-- Bắt buộc khi Availability/Reliability là thuộc tính ưu tiên.
     Phải có ít nhất 1 scenario cho tải tới hạn (peak load) thể hiện yêu cầu Performance dưới tải cao. -->

#### Scenario R1: {{Tên scenario — VD: Tải API cao đột biến}}

| | Mô tả |
|---|---|
| **Context** | <!-- VD: Số lượng request đạt ngưỡng 15.000/giây trong 30–60 giây --> |
| **System Response** | <!-- VD: Một số request bị từ chối có error message rõ ràng; ops team có thể nhận ra tình trạng --> |
| **Metrics** | <!-- VD: Requests bị từ chối không quá 30%; response time của request thành công tăng không quá 10% --> |

## 4. Scalability

<!-- Bắt buộc khi Scalability là thuộc tính ưu tiên.
     Phải có scenario cho: lộ trình scale theo roadmap HOẶC các thời điểm scale theo sự kiện.
     Scenario phải thể hiện: yêu cầu về chi phí, Availability, Performance khi scale. -->

### Scalability Scenarios

#### Scenario S1: {{Tên scenario — VD: Tăng trưởng có lộ trình}}

| | Mô tả |
|---|---|
| **Context** | <!-- VD: Lịch sử vận hành cho thấy khối lượng giao dịch tăng 10% mỗi quý --> |
| **System Response** | <!-- VD: Hệ thống đáp ứng lộ trình scale mà response time và availability không thay đổi đáng kể --> |
| **Metrics** | <!-- VD: Chi phí cloud tăng không quá 10%/quý; p95 latency không tăng quá 5%; uptime không giảm quá 2% --> |

## 5. Security And Compliance

| Yêu cầu | Target / Control | Ghi chú |
|---|---|---|
| Auth | | |
| Encryption | | |
| Compliance | | |

## 6. Observability And Operations

| Yêu cầu | Target | Ghi chú |
|---|---|---|
| Logging | | |
| Metrics | | |
| Alerting (SLO-based) | | |
| Uptime monitoring | | |

## 7. Cost / Capacity Constraints

| Khu vực | Ràng buộc | Ghi chú |
|---|---|---|
| Compute | | |
| Storage | | |
| Traffic | | |

## 8. Implementation Configuration Mapping

<!-- NFR targets phải được wire vào configuration values cụ thể — không chỉ tồn tại trong document. -->
<!-- Bảng này là bridge giữa NFR targets và `application.yml` / Infrastructure as Code. -->
<!-- Implementation Phase đọc bảng này để biết config key nào cần set với value bao nhiêu. -->

| NFR ID | NFR Target | Config Key | Recommended Value | Who Sets It | Notes |
|---|---|---|---|---|---|
| NFR-NNN | p95 API latency ≤ 200ms | `http.client.timeout-ms` | `150` *(80% của target để có margin)* | App config (`application.yml`) | HTTP client timeout cho outbound calls |
| NFR-NNN | p95 API latency ≤ 200ms | `db.pool.connection-timeout-ms` | `5000` | App config | DB connection acquisition timeout |
| NFR-NNN | Max 1000 concurrent users | `db.pool.max-size` | `50` *(N concurrent users / 20 = pool size rule of thumb)* | App config | Tùy DB engine và query patterns |
| NFR-NNN | Max 1000 concurrent users | `server.thread-pool.max` | `200` | App config / Kubernetes |  |
| NFR-NNN | Cache hit rate ≥ 80% | `cache.default-ttl-seconds` | `300` *(5 phút — adjust per entity)* | App config | |
| NFR-NNN | Rate limit 100 req/min per user | `rate-limiter.requests-per-minute` | `100` | App config | |
| NFR-NNN | Rate limit 100 req/min per user | `rate-limiter.bucket-capacity` | `10` *(burst allowance)* | App config | |
| NFR-NNN | Circuit breaker: open after 5 failures | `circuit-breaker.failure-threshold` | `5` | App config | Per integration point |
| NFR-NNN | Circuit breaker: open after 5 failures | `circuit-breaker.wait-duration-seconds` | `30` | App config | Half-open retry interval |
| NFR-NNN | Uptime 99.9% → RTO ≤ 52 min/year | `health-check.interval-seconds` | `30` | Kubernetes liveness probe | |
| NFR-NNN | Uptime 99.9% → RTO ≤ 52 min/year | `deployment.replicas.min` | `2` | Kubernetes / Terraform | HA — không bao giờ chạy single replica |

<!-- Thêm mappings theo NFR targets thực tế của project. Nếu NFR target chưa có config key tương ứng → ghi "TBD — cần architect input". -->

---

## Self-Review Checklist

- [ ] Quality Contract refs satisfied: `DOC-1`, `DOC-2`, `DOC-3`, `LINK-1`, `LINK-2`, `ORB-1`, `ARCH-1`
- [ ] Mọi NFR đều có target đo được
- [ ] Target gắn với nguồn yêu cầu cụ thể (PRD section, ADR, v.v.)
- [ ] Các thuộc tính chất lượng ưu tiên đều có Architecturally Significant Scenario với đủ 3 phần: Context / System Response / Metrics
- [ ] Khi Availability/Reliability là ưu tiên: có scenario tải tới hạn
- [ ] Khi Scalability là ưu tiên: có scenario scale với chi phí + Availability + Performance
- [ ] §8 Config Mapping Table có entry cho mọi NFR target quan trọng — bridge từ target đến `application.yml` / IaC
- [ ] Không có NFR mơ hồ như "hệ thống phải nhanh" hay "phải bảo mật" không có số liệu cụ thể
- [ ] Compliance constraints rõ ràng và actionable
