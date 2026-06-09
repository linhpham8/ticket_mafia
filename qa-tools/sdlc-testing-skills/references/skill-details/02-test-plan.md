# Detailed Procedure: 02-test-plan

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

- [ ] Đủ 11 mục bắt buộc, không còn placeholder `{...}`
- [ ] Mục 11 — Approval: đã điền tên người phê duyệt (tối thiểu QC Lead + PM)
- [ ] `project/qa-config.yaml` đã xuất đủ các field bắt buộc
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `current_sprint`

---

## Đầu vào bắt buộc

| Thông tin | Bắt buộc |
|---|---|
| Danh sách ticket / epic / feature (key, summary, status) | ✅ |
| Thời gian dự án / milestone (ngày bắt đầu – kết thúc) | ✅ |
| Danh sách nhân lực QC và vai trò | ✅ |
| Môi trường và công cụ | ✅ |
| Tên dự án, version, milestone | ✅ |

Thiếu thông tin → ghi `[Cần bổ sung]`, hỏi lại. Không đoán mò.

## Bước 0 — Đọc qa-config.yaml (nếu có)

Nếu project đã có `qa-config.yaml` → đọc và dùng trực tiếp các giá trị sau, không hỏi lại:

| Field trong config | Dùng cho mục Test Plan |
|---|---|
| `project.name`, `project.sprint` | Mục 1 — Thông tin chung |
| `project.domain`, `project.architecture` | Mục 3 — Phương pháp & Risk |
| `team.*` | Mục 8 — Nhân lực |
| `environments.*` | Mục 8 — Môi trường |
| `tools.*` | Mục 3 — Công cụ, Mục 10 — Deliverables |
| `scope.modules` | Mục 2 — Phạm vi |
| `exit_criteria.*` | Mục 5 — Exit Criteria |
| `suspension_criteria.*` | Mục 6 — Suspension Criteria |
| `uat.required`, `uat.stakeholders` | Mục 2 — Scope, Mục 10 |
| `accessibility.required` | Mục 2 — Loại kiểm thử áp dụng |

Nếu chưa có `qa-config.yaml` → tiến hành Bước 1 như bình thường, sau đó thực hiện Bước 4 để xuất qa-config.yaml.

## Bước 0.5 — Đọc toàn bộ feature file trong thư mục dự án (bắt buộc)

Trước khi sinh nội dung, **đọc tất cả file `.md` trong thư mục chứa feature requirements (VD: `docs/features/`)** (bỏ qua `feature-template.md`).

Từ mỗi feature file, ánh xạ vào Master Test Plan:

| Trường trong feature file | Dùng cho mục |
|---|---|
| `Module`, `Feature`, `Ticket IDs` | Mục 1 — Danh sách ticket, phạm vi |
| `Business goal` | Mục 1 — Bối cảnh, Mục 3 — Chiến lược |
| `In scope` | Mục 2 — In Scope |
| `Out of scope` | Mục 2 — Out of Scope |
| `Acceptance criteria` | Mục 2, Mục 4 — Entry Criteria bổ sung |
| `Business rules` | Mục 3 — Kỹ thuật test |
| `Main flow`, `Alternate flows`, `Negative flows` | Mục 3 — Approach, cơ sở estimate |
| `Dependencies` | Mục 2 — Out of Scope (nếu external), Mục 9 — Rủi ro |
| `Preconditions` | Mục 8 — Tài khoản & dữ liệu test |
| `Open questions` | Mục 9 — Rủi ro ("Chưa rõ requirement") |

**Quy tắc:**
- Nếu `scope.modules` trong config vẫn còn placeholder → bỏ qua config, dùng `Module` từ feature file.
- Nếu thư mục `features/` không tồn tại → ghi `[Chưa có feature requirement]` và tiếp tục.

## Bước 1 — Xác định domain, kiến trúc và scope tổng thể

Đọc ticket/feature/BRD để xác định:
- Domain: fintech / ecommerce / logistics / SaaS / healthcare...
- Kiến trúc: monolith / microservices / mobile / API-only
- Scope tổng thể: số module, số WS/sprint, số tính năng

