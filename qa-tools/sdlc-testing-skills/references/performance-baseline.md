# Performance Baseline & Testing Guide

> Skill 11 đọc file này để xác định ngưỡng baseline và cách thực hiện performance testing.
> Baseline mặc định áp dụng khi dự án không có SLA riêng.
> Luôn ưu tiên SLA trong qa-config.yaml nếu có.

---

## Ngưỡng Baseline Mặc Định

### Response Time (API)

| Loại API | P50 (median) | P95 | P99 | Max chấp nhận |
|---|---|---|---|---|
| API CRUD đơn giản (GET/POST) | ≤ 200ms | ≤ 500ms | ≤ 1000ms | 2000ms |
| API có business logic (tính toán, workflow) | ≤ 500ms | ≤ 1000ms | ≤ 2000ms | 5000ms |
| API tích hợp bên thứ ba (payment, SMS) | ≤ 1000ms | ≤ 3000ms | ≤ 5000ms | 10000ms |
| API export / report (xử lý nhiều data) | ≤ 2000ms | ≤ 5000ms | ≤ 10000ms | 30000ms |
| API upload file | ≤ 3000ms | ≤ 8000ms | ≤ 15000ms | 30000ms |

### Page Load Time (Web)

| Loại trang | FCP (First Contentful Paint) | LCP (Largest Contentful Paint) | TTI (Time to Interactive) |
|---|---|---|---|
| Landing page / Marketing | ≤ 1.5s | ≤ 2.5s | ≤ 3s |
| Dashboard / App trang chính | ≤ 2s | ≤ 3s | ≤ 4s |
| Trang danh sách dữ liệu lớn | ≤ 2s | ≤ 4s | ≤ 5s |
| Trang báo cáo / biểu đồ | ≤ 3s | ≤ 5s | ≤ 6s |

> Nguồn: Google Core Web Vitals thresholds (Good: ≤ 2.5s LCP, Poor: > 4s)

### Throughput & Concurrent Users

| Quy mô hệ thống | Concurrent Users (bình thường) | Concurrent Users (peak) | Requests/giây |
|---|---|---|---|
| Small (startup, nội bộ) | 10–50 | 100 | 50–200 rps |
| Medium (SME, vài nghìn user) | 100–500 | 1000 | 200–1000 rps |
| Large (enterprise, public) | 1000–5000 | 10000 | 1000+ rps |

---

## Chỉ Số Cần Đo

| Chỉ số | Mô tả | Ngưỡng cảnh báo |
|---|---|---|
| **Response time P95** | 95% request hoàn thành trong thời gian này | > Baseline P95 × 1.5 |
| **Error rate** | % request thất bại (5xx, timeout) | > 1% |
| **Throughput (rps)** | Số request xử lý được mỗi giây | Giảm > 20% so với baseline |
| **CPU usage** | Mức sử dụng CPU trung bình | > 80% liên tục |
| **Memory usage** | RAM sử dụng, có leak không | Tăng liên tục không giảm |
| **Database connections** | Số connection mở đồng thời | > Connection pool limit × 0.8 |
| **Cache hit rate** | % request được phục vụ từ cache | < 70% (nếu có cache) |

---

## Loại Performance Test

### 1. Load Test — Kiểm tra hệ thống dưới tải bình thường

**Mục đích:** Xác nhận hệ thống hoạt động đúng ở tải dự kiến hàng ngày.

**Cấu hình chuẩn:**
- Users: concurrent users bình thường (xem bảng quy mô ở trên)
- Duration: 10–30 phút
- Ramp-up: tăng dần trong 2–5 phút đầu
- Pattern: constant load

**Pass khi:** P95 ≤ baseline, error rate < 1%, không có memory leak.

---

### 2. Stress Test — Kiểm tra giới hạn hệ thống

**Mục đích:** Tìm điểm gãy — hệ thống bắt đầu degradation ở ngưỡng nào.

**Cấu hình chuẩn:**
- Users: tăng dần từ 0 lên 2–5× concurrent users bình thường
- Duration: 20–60 phút
- Ramp-up: tăng từng bước (25% → 50% → 75% → 100% → 150% → 200%)
- Quan sát: điểm P95 bắt đầu vượt baseline, error rate bắt đầu tăng

**Báo cáo:** Ghi nhận breaking point — số concurrent users và rps tại đó hệ thống bắt đầu fail.

---

### 3. Spike Test — Kiểm tra phản ứng với tải đột biến

**Mục đích:** Mô phỏng flash sale, sự kiện, traffic đột biến.

