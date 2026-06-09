# Cấu Trúc Master Test Plan — 11 Mục (IEEE 829 / ISTQB)

> Skill 01 đọc file này để xác định cấu trúc và nội dung từng mục.
> Quy tắc bắt buộc:
> - Đủ 11 mục, không bỏ mục nào
> - Không còn placeholder trống trong nội dung chính
> - Estimate có lý do, KHÔNG chia đều giữa các ticket
> - Suspension Criteria phải có ngưỡng cụ thể (%, số giờ) — không được mơ hồ
> - Entry Criteria phải ghi rõ ai xác nhận và bằng cách nào
> - Exit Criteria phải tách Test Completion vs Go-Live Decision
> - KPI phải có target cụ thể (số, %)
> - Viết bằng tiếng Việt có dấu
>
> Luồng chuẩn:
> - Hoàn thành 11 mục Master Test Plan (skill 02 — qa-core/02-test-plan)
> - Thực hiện Bước 4 trong skill 02 để xuất `qa-config.yaml`
> - Từ sprint kế tiếp, dùng skill 03 (qa-core/03-sprint-test-plan) — ngắn gọn, tái sử dụng config

---

## Mục 1 — Thông Tin Chung

Bao gồm:
- Tên dự án, version, milestone (VD: MVP1, Sprint 12)
- Mã tài liệu: `TP-{ProjectCode}-{Milestone}-{YYYYMMDD}`
- Người tạo, người phê duyệt, ngày tạo, trạng thái (Draft / Review / Approved)
- Danh sách feature/ticket trong phạm vi (key, summary, WS/sprint, độ phức tạp ước tính: Thấp / Trung bình / Cao)
- Tài liệu tham chiếu: BRD/PRD, sprint board, môi trường, repo

---

## Mục 2 — Phạm Vi Kiểm Thử (Scope)

Bao gồm:
- **Trong phạm vi (In Scope):** Liệt kê từng module/tính năng sẽ test, loại test áp dụng (Functional / Regression / Smoke / SIT / Performance / Security / UAT), lý do ưu tiên
- **Ngoài phạm vi (Out of Scope):** Liệt kê những gì KHÔNG test và lý do cụ thể (không thay đổi / chưa sẵn sàng môi trường / phụ thuộc team khác)
- **Loại kiểm thử áp dụng:** Đánh dấu từng loại:

| Loại test | Áp dụng | Ghi chú |
|---|---|---|
| Functional | ✅ / ❌ | |
| Integration / SIT | ✅ / ❌ | |
| Regression | ✅ / ❌ | |
| Smoke | ✅ / ❌ | |
| Performance | ✅ / ❌ | Skill 11 |
| Security | ✅ / ❌ | Skill 10 |
| Accessibility | ✅ / ❌ | Skill 15 |
| UAT | ✅ / ❌ | Skill 12 |

---

## Mục 3 — Phương Pháp & Chiến Lược Kiểm Thử (Approach & Strategy)

Bao gồm:
- **Domain và kiến trúc:** Fintech / Ecommerce / Logistics / SaaS / Healthcare và Monolith / Microservices / Mobile / API-only
- **Chiến lược:** Risk-based testing — ưu tiên theo mức độ thay đổi code + impact đến core flow
- **Kỹ thuật thiết kế TC:** EP, BVA, Decision Table, State Transition, Error Guessing, Exploratory — áp dụng từng kỹ thuật cho loại feature nào
- **Quy trình thực hiện:** Smoke → Functional → Integration → Regression → Retest → Report
- **Công cụ:** Tên cụ thể cho từng mục đích

### Strategy Matrix

Ánh xạ module → risk level → test type → priority:

| Module/Feature | Risk Level | Test Types | Priority | Ghi chú |
|---|---|---|---|---|
| {module} | High/Med/Low | Functional, SIT, Performance, Security | P1/P2/P3 | |

### NFT Breakdown

| NFT Type | Scope | Tool | Metric mục tiêu | Skill |
|---|---|---|---|---|
| Performance | {endpoint/flow} | k6 / JMeter | p95 < {N}ms, TPS ≥ {N} | skill 11 |
| Security | {module} | OWASP ZAP | Critical = 0, High = 0 | skill 10 |
| Accessibility | {page} | axe-core | WCAG 2.1 AA ≥ {N}% | skill 15 |