## Bước 2 — Sinh nội dung 11 mục

Đọc `../../references/test-plan-template.md` để lấy cấu trúc chi tiết.

**11 mục bắt buộc của Master Test Plan:**

1. **Thông Tin Chung** — tên dự án, milestone, mã tài liệu, người tạo/phê duyệt, phạm vi feature
2. **Phạm Vi Kiểm Thử** — In Scope / Out of Scope / loại test áp dụng (Functional, NFT, UAT...)
3. **Phương Pháp & Chiến Lược** — domain/arch, risk-based strategy, kỹ thuật TC, **lịch trình thực hiện** (timeline ngược từ go-live), **strategy matrix**, NFT breakdown
4. **Tiêu Chí Vào (Entry Criteria)** — điều kiện BẮT BUỘC phải đạt trước khi bắt đầu test
5. **Tiêu Chí Ra (Exit Criteria)** — điều kiện PASS để release, điều kiện FAIL, **tách biệt test completion vs go-live conditions**
6. **Tiêu Chí Tạm Dừng & Tiếp Tục** — ngưỡng cụ thể (%, giờ), không mơ hồ
7. **KPI & Metrics** — DRE, automation %, coverage by risk level, pass rate target
8. **Kế Hoạch & Lịch Trình** — estimate theo độ phức tạp, không chia đều
9. **Nhân Lực & Môi Trường** — team roles, environments, test accounts
10. **Rủi Ro & Phương Án Dự Phòng** — ≥ 4 rủi ro thực tế, không chung chung
11. **Tài Liệu Đầu Ra & Phê Duyệt** — deliverables table, **ô ký duyệt chính thức**

Nguyên tắc bắt buộc:
- Không chia đều estimate — dựa trên độ phức tạp thực tế từng ticket/module
- Suspension Criteria phải có ngưỡng cụ thể (%, số giờ)
- Entry Criteria phải ghi rõ "ai xác nhận" và "bằng cách nào"
- Exit Criteria phải tách 2 phần: test completion conditions vs go-live decision conditions — **bắt buộc có cả danh sách điều kiện FAIL rõ ràng**
- KPI phải có baseline hoặc target cụ thể (số, %)
- Severity/Priority phải viết đầy đủ (Severity Critical, Severity High, Priority Critical...) — không dùng S1/S2/P1/P2
- Nhân sự: chỉ điền tên người đã xác nhận; dùng `[Cần xác nhận]` cho chưa biết — không đoán mò hoặc lấy tên từ tài liệu khác

**Ranh giới Master Test Plan vs Sprint Test Plan — bắt buộc tuân thủ:**

| Thuộc Master Test Plan (chiến lược) | Thuộc Sprint Test Plan / Jira (tác chiến) |
|---|---|
| Strategy matrix theo risk group (4–5 dòng) | Per-feature automation % chi tiết |
| Phương pháp test + automation milestone target | TC design technique mapping từng feature |
| NFT types + approach + owner | Golden dataset spec cụ thể |
| Lịch trình phase-level (5 phase) | Task-by-task với sprint/người/giờ cụ thể |
| AI Policy: 1 bảng tổng hợp | Execution acceleration tactics |
| Test data: nguyên tắc + công cụ | Sprint execution checklist |

### Chi tiết Mục 3.1 — Manual vs Automation

Bảng phương pháp theo loại test với **automation target milestone-based** (không phẳng suốt dự án):

| Loại test | Phương pháp | Automation target | Framework |
|---|---|---|---|
| Functional — API | Automation ưu tiên + Manual edge case | ≥ 70% | Robot Framework |
| Integration | Manual lần đầu + Auto sau khi flow ổn định | ≥ 40% | Robot Framework |
| Regression | Automation toàn bộ, CI-triggered | = 100% | Robot Framework |
| Performance | Tool-driven | = 100% | k6 / JMeter |
| UAT | Manual user walkthrough | 0% | — |

**Target tổng thể:** milestone-based — VD: ≥ 60% giai đoạn functional, ≥ 75% khi vào SIT/NFT.

**Kỹ thuật thiết kế TC:** Gộp 1 câu trong mục này — không tạo section riêng. VD: "Áp dụng EP, BVA, Decision Table cho API; State Transition cho Saga/GitOps; OWASP Top 10 cho Security; Idempotency cho Audit."

---

### Chi tiết Mục 3.2 — AI Policy

**Chỉ viết 1 bảng tổng hợp duy nhất** — không viết thành policy document với nhiều sub-section:

| Hoạt động AI hỗ trợ | QC review bắt buộc | Ràng buộc dữ liệu |
|---|---|---|
| Sinh Test Plan / Sprint Plan / HLTC | QC Lead review và ký duyệt | Không đưa architecture detail, credentials vào AI |
| Sinh draft Test Case | QC Engineer review từng TC, đối chiếu FRS | Không đưa PII thực vào AI — vi phạm Decree 13/2023 |
| Sinh test data synthetic | QC Engineer verify không chứa PII thực | Chỉ synthetic data |
| Sinh draft Automation Script | Pass DoD checklist trước khi commit | — |
| Tổng hợp Report | QC Lead review trước khi phát hành | — |

---

### Chi tiết Mục 3.3 — Strategy Matrix

**Gộp theo risk group (4–5 dòng)** — không liệt kê từng feature riêng lẻ. Automation % chi tiết thuộc Sprint Plan.

| Nhóm rủi ro | Feature tiêu biểu | Loại test áp dụng | Mức độ coverage |
|---|---|---|---|
| Rất cao | {auth, core API, data access} | Functional + Integration + Security + NFT | 100% — hard blocker |
| Cao | {audit, identity, governance} | Functional + Integration + Security/Compliance | 100% — compliance sign-off |
| Trung bình | {catalog, metadata, search} | Functional + Integration | ≥ 95% |
| Thấp | {view, report, UI} | Functional | ≥ 90% |

### Chi tiết Mục 3.4 — NFT Breakdown

Với mỗi loại NFT có trong scope, mô tả scope + tool + metric + owner. Cột **Owner** quan trọng — Security thường do Security Team sở hữu, QA chỉ hỗ trợ môi trường.

| NFT Type | Scope | Tool | Metric mục tiêu | Owner |
|---|---|---|---|---|
| Performance — Load | {core API endpoint} | k6 / JMeter | p95 < {N}ms tại {N} concurrent users `[Chờ PO]` | QA — Skill 11 |
| Performance — Stress | {core API} | k6 | Tìm breaking point — error rate > 5% | QA — Skill 11 |
| Performance — Soak | {long-running service} | k6 | 80% load × 2–4h; no memory leak | QA — Skill 11 |
| Performance — Spike | {auth/entry API} | k6 | 0 → peak trong 30s; đo recovery time | QA — Skill 11 |
| Availability / Uptime | Toàn platform | Grafana monitoring | ≥ {N}% uptime `[Chờ PO]` | QA + Ops |
| Resilience | {fail-closed, circuit breaker} | Manual + API test | System block request khi dependency down | QA |
| Observability / Alert | {monitoring stack} | Alert validation | Alert fire đúng threshold; no silent failure | QA + Ops |
| Security | {IAM, API layer} | OWASP ZAP + Burp Suite | Critical = 0, High = 0 | **Security Team** — QA hỗ trợ env + evidence |
| Accessibility | {UI page} | axe-core | WCAG 2.1 AA ≥ {N}% | QA — Skill 15 |

**Lưu ý:** Nếu SRS có trường NFR còn TBD → **bắt buộc tạo bảng NFR Open Questions gửi PO** ngay trong phần này. Không để placeholder im lặng — kết quả test không có SLA target thì không có giá trị sign-off.

**Mẫu NFR Open Questions:**

| # | Câu hỏi | Lý do cần biết | Ảnh hưởng nếu thiếu | Người cần trả lời | Deadline |
|---|---|---|---|---|---|
| NFR-01 | Concurrent users tối đa? | Thiết kế load scenario | Load test không có baseline | PO / SA | Trước Sprint NFT |
| NFR-02 | Data volume / dataset size? | p95 latency của query engine | Query SLA không xác định được | PO / Data Architect | Trước Sprint NFT |

