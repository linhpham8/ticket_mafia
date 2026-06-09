# Detailed Procedure: 02-performance-testing

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## Kiem tra truoc khi bao DONE

> **L2 - QA Lead review bat buoc.** Report chua duoc gui stakeholder cho den khi nhan Approved. Xem muc Sign-off cuoi file.

- [ ] Du loai test: load, stress, spike (hoac scope da xac nhan)
- [ ] Ket qua so sanh baseline ro rang (P95, error rate)
- [ ] Bottleneck da phan tich va co action items
- [ ] Sign-off L2 da emit
- [ ] Append execution record vao governance/audit-log.md
- [ ] Cap nhat project/session-state.yaml -> last_execution, pending_sign_offs

---







## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| URL môi trường test (staging — cấu hình tương đương production) | ✅ |
| Danh sách API / luồng cần đo | ✅ |
| Loại test cần thực hiện (load / stress / spike / soak) | ✅ |
| SLA hoặc ngưỡng performance mong đợi (nếu có) | Khuyến nghị |
| Quy mô hệ thống (số user thực tế, peak time) | Khuyến nghị |
| Công cụ đã dùng trong project (từ `tools.automation.performance` trong qa-config) | Khuyến nghị |

Thiếu thông tin bắt buộc → ghi `[Cần bổ sung]`, hỏi lại.
Nếu không có SLA → dùng baseline mặc định trong `../../references/performance-baseline.md`.

Nếu project có `qa-config.yaml` → đọc trước, không hỏi lại:
- `performance.*` → ngưỡng SLA: `concurrent_users_normal/peak`, `api_p95_ms`, `api_error_rate_threshold`, `rollback_error_rate`
- `tools.automation.performance` → công cụ thực thi (jmeter/artillery/locust/k6)
- `environments.staging.url` → URL môi trường test mặc định
- `environments.staging.auth_required` → có cần setup auth không

Nếu chưa có `qa-config.yaml` → dùng baseline mặc định từ `../../references/performance-baseline.md`; hỏi user nếu cần SLA cụ thể.

---

## Bước 1 — Xác định baseline và mục tiêu

Đọc `../../references/performance-baseline.md` để lấy ngưỡng mặc định.

Dùng giá trị đã đọc từ `qa-config.yaml` (ở trên) nếu có; ngược lại dùng baseline mặc định.

Ghi nhận baseline áp dụng:

| API / Endpoint | Loại | P50 target | P95 target | Error rate | Concurrent users |
|---|---|---|---|---|---|
| `GET /api/...` | CRUD đơn giản | ≤ 200ms | ≤ 500ms | < 1% | [N] |
| `POST /api/...` | Business logic | ≤ 500ms | ≤ 1000ms | < 1% | [N] |

---

## Bước 2 — Chọn loại test và cấu hình

Đọc `../../references/performance-baseline.md` phần "Loại Performance Test" để lấy cấu hình chi tiết.

**Công cụ thực thi:** ưu tiên `tools.automation.performance` từ `qa-config.yaml` nếu đã có; nếu không có thì mặc định dùng **JMeter**.

Tool hiện hỗ trợ tốt nhất trong skill này:
- **JMeter** — mặc định, dùng template và baseline trong `../../references/performance-baseline.md`
- **Artillery / Locust** — chỉ dùng khi project đã chốt tool này trong config hoặc user yêu cầu rõ

### Chọn loại test theo mục tiêu

| Mục tiêu | Loại test |
|---|---|
| Xác nhận hoạt động ổn ở tải hàng ngày | Load Test |
| Tìm giới hạn / breaking point | Stress Test |
| Kiểm tra flash sale, traffic đột biến | Spike Test |
| Phát hiện memory leak, degradation dài hạn | Soak Test |

### Cấu hình JMeter chuẩn

Nếu tool thực thi là **JMeter** thì áp dụng cấu hình chuẩn bên dưới. Nếu project dùng **Artillery** hoặc **Locust**, giữ nguyên mục tiêu tải/SLA tương đương và chuyển đổi sang cấu hình của tool đó.

Đọc `../../references/performance-baseline.md` phần "Cấu Trúc JMeter Test Plan Chuẩn" để lấy template.

**Cấu hình Thread Group theo loại test:**

**Load Test:**
- Number of Threads (users): `CONCURRENT_USERS`
- Ramp-Up Period: 120 giây (2 phút)
- Loop Count: Forever + Scheduler Duration: 600 giây (10 phút)

**Stress Test:**
- Dùng Ultimate Thread Group hoặc nhiều Thread Group tăng dần:
  - Group 1: 50% users — 5 phút
  - Group 2: 100% users — 5 phút
  - Group 3: 150% users — 5 phút
  - Group 4: 200% users — 5 phút

**Spike Test:**
- Thread Group 1 (baseline thấp): 10% users — 5 phút
- Thread Group 2 (spike): 1000% users — 1 phút
- Thread Group 3 (recover): 10% users — 5 phút

**Soak Test:**
- Number of Threads: 70% concurrent users bình thường
- Duration: 4 giờ (hoặc qua đêm)
- Ghi log metrics mỗi 30 phút để phát hiện drift

---

## Bước 3 — Thiết lập Assertions / Threshold theo tool