**Cấu hình chuẩn:**
- Phase 1: tải thấp (10–20% concurrent users bình thường) — 5 phút
- Phase 2: đột biến lên 500–1000% — 1–2 phút
- Phase 3: về tải thấp lại — 5 phút
- Quan sát: hệ thống có recover không? Auto-scale hoạt động không?

---

### 4. Soak Test (Endurance) — Kiểm tra độ bền dài hạn

**Mục đích:** Phát hiện memory leak, connection leak, degradation theo thời gian.

**Cấu hình chuẩn:**
- Users: 50–80% concurrent users bình thường
- Duration: 2–8 giờ (hoặc qua đêm)
- Quan sát: response time có tăng dần theo thời gian không? Memory có tăng liên tục không?

---

## Công Cụ Khuyến Nghị

| Công cụ | Use case | Ghi chú |
|---|---|---|
| **JMeter** | Load test, Stress test, API test — GUI + script | Ưu tiên — đầy đủ tính năng, team đã quen |
| **Artillery** | API + WebSocket test | Ưu tiên cho real-time app |
| **Locust** | Load test bằng Python | Dùng khi team quen Python |
| **Lighthouse** | Web performance (FCP, LCP, TTI) | Tích hợp Chrome DevTools |
| **WebPageTest** | Real browser performance đa địa điểm | Dùng cho frontend audit |
| **BlazeMeter** | Distributed load test từ nhiều region | Trả phí, tích hợp JMeter script |

---

## Cấu Trúc JMeter Test Plan Chuẩn

### Cấu trúc Test Plan
```
Test Plan
├── Thread Group (Load Test)
│   ├── HTTP Request Defaults (base URL, headers)
│   ├── HTTP Header Manager (Authorization, Content-Type)
│   ├── HTTP Cookie Manager
│   ├── [Sampler] HTTP Request — endpoint cần test
│   ├── [Assertion] Response Assertion (status code)
│   ├── [Assertion] Duration Assertion (≤ P95 target)
│   └── [Timer] Constant Timer — think time giữa requests
├── Listeners
│   ├── Summary Report
│   ├── Response Times Over Time
│   └── Active Threads Over Time
└── Test Fragments (reusable: login, setup, teardown)
```

### Cấu hình Thread Group chuẩn — Load Test

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| Number of Threads | `${CONCURRENT_USERS}` | Dùng JMeter property |
| Ramp-Up Period | 120 (giây) | Tăng dần trong 2 phút |
| Loop Count | Forever | Kết hợp với Scheduler |
| Duration (Scheduler) | 600 (giây) | Chạy 10 phút |
| Startup delay | 0 | |

### Thresholds kiểm tra

Dùng **Backend Listener** gửi metrics vào InfluxDB/Grafana hoặc đọc từ Summary Report:

| Chỉ số trong JMeter | Tên hiển thị | Ngưỡng Pass |
|---|---|---|
| Average | Average response time | ≤ Baseline P50 |
| 90th Percentile | P90 | ≤ Baseline P95 × 0.9 |
| 95th Percentile | P95 | ≤ Baseline P95 |
| 99th Percentile | P99 | ≤ Baseline P99 |
| Error % | Error rate | < 1% |
| Throughput | Requests/sec | ≥ Target rps |

### Chạy JMeter non-GUI (CI-friendly)

```bash
jmeter -n -t test-plan.jmx \
  -l results.jtl \
  -e -o html-report/ \
  -JCONCURRENT_USERS=50 \
  -JDURATION=600 \
  -JBASE_URL=https://staging.example.com
```

---

## Format Báo Cáo Performance

Khi kết thúc performance test, báo cáo phải bao gồm:

| Chỉ số | Baseline | Kết quả | Pass? |
|---|---|---|---|
| P50 response time | {N}ms | {N}ms | ✅ / ❌ |
| P95 response time | ≤ {N}ms | {N}ms | ✅ / ❌ |
| P99 response time | ≤ {N}ms | {N}ms | ✅ / ❌ |
| Error rate | < 1% | {x}% | ✅ / ❌ |
| Throughput | ≥ {N} rps | {N} rps | ✅ / ❌ |
| Max concurrent users đạt được | — | {N} | — |
| Breaking point (nếu stress test) | — | {N} users / {N} rps | — |

**Kết luận:** ✅ Đạt SLA / ⚠️ Cần tối ưu ({điểm cụ thể}) / ❌ Không đạt SLA

**Bottleneck phát hiện:** {Database N+1 query / Missing index / Memory leak tại X / Thiếu caching}

**Khuyến nghị:** {Cụ thể — không chung chung}