### Chi tiết Mục 3 — Lịch trình thực hiện (3.6)

> Phải trình bày **ngược từ go-live** — không chỉ là dependency chain kỹ thuật.

**Bắt buộc có đủ 5 phần:**

1. **Tổng quan timeline theo sprint** — bảng sprint × phase × feature coverage + danh sách mốc cứng ngược từ go-live (go-live → UAT sign-off → SIT start → Functional test end → ...)
2. **Lịch trình Functional Test** — phase nào, sprint nào, module nào, điều kiện vào mỗi phase, dependency chain thực thi
3. **Lịch trình SIT** — thời gian cụ thể, điều kiện vào, scope cross-module, người thực hiện, exit condition
4. **Lịch trình UAT** — thời gian, scope user journey, người tham gia (vai trò thực tế), sign-off deadline
5. **Lịch trình Performance Test** — thời gian, tool, điều kiện vào, và **4 loại test với scenario + target cho từng loại:**

   | Loại | Mục tiêu | Scenario mẫu |
   |---|---|---|
   | **Load test** | Xác nhận SLA ở tải bình thường (expected concurrent users) | Giữ {N} users × 30 phút; đo p95 |
   | **Stress test** | Tìm breaking point | Tăng dần → 2× → 3× users đến khi error rate > 5% |
   | **Soak test** | Phát hiện memory leak, resource exhaustion | 80% expected load × 2–4 giờ liên tục |
   | **Spike test** | Đánh giá khả năng phục hồi khi burst | 0 → peak trong 30 giây; đo thời gian recover |

### Chi tiết Mục 4 — Entry Criteria

| Điều kiện | Xác nhận bởi | Phương thức xác nhận |
|---|---|---|
| Build deploy thành công lên staging | Dev Lead | Jenkins/CI log hoặc email xác nhận |
| Smoke test pass ≥ {N}% | QC | Smoke test result |
| Test data sẵn sàng | QC | Data verification script |
| Requirement freeze hoặc change log rõ ràng | BA/PM | Confluence page |
| Môi trường ổn định ≥ {N} giờ trước khi test | Ops | Uptime monitoring |

### Chi tiết Mục 5 — Exit Criteria

**Phần A — Test Completion (QC quyết định):**

| Chỉ số | Ngưỡng |
|---|---|
| Pass rate tổng thể | ≥ {N}% |
| Pass rate nhóm rủi ro Rất cao / Cao | = 100% |
| Bug Severity Critical còn open | = 0 |
| Bug Severity High còn open | ≤ {N} (PM/Tech Lead xác nhận chấp nhận) |
| TC executed / tổng TC kế hoạch | ≥ 95% |
| Regression pass rate | = 100% |

**Điều kiện FAIL — bắt buộc phải liệt kê (không chỉ PASS):**
- Pass rate < {N}% (thấp hơn ngưỡng warning)
- Bất kỳ bug Severity Critical nào còn open
- Auth bypass detected (endpoint trả 200 khi không có valid token)
- Audit log có thể bị modify/delete
- Raw PII phát hiện trong storage layer (nếu có privacy feature)
- Fail-Closed bị vi phạm (asset không có policy nhưng vẫn accessible)

**Phần B — Go-Live Decision (PM/Product quyết định):**
- Test completion đạt Phần A
- Security audit: Severity Critical = 0, Severity High = 0
- Performance pass tại baseline load (từ NFR PO)
- UAT sign-off từ {stakeholder}
- Compliance/Legal sign-off nếu có tính năng Privacy/PII/IDR
- Risk acceptance có văn bản từ PM/Tech Lead nếu còn Severity High open khi release

### Chi tiết Mục 7 — KPI & Metrics

