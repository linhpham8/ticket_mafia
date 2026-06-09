# Detailed Procedure: 14-smoke-production

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## Kiem tra truoc khi bao DONE

> L3 - On-call Confirmation BLOCKING (SLA: 30 phut). Sau khi smoke ket thuc: DUNG. Cho On-call reply STABLE / ROLLBACK / MONITOR. Xem muc Confirmation cuoi file.

- [ ] Smoke result ro rang: STABLE / MONITOR / ROLLBACK + ly do
- [ ] Moi CUJ da verify hoac co note ly do skip
- [ ] On-call confirmation da nhan
- [ ] Append execution record vao governance/audit-log.md
- [ ] Cap nhat project/session-state.yaml -> last_execution, sprint_progress

---







## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| URL production sau deploy | ✅ |
| Danh sách luồng nghiệp vụ cốt lõi cần verify (critical user journeys) | ✅ |
| Tài khoản test trên production (dedicated test account, không dùng account thật) | ✅ |
| Thông tin deploy: version/commit được deploy, thời gian deploy | ✅ |
| Rollback trigger conditions (ngưỡng kích hoạt rollback) | Khuyến nghị |
| Smoke test từ lần trước (để so sánh baseline) | Khuyến nghị |

> **Quan trọng:** Smoke test production phải **nhanh** (mục tiêu ≤ 15–30 phút) và chỉ cover luồng CRITICAL. Không test edge case, không test toàn bộ tính năng trên production.

Nếu project có `qa-config.yaml` → đọc trước (không hỏi lại các giá trị đã có trong config):
- `environments.production.url` → URL production
- `critical_user_journeys` → danh sách CUJ cần verify (dùng trực tiếp, không cần hỏi)
- `test_accounts` → tài khoản test trên production
- `performance.rollback_error_rate` → ngưỡng error rate trigger rollback
- `performance.api_p95_ms` → baseline P95 để so sánh sau deploy
- `tools.communication.escalation` → kênh escalate khi cần rollback

Thiếu thông tin bắt buộc → dừng, hỏi trước khi test.

---

## Bước 1 — Xác định Critical User Journeys (CUJ)

Chọn tối đa **5–10 luồng** quan trọng nhất — những gì mà nếu hỏng sẽ phải rollback ngay:

**Tiêu chí chọn CUJ:**
1. Luồng doanh thu trực tiếp (thanh toán, đặt hàng, ký hợp đồng)
2. Luồng mà người dùng dùng hàng ngày, thường xuyên nhất
3. Luồng mà deploy này có thay đổi trực tiếp
4. Luồng auth/login — nếu hỏng, không ai vào được

**Không đưa vào smoke test:**
- Tính năng admin nội bộ ít người dùng
- Edge case hiếm gặp
- Tính năng không liên quan đến sprint này

---

## Bước 2 — Thực hiện smoke test theo checklist

Chạy từng CUJ, ghi nhận kết quả ngay lập tức. **Nguyên tắc thực hiện:**

- Mỗi CUJ test trong **≤ 3 phút** — không debug, không tìm hiểu sâu
- Gặp fail → ghi nhận, tiếp tục test CUJ khác, đánh giá rollback sau
- Không tạo data thật (đơn hàng thật, thanh toán thật) trừ khi có dedicated test account

### Checklist smoke test chuẩn

**Luồng Auth (bắt buộc với mọi deploy):**
- [ ] Đăng nhập thành công với tài khoản test
- [ ] Đăng xuất thành công, không còn session
- [ ] Không thể truy cập trang protected sau logout

**Luồng Core Business (tùy ứng dụng):**
- [ ] [CUJ 1]: [Mô tả hành động + kết quả mong đợi]
- [ ] [CUJ 2]: [Mô tả hành động + kết quả mong đợi]
- [ ] [CUJ 3]: [Mô tả hành động + kết quả mong đợi]