### 3a — Chiến lược thực thi nhanh (Execution Acceleration)

> Bắt buộc điền nếu số TC > 50 hoặc thời gian test ≤ 5 ngày làm việc.

- **Nhóm rule/TC theo pattern:** Liệt kê các nhóm TC có cùng cấu trúc input-output có thể chạy theo batch
- **Thứ tự ưu tiên thực thi:** Rule/TC nào phải chạy trước (S1 risk cao nhất), nhóm nào defer nếu hết giờ
- **Mutation strategy:** Bắt đầu từ golden dataset rồi mutate từng tiêu chí
- **Automation-first:** TC nào chạy tự động, TC nào manual — ghi rõ tỷ lệ mục tiêu
- **Parallel execution:** Nhóm TC nào có thể chạy song song

### 3b — Chiến lược sinh test data

> Bắt buộc điền — không để trống.

- **Golden dataset:** Mô tả 1 bộ data chuẩn dùng làm gốc để mutate
- **Loại data cần sinh:** BVA boundary values, EP partitions, normalize variants, threshold values
- **Công cụ / cách gen:** Script JSON/TSV tự động hay thủ công
- **Traceability:** Data file lưu tại `testing-output/test-data/`
- **Teardown:** Cách reset data sau mỗi lần chạy

---

## Mục 4 — Tiêu Chí Vào (Entry Criteria)

Điều kiện BẮT BUỘC phải đạt **trước khi** bắt đầu test. Mỗi điều kiện phải ghi rõ ai xác nhận và bằng cách nào:

| Điều kiện | Xác nhận bởi | Phương thức xác nhận |
|---|---|---|
| Build deploy thành công lên staging | Dev Lead | CI/CD log hoặc email xác nhận |
| Smoke test pass ≥ {N}% | QC | Smoke test result |
| Test data sẵn sàng và verified | QC | Data verification checklist |
| Requirement freeze hoặc change log rõ ràng | BA/PM | Confluence page |
| Môi trường ổn định ≥ {N} giờ trước khi test | Ops/Dev | Uptime monitoring |
| Test Plan được phê duyệt | QC Lead + PM | Ký duyệt Mục 11 |

---

## Mục 5 — Tiêu Chí Ra (Exit Criteria)

### Phần A — Test Completion (QC quyết định)

**Điều kiện PASS:**
- Pass rate: ≥ {X}% (cụ thể hóa theo dự án)
- S1 (Critical) còn open: = 0
- S2 (High) còn open: ≤ {N}
- TC đã thực hiện: ≥ {X}%
- Regression pass rate: = 100%

**Điều kiện FAIL (dấu hiệu phải dừng/không release):**
- Pass rate: < {X}%
- S1 còn open: ≥ 1
- Môi trường không ổn định: > {X} giờ trong ngày

### Phần B — Go-Live Decision (PM/Product quyết định)

Dựa trên Test Completion (Phần A) + business risk:
- Test completion đạt toàn bộ điều kiện Phần A
- Không có blocker business chưa giải quyết
- UAT sign-off từ {stakeholder} (nếu yêu cầu)
- Risk acceptance từ {người phê duyệt} nếu có S2 còn open khi release

---

## Mục 6 — Tiêu Chí Tạm Dừng & Tiếp Tục (Suspension Criteria)

> ⚠️ Quy tắc bắt buộc: MỌI điều kiện tạm dừng phải có ngưỡng số cụ thể.

**Điều kiện tạm dừng:**

| Điều kiện | Ngưỡng cụ thể | Hành động ngay |
|---|---|---|
| Tỷ lệ TC bị Blocked | > {30}% tổng TC | Dừng test, báo QC Lead, họp triage |
| Môi trường không khả dụng | > {4} giờ liên tục trong 1 ngày | Dừng, escalate Dev/Ops, ghi log |
| Bug S1 blocking (môi trường) | ≥ 1 | Dừng luồng liên quan, xác nhận root cause |
| Dữ liệu test bị corrupt | > {10}% data sai | Dừng, rebuild data |
| Pass rate sụt giảm đột ngột | < {60}% trong 1 ngày sau khi đã đạt {80}% | Dừng, phân tích, họp khẩn |