Nếu dùng **JMeter** thì cấu hình theo phần dưới đây. Nếu dùng tool khác, áp cùng threshold response time, error rate và throughput tương đương.

Áp dụng ngưỡng từ Bước 1 vào JMeter:

| Assertion | Cấu hình |
|---|---|
| Response Assertion | Response Code = 200 (hoặc code mong đợi) |
| Duration Assertion | Response Time ≤ Baseline P95 |
| Summary Report | Theo dõi: Average, P90, P95, P99, Error% |

**Listeners cần thiết:**
- Summary Report (tổng hợp cuối)
- Response Times Over Time (xem trend)
- Active Threads Over Time (xem ramp-up)
- Backend Listener → InfluxDB/Grafana (nếu có setup monitoring)

---

## Bước 4 — Chạy test và thu thập kết quả

Các chỉ số cần thu thập (xem đầy đủ trong `../../references/performance-baseline.md`):

| Chỉ số | Nguồn thu thập |
|---|---|
| P50, P95, P99 response time | JMeter Summary Report (cột Average, 90th%ile, 95th%ile, 99th%ile) |
| Error rate | JMeter Summary Report — cột Error% |
| Throughput (rps) | JMeter Summary Report — cột Throughput |
| CPU usage | Server monitoring (CloudWatch, Grafana, htop) |
| Memory usage | Server monitoring — quan sát có tăng liên tục không |
| DB connections | DB dashboard hoặc `SHOW PROCESSLIST` |

**Với Soak Test:** chụp snapshot metrics mỗi 30 phút để phát hiện drift.

---

## Bước 5 — Phân tích kết quả và bottleneck

So sánh kết quả với baseline. Nếu vượt ngưỡng, phân tích nguyên nhân:

| Triệu chứng | Nguyên nhân phổ biến | Hướng điều tra |
|---|---|---|
| P95 cao, CPU thấp | N+1 query, missing index | Bật slow query log, EXPLAIN query |
| P95 cao, CPU cao | Thiếu caching, tính toán nặng | Profile code, thêm Redis cache |
| Memory tăng liên tục | Memory leak | Heap dump, profiler |
| Error rate tăng khi load cao | Connection pool cạn | Tăng pool size, kiểm tra timeout |
| Throughput giảm khi scale | Bottleneck tại shared resource | Kiểm tra DB lock, message queue |

---

## Format output — Performance Test Report

```markdown




| Trường | Giá trị |
|---|---|
| **Ngày test** | [dd/mm/yyyy] |
| **Môi trường** | [URL staging] |
| **Loại test** | Load / Stress / Spike / Soak |
| **Công cụ** | [Tool thực thi: JMeter / Artillery / Locust] |
| **Thời lượng** | [X phút / giờ] |

---

## Kết quả tổng hợp

| Chỉ số | Baseline | Kết quả | Pass? |
|---|---|---|---|
| P50 response time | ≤ [N]ms | [N]ms | ✅ / ❌ |
| P95 response time | ≤ [N]ms | [N]ms | ✅ / ❌ |
| P99 response time | ≤ [N]ms | [N]ms | ✅ / ❌ |
| Error rate | < 1% | [x]% | ✅ / ❌ |
| Throughput | ≥ [N] rps | [N] rps | ✅ / ❌ |
| Max concurrent users | — | [N] | — |
| Breaking point (stress) | — | [N] users / [N] rps | — |

---

## Kết quả theo endpoint

| Endpoint | P50 | P95 | P99 | Error rate | Pass? |
|---|---|---|---|---|---|
| `GET /api/...` | [N]ms | [N]ms | [N]ms | [x]% | ✅ / ❌ |

---

## Server metrics

| Thời điểm | CPU | Memory | DB connections |
|---|---|---|---|
| Baseline (no load) | [x]% | [N]MB | [N] |
| Peak load | [x]% | [N]MB | [N] |
| After test | [x]% | [N]MB | [N] |

---

## Bottleneck phát hiện

[Mô tả cụ thể: N+1 query tại endpoint X / Memory tăng từ 512MB → 1.8GB / Connection pool timeout]

## Khuyến nghị

1. [Hành động cụ thể — thêm index vào bảng orders.created_at]
2. [Hành động cụ thể — cache kết quả endpoint /api/report với TTL 5 phút]
3. [Hành động cụ thể]

---

## Kết luận

✅ Đạt SLA / ⚠️ Cần tối ưu trước release / ❌ Không đạt SLA — không đủ điều kiện release

**Lý do:** [1-2 câu tóm tắt]
```

---

**Lưu file vào:** `output_paths.reports.performance` từ qa-config (default: `testing-output/reports/performance/`)
→ `reports/performance-report-{project.sprint}.md`

## Sign-off Request (L2)



Sau khi nhan Approved: cap nhat project/session-state.yaml, xoa item khoi pending_sign_offs.

---

## Completion Status

- **DONE** — Test hoàn thành, report đầy đủ, kết quả so sánh baseline rõ ràng
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng: {P95 vượt baseline tại endpoint X / Memory leak nghi ngờ / Cần soak test dài hơn}
- **BLOCKED** — Không thể test do: {Môi trường staging không representative / Không có monitoring server / Script lỗi}
- **NEEDS_CONTEXT** — Cần bổ sung: {SLA cụ thể / URL endpoint cần test / Quy mô concurrent users mong đợi}