**Kiểm tra kỹ thuật cơ bản:**
- [ ] Trang chủ load thành công (HTTP 200, không có lỗi console critical)
- [ ] Không có lỗi JavaScript critical trên console (F12 → Console)
- [ ] API health endpoint phản hồi OK (nếu có `/health` hoặc `/api/status`)
- [ ] Tính năng được deploy trong sprint này hoạt động đúng

---

## Bước 3 — Quan sát monitoring sau deploy

Trong khi smoke test, đồng thời kiểm tra:

| Chỉ số | Công cụ | Ngưỡng cảnh báo |
|---|---|---|
| Error rate (5xx) | Grafana / Datadog / CloudWatch | > 1% → cảnh báo, > 5% → rollback |
| Response time P95 | APM tool | Tăng > 50% so với trước deploy |
| CPU / Memory | Server monitoring | CPU > 90% liên tục 5 phút |
| Active users | Analytics | Drop bất thường ngay sau deploy |
| Số lượng exception | Sentry / logging | Tăng đột biến so với baseline |

**Thời gian quan sát:** Ít nhất 15 phút sau deploy trước khi kết luận "ổn định".

---

## Bước 4 — Quyết định Go / Rollback

### Rollback ngay (không cần chờ) nếu:
- Bất kỳ CUJ nào fail — đặc biệt là auth, thanh toán, luồng core
- Error rate 5xx > 5% trong 5 phút liên tiếp
- Response time P95 tăng > 100% và không giảm
- Data corruption phát hiện
- Nhiều user báo cáo không vào được hệ thống

### Theo dõi chặt (không rollback ngay) nếu:
- CUJ thứ yếu fail nhưng CUJ core ổn
- Error rate tăng nhẹ (1–5%), đang giảm dần
- Một tính năng mới có lỗi nhỏ nhưng không ảnh hưởng luồng cũ

### Ổn định nếu:
- Tất cả CUJ pass
- Error rate < 1%, không tăng
- Response time trong baseline
- Monitoring bình thường sau 15 phút

---

## Format output — Smoke Test Result

```markdown




| Trường | Giá trị |
|---|---|
| **Thời gian deploy** | [dd/mm/yyyy HH:mm] |
| **Version / Commit** | [v1.2.3 / abc1234] |
| **Thời gian smoke test** | [HH:mm] – [HH:mm] (tổng [N] phút) |
| **Tester** | [Tên] |
| **Môi trường** | Production — [URL] |

---

## Kết quả CUJ

| # | Critical User Journey | Kết quả | Thời gian | Ghi chú |
|---|---|---|---|---|
| 1 | Đăng nhập | ✅ Pass / ❌ Fail | [N]s | |
| 2 | [Luồng core 1] | ✅ Pass / ❌ Fail | [N]s | |
| 3 | [Luồng core 2] | ✅ Pass / ❌ Fail | [N]s | |

**Tổng:** [N] Pass / [N] Fail / [N] Skip

---

## Monitoring snapshot (15 phút sau deploy)

| Chỉ số | Trước deploy | Sau deploy | Trạng thái |
|---|---|---|---|
| Error rate (5xx) | [x]% | [x]% | ✅ / ⚠️ / ❌ |
| P95 response time | [N]ms | [N]ms | ✅ / ⚠️ / ❌ |
| CPU | [x]% | [x]% | ✅ / ⚠️ / ❌ |

---

## Vấn đề phát sinh

### [SMOKE-001: Tên vấn đề] — Nếu có

| Trường | Giá trị |
|---|---|
| **CUJ ảnh hưởng** | [Tên CUJ] |
| **Mô tả** | [Expected vs Actual] |
| **Screenshot** | [Link] |
| **Quyết định** | Rollback / Monitor / Accept |

---

## QUYẾT ĐỊNH CUỐI

> ### ✅ STABLE — Deploy thành công
> Tất cả [N] CUJ pass. Monitoring ổn định. Error rate [x]%. Deploy được xác nhận thành công.

> ### ⚠️ MONITOR — Tiếp tục theo dõi
> [N]/[N] CUJ pass. Có vấn đề nhỏ tại [tên CUJ] nhưng không ảnh hưởng core.
> **Hành động:** Theo dõi thêm [N] phút. Escalate nếu error rate > [x]%.

> ### ❌ ROLLBACK — Thực hiện rollback ngay
> **Lý do:** [CUJ X fail — luồng thanh toán không hoạt động / Error rate [x]% / ...]
> **Thực hiện:** [Tên người rollback] tiến hành rollback lúc [HH:mm].
> **Notify:** [Kênh thông báo — Slack #deploy-alerts / nhóm on-call]

---

*Thời gian kết thúc smoke test: [HH:mm] | Kết luận: [STABLE / MONITOR / ROLLBACK]*
```