| KPI | Công thức | Target | Ghi chú |
|---|---|---|---|
| Pass Rate — Tổng | pass / (pass + fail) × 100% | ≥ {N}% | Không tính blocked |
| Pass Rate — Nhóm rủi ro cao nhất | pass_critical / total_critical × 100% | = 100% | Hard requirement trước release |
| Defect Removal Efficiency (DRE) | bugs QA / (bugs QA + bugs UAT/Prod) × 100% | **≥ 95%** cho hệ thống compliance/PII; ≥ 85% cho hệ thống thường | Đo sau release |
| Automation Coverage | TC automated executed / tổng TC executed × 100% | Milestone-based — xem mục 3.1 | Chỉ tính TC đã chạy |
| TC Execution Rate | TC executed / tổng TC kế hoạch | ≥ 95% | |
| Audit / Privacy Compliance | Số vi phạm tìm thấy | = 0 | Hard requirement — regulatory |
| Health Score | Xem `references/report-template.md` | ≥ {N}/100 | Input Skill 07/08 — không dùng để go-live |

### Chi tiết Mục 8 — Kế Hoạch & Lịch Trình

**Dùng bảng phase-level (4–6 dòng)** — KHÔNG liệt kê task-by-task. Task chi tiết thuộc Sprint Plan / Jira.

| Phase | Sprint | Thời gian | Nội dung chính | Team phụ trách | Effort ước tính |
|---|---|---|---|---|---|
| Chuẩn bị | {sprint} | {dates} | TC writing, test data script | {team} | {N}h |
| Functional Test | {sprint} | {dates} | Thực thi Functional Test theo dependency chain | {team} | {N}h |
| SIT + NFT | {sprint} | {dates} | Integration test cross-module; Performance; Security (Security Team) | {team} | {N}h |
| UAT + Retest | {sprint} | {dates} | UAT support; retest bug | {team} | {N}h |
| Go/No-Go | {sprint} | {dates} | Final sign-off; production smoke checklist | QC Lead | {N}h |

Kèm theo: **Capacity check** = tổng effort / (capacity/sprint × số sprint) = % utilization.

---

### Chi tiết Mục 11 — Approval

| Vai trò | Tên | Ngày ký | Chữ ký |
|---|---|---|---|
| QC Lead / Test Manager | {Tên} | | |
| Tech Lead / Dev Lead | {Tên} | | |
| Product Manager / BA | {Tên} | | |
| Project Manager | {Tên} | | |
| Compliance / Legal | {Tên} | | |

> Tài liệu chỉ được triển khai khi có ít nhất QC Lead và PM ký duyệt.
> **Nếu project có tính năng Privacy/PII/IDR** → Compliance/Legal bắt buộc ký trước go-live.

## Bước 3 — Xuất file

Xuất Markdown đầy đủ 11 mục.

**Naming convention** (theo `references/project-folder-convention.md`):
`Test_Plan_{project.code}_{milestone}_v{semver}_{yyyy-mm-dd}_{HHmm}.md`

**Lưu vào:** `output_paths.test_plan` từ qa-config (default: `testing-output/test-plan/`)

**Không ghi đè file cũ** — mỗi lần tạo/sửa tạo file mới với timestamp mới.

## Bước 4 — Xuất qa-config.yaml

Sau khi Master Test Plan hoàn chỉnh, tự động trích xuất thành `project/qa-config.yaml` theo schema tại `references/qa-config-schema.yaml`.

**Field bắt buộc tối thiểu — trả NEEDS_CONTEXT nếu thiếu:**
- `project` (name, code, sprint, domain, architecture)
- `environments.staging` (url, auth_required)
- `tools` (test_management, bug_tracker, automation.ui/api)
- `scope` (type, modules)
- `exit_criteria` (pass_rate, health_score_baseline, max_s1_open, max_s2_open, tc_executed_rate)

**Quy tắc extract:**
- Bám đúng key order và naming theo `references/qa-config-schema.yaml`
- Field optional để `~` nếu Test Plan không đề cập
- Không để placeholder `<...>` trong output cuối

**Lưu file:** `project/qa-config.yaml` (hoặc `testing-output/qa-config.yaml` nếu chưa có thư mục project/)

Sau khi tạo xong, gợi ý người dùng dùng **03-sprint-test-plan** cho các sprint tiếp theo — ngắn gọn hơn, tái sử dụng config này.