**Điều kiện tiếp tục:**
- Môi trường ổn định và được Dev/Ops xác nhận
- Bug S1 blocking đã fix và deploy lên staging
- Test data đã rebuild và verify
- QC Lead cho phép tiếp tục bằng văn bản (Slack / email)

---

## Mục 7 — KPI & Metrics

| KPI | Công thức | Target | Ghi chú |
|---|---|---|---|
| Pass Rate | pass / (pass + fail) × 100% | ≥ {N}% | Không tính blocked |
| Defect Removal Efficiency (DRE) | bugs tìm được trong test / tổng bugs × 100% | ≥ {N}% | Đo sau release |
| Automation Coverage | TC automated / tổng TC × 100% | ≥ {N}% | Chỉ tính TC được execute |
| Coverage by Risk | High-risk TC executed / tổng High-risk TC | = 100% | Bắt buộc trước release |
| TC Execution Rate | TC executed / tổng TC kế hoạch | ≥ {N}% | |
| Bug Detection Rate | bugs / TC | < {N} | Baseline từ sprint trước |
| Health Score | Công thức trong `references/report-template.md` | ≥ {N}/100 | |

---

## Mục 8 — Kế Hoạch & Lịch Trình (Testing Tasks & Schedule)

> ⚠️ KHÔNG chia đều giờ giữa các ticket. Phải ước tính dựa trên độ phức tạp thực tế.

Hướng dẫn estimate:
- **Thấp** (CRUD đơn giản, 1 luồng): 2–4h viết TC + 2–3h test
- **Trung bình** (logic nghiệp vụ, nhiều trường hợp): 4–8h viết TC + 4–6h test
- **Cao** (tích hợp, trạng thái phức tạp, security/payment): 8–16h viết TC + 8–12h test

| # | Nhiệm vụ | Ticket liên quan | Độ phức tạp | Người thực hiện | Thời gian | Effort | Ghi chú |
|---|---|---|---|---|---|---:|---|
| 1 | Viết TC Functional + SIT | {Ticket A, B} | Cao | {QC} | {Ngày N–M} | {N}h | |
| 2 | Viết TC Functional | {Ticket C} | Thấp | {QC} | {Ngày N} | {N}h | |
| 3 | Chuẩn bị Test Data | Tất cả | Trung bình | {QC} | {Ngày N} | {N}h | |
| 4 | Thực hiện Smoke Test | Tất cả | — | {QC} | {Ngày N} | {N}h | |
| 5 | Thực hiện Functional Test | {Ticket A, B, C} | — | {QC} | {Ngày N–M} | {N}h | |
| 6 | Regression Test | Core flows | — | {QC} | {Ngày N} | {N}h | |
| 7 | Retest sau fix | Theo bug report | — | {QC} | {Ngày N–M} | {N}h | |
| 8 | Tổng hợp Sprint Report | — | — | QC Lead | {Ngày N} | {N}h | |
| **Tổng** | | | | | | **{N}h** | |

---

## Mục 9 — Nhân Lực & Môi Trường (Resources & Environment)

**Nhân lực:**

| Vai trò | Tên | Trách nhiệm chính | % Thời gian |
|---|---|---|---:|
| QC Lead | {Tên} | Review TC, báo cáo, escalate blocker, quyết định suspend | {N}% |
| QC Engineer | {Tên} | Viết TC, thực hiện test, log bug | {N}% |

**Môi trường:**

| Môi trường | URL | Trạng thái | Auth | Ghi chú |
|---|---|---|---|---|
| Staging | {URL} | {Sẵn sàng / Chờ deploy} | {Basic auth / OAuth} | Deploy mới nhất: {ngày} |
| UAT | {URL} | {Sẵn sàng / Chưa có} | | |

**Tài khoản test cần chuẩn bị:**

| Loại tài khoản | Username | Role / Quyền |
|---|---|---|
| Admin | {email} | Toàn quyền |
| User thường | {email} | Quyền cơ bản |
| User không có quyền X | {email} | Kiểm tra negative case |

---

## Mục 10 — Rủi Ro & Phương Án Dự Phòng (Risks & Contingencies)

Liệt kê tối thiểu 4 rủi ro thực tế, không để chung chung:

| # | Rủi ro | Khả năng | Tác động | Phương án dự phòng |
|---|---|---|---|---|
| R1 | Môi trường staging không ổn định | Cao | Chặn {N}% TC | Backup môi trường / coordinate Ops từ ngày {N} |
| R2 | Requirement thay đổi giữa sprint | Trung bình | Phải viết lại {N}% TC | Review ticket daily, checkpoint ngày {N} |
| R3 | Thiếu test data | Trung bình | Block functional test | Chuẩn bị data script từ ngày {1} sprint |
| R4 | Bug S1 cuối sprint sát deadline | Trung bình | Risk release | Escalation path rõ ràng, exit criteria đã định nghĩa |
| R5 | QC member nghỉ đột xuất | Thấp | Delay {N} ngày | Cross-training, TC documentation đầy đủ |

---

## Mục 11 — Tài Liệu Đầu Ra & Phê Duyệt (Deliverables & Approval)

| Tài liệu | Skill sinh | Định dạng | Người tạo | Thời hạn | Nơi lưu |
|---|---|---|---|---|---|
| Master Test Plan | skill 02 (qa-core/02-test-plan) | `Test_Plan_{code}_{milestone}_v{ver}_{date}.md` | QC Lead | Trước ngày test | `testing-output/test-plan/` |
| Sprint Test Plan | skill 03 (qa-core/03-sprint-test-plan) | `Sprint_Test_Plan_{code}_{sprint}_v{ver}_{date}.md` | QC Lead | Đầu sprint | `testing-output/test-plan/` |
| High-Level Test Design | skill 04 (qa-core/04-test-design-high-level) | `hltc-{module}-{sprint}-v{ver}-{date}.md` | QC Lead | Ngày {N} sprint | `testing-output/test-cases/hltc/` |
| Test Case Functional | skill 05 (qa-core/05-gen-tc-functional) | `tc-functional-{module}-{sprint}-v{ver}-{date}.tsv` | QC | Ngày {N} sprint | `testing-output/test-cases/functional/` |
| Test Case SIT | skill 06 (qa-core/06-gen-tc-sit) | `tc-sit-{module}-{sprint}-v{ver}-{date}.tsv` | QC | Ngày {N} sprint | `testing-output/test-cases/sit/` |
| Test Data | skill 08 (qa-core/08-gen-data-test) | `master-dataset-{sprint}-v{ver}-{date}.tsv` | QC | Trước ngày test | `testing-output/test-data/` |
| Automation Script | skill qa-automation/02-gen-script-test | Robot Framework `.robot` | QC | Ngày {N} sprint | `testing-output/automation/` |
| Daily Test Report | skill 09 (qa-core/09-check-result) | `.md` + `.html` | QC | Mỗi ngày test | `testing-output/reports/daily/` |
| Sprint Summary Report | skill 10 (qa-core/10-test-report) | `.md` + `.html` | QC Lead | Ngày cuối sprint | `testing-output/reports/sprint/` |
| Bug Report | — | Jira ticket | QC | Trong ngày phát hiện | Jira project {X} |

**Phê duyệt tài liệu:**

| Vai trò | Tên | Ngày ký | Chữ ký / Xác nhận |
|---|---|---|---|
| QC Lead / Test Manager | {Tên} | | |
| Tech Lead / Dev Lead | {Tên} | | |
| Product Manager / BA | {Tên} | | |
| Project Manager | {Tên} | | |

> Tài liệu chỉ được triển khai khi có ít nhất QC Lead và PM ký duyệt.

> **Lưu ý bắt buộc:**
> - Sau khi có danh sách TC → chạy **skill 08 (qa-core/08-gen-data-test)** ngay để sinh test data
> - TC nào có thể automation → chạy **skill qa-automation/02-gen-script-test** để gen script
> - Mọi file output phải có `v{semver}` + `{yyyy-mm-dd}_{HHmm}` trong tên file