---

## Checklist post-smoke (sau khi kết luận STABLE)

- [ ] Thông báo team: deploy thành công, smoke test passed
- [ ] Cập nhật release notes / changelog
- [ ] Close sprint / release ticket
- [ ] Log thời gian deploy và version vào deploy history
- [ ] Cleanup: xóa data test tạo ra trên production (nếu có)

---

## Completion Status

- **DONE** — Smoke test hoàn thành, quyết định rõ ràng (Stable / Monitor / Rollback)
- **DONE_WITH_CONCERNS** — Stable nhưng có điểm cần theo dõi tiếp: {Error rate nhỉnh hơn bình thường / CUJ thứ yếu chưa verify}
- **BLOCKED** — Không thể smoke test do: {Không có tài khoản test trên production / Môi trường đang down / Deploy chưa hoàn tất}
- **NEEDS_CONTEXT** — Cần bổ sung: {URL production / Danh sách CUJ / Tài khoản test production}




---

## Bước cuối — Sign-off (L3 — Ops) + Audit Log

### 1. Smoke result confirmation (L3 — SLA: 30 phút)

```
---
🔴 CONFIRMATION REQUIRED — 14-smoke-production (Level 3 — On-call)
Người xác nhận:
  - QC Lead: [team.qc_lead từ qa-config]
  - On-call Dev: [team.dev_lead từ qa-config]
Deadline: 30 phút sau khi smoke kết thúc
Output: testing-output/reports/gate/smoke-{sprint}-{date}.md
Hành động bắt buộc:
  - Reply "STABLE" / "ROLLBACK" / "MONITOR [N] phút"
Nếu ROLLBACK → thực hiện ngay, không cần chờ approval thêm.
---
```

**Trường hợp đặc biệt — ROLLBACK:** Không cần chờ approval. Notify ngay và ghi log với status=ROLLBACK.

### 2. Post-smoke Tool Integration

Sau khi nhận confirmation:

```bash
# Publish smoke result
python tools/confluence_publish_markdown.py \
  --file "testing-output/reports/gate/smoke-{sprint}-{date}.md" \
  --parent-page "{confluence.parent_pages.team_root}/Production Deployments"

# Nếu STABLE — update Jira
python tools/jira_sync.py --action transition \
  --issue "{sprint_ticket_id}" \
  --status "Done" \
  --comment "Smoke STABLE: {N}/{N} CUJ pass. Deploy confirmed {date} {time}."

# Nếu ROLLBACK — update Jira urgent
python tools/jira_sync.py --action comment \
  --issue "{sprint_ticket_id}" \
  --comment "ROLLBACK triggered: [lý do]. Notify @oncall-dev."
```

### 3. Audit Log

```yaml
execution_record:
  id: "{yyyy-mm-dd}-{HHmm}-14-smoke"
  timestamp: "{yyyy-mm-ddTHH:mm}"
  skill: "14-smoke-production"
  project: "{project.name}"
  sprint: "{project.sprint}"
  executor: "{executor}"
  input_summary: "Smoke production {version}: {N}/{N} CUJ, decision: STABLE/MONITOR/ROLLBACK"
  output_paths:
    - "testing-output/reports/gate/smoke-{sprint}-{date}.md"
  status: "DONE | DONE_WITH_CONCERNS | BLOCKED"
  requires_human_review: true
  reviewer: null
  reviewed_at: null
  sign_off_status: "PENDING | APPROVED (STABLE) | APPROVED (ROLLBACK)"
```