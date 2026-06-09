# Detailed Procedure: 13-go-no-go

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## Kiem tra truoc khi bao DONE

> L3 - PM/PO/Tech Lead Approval BLOCKING (SLA: 4h). Sau khi gen report: DUNG. Khong publish Confluence, khong update Jira cho den khi nhan reply. Xem muc Approval cuoi file.

- [ ] Bao cao Go/No-Go du: so sanh exit criteria, risk, quyet dinh ro
- [ ] UAT sign-off da nhan truoc (prerequisite)
- [ ] Approval L3 da nhan: GO / NO-GO / GO voi dieu kien
- [ ] Append execution record vao governance/audit-log.md
- [ ] Cap nhat project/session-state.yaml -> last_execution, pending_sign_offs

---






## Bước 0 — Đọc qa-config.yaml (nếu có)

Nếu project đã có `qa-config.yaml` → đọc và dùng trực tiếp các giá trị sau, không hỏi lại:

| Field trong config | Dùng cho |
|---|---|
| `exit_criteria.*` | Gate 1 — ngưỡng pass_rate, health_score_baseline, max_s1_open, max_s2_open, tc_executed_rate |
| `uat.required`, `uat.stakeholders` | Gate 2 — xác định có áp dụng UAT gate không |
| `security.focus` | Gate 3 — danh sách OWASP category cần kiểm tra |
| `accessibility.required`, `accessibility.lighthouse_score_min` | Gate 3.5 — ngưỡng accessibility |
| `performance.*` | Gate 4 — ngưỡng p95, error rate |
| `environments.production.*` | Gate 5 — checklist deploy readiness |
| `team.qc_lead` | Người ký Go/No-Go report |

Nếu chưa có `qa-config.yaml` → đọc Exit Criteria từ Test Plan. Ghi rõ nguồn đang dùng ở đầu report.

## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| Test Report cuối sprint (hoặc kết quả test tổng hợp) | ✅ |
| `qa-config.yaml` (nguồn ưu tiên) **hoặc** Test Plan gốc (fallback) | ✅ một trong hai |
| Danh sách bug còn open (ID, severity, priority) | ✅ |
| Kết quả UAT sign-off (nếu `uat.required: true` trong config) | Theo config |
| Kết quả security test / performance test (nếu có) | Khuyến nghị |
| Ngày deploy dự kiến | ✅ |

Thiếu thông tin bắt buộc → ghi `[Cần bổ sung]`, hỏi lại. Không tự suy đoán kết quả.

## Bước 1 — Tổng hợp các Gate kiểm tra

Đánh giá lần lượt từng gate. Mỗi gate phải **rõ ràng Pass hoặc Fail** — không để "N/A" nếu không có lý do chính đáng.

### Gate 1 — Chất lượng kiểm thử

Đọc `../../references/report-template.md` và `../../references/bug-severity.md` để lấy ngưỡng chuẩn.

| Chỉ số | Exit Criteria | Thực tế | Kết quả |
|---|---|---|---|
| Pass rate | ≥ {x}% (từ Test Plan) | {x}% | ✅ / ❌ |
| Health Score | ≥ {N}/100 | {N}/100 | ✅ / ❌ |
| Bug S1 (Critical) còn open | = 0 | {N} | ✅ / ❌ |
| Bug S2 (High) còn open | ≤ {N} | {N} | ✅ / ❌ |
| TC chưa thực hiện (Not Run) | = 0 | {N} | ✅ / ❌ |
| Regression test pass rate | = 100% | {x}% | ✅ / ❌ |

### Gate 2 — UAT (nếu áp dụng)

| Chỉ số | Yêu cầu | Thực tế | Kết quả |
|---|---|---|---|
| UAT sign-off | Có sign-off từ stakeholder chính | ✅ / ❌ | ✅ / ❌ |
| Bug UAT S1 còn open | = 0 | {N} | ✅ / ❌ |
| % người dùng hoàn thành UAT | ≥ {N}% | {x}% | ✅ / ❌ |

### Gate 3 — Bảo mật (nếu có security test)

| Chỉ số | Yêu cầu | Thực tế | Kết quả |
|---|---|---|---|
| Lỗ hổng S1 (Critical) còn open | = 0 | {N} | ✅ / ❌ |
| Lỗ hổng S2 (High) còn open | = 0 (hoặc ≤ N có risk acceptance) | {N} | ✅ / ❌ |

### Gate 3.5 — Accessibility (nếu có accessibility test hoặc qa-config `accessibility.required: true`)

| Chỉ số | Yêu cầu | Thực tế | Kết quả |
|---|---|---|---|
| Lighthouse Accessibility Score | ≥ {N} (thường ≥ 80) | {N}/100 | ✅ / ❌ |
| Lỗi S1 accessibility (keyboard trap, nguy hiểm) | = 0 | {N} | ✅ / ❌ |
| Lỗi S2 accessibility (contrast, label, focus) | ≤ {N} hoặc có fix plan | {N} | ✅ / ❌ |

### Gate 4 — Hiệu năng (nếu có performance test)

| Chỉ số | Yêu cầu | Thực tế | Kết quả |
|---|---|---|---|
| P95 response time | ≤ SLA | {N}ms | ✅ / ❌ |
| Error rate dưới tải | < 1% | {x}% | ✅ / ❌ |

### Gate 5 — Sẵn sàng deploy

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Release notes đã soạn | ✅ / ❌ | |
| Rollback plan đã xác định | ✅ / ❌ | |
| Backup DB trước deploy | ✅ / ❌ | |
| Thông báo stakeholder / user | ✅ / ❌ | |
| Monitoring / alerting sẵn sàng | ✅ / ❌ | |
| Maintenance window đã thông báo (nếu cần) | ✅ / ❌ / N/A | |

## Bước 2 — Đánh giá bug còn open

Với mỗi bug còn open, đánh giá khả năng **accept risk** để deploy:

| Bug ID | Severity | Mô tả | Tác động nếu deploy | Quyết định |
|---|---|---|---|---|
| BUG-001 | S2 | {Mô tả} | {Tác động} | Fix trước / Accept risk / Defer |
| BUG-002 | S3 | {Mô tả} | {Tác động} | Fix trước / Accept risk / Defer |

**Nguyên tắc:**
- S1 còn open → **KHÔNG deploy** (không có ngoại lệ)
- S2 còn open → Deploy chỉ khi có **risk acceptance bằng văn bản** từ Product Owner / stakeholder có thẩm quyền
- S3/S4 còn open → Deploy được, ghi rõ vào Known Issues của release

## Bước 3 — Phân tích rủi ro deployment

| Rủi ro | Khả năng xảy ra | Tác động | Mitigation |
|---|---|---|---|
| {Rủi ro kỹ thuật — migration DB, breaking change API} | Cao / Trung bình / Thấp | {Mô tả} | {Hành động} |
| {Rủi ro nghiệp vụ — tính năng mới ảnh hưởng luồng cũ} | Cao / Trung bình / Thấp | {Mô tả} | {Hành động} |
| {Rủi ro môi trường — deploy giờ peak} | Cao / Trung bình / Thấp | {Mô tả} | {Hành động} |

## Bước 4 — Xác định rollback plan

Nếu deploy thất bại hoặc phát sinh S1 sau deploy:

| Bước | Hành động | Người thực hiện | Thời gian ước tính |
|---|---|---|---|
| 1 | Phát hiện vấn đề nghiêm trọng | QC / Dev On-call | Ngay lập tức |
| 2 | Thông báo kênh khẩn cấp | [Kênh Slack / Nhóm chat] | 5 phút |
| 3 | Quyết định rollback | [Người có thẩm quyền] | 10 phút |
| 4 | Thực hiện rollback | Dev / DevOps | [N] phút |
| 5 | Verify sau rollback | QC | [N] phút |
| 6 | Thông báo hoàn tất | PM / stakeholder | Ngay sau verify |

## Format output — Go/No-Go Report

```markdown




| Trường | Giá trị |
|---|---|
| **Ngày đánh giá** | [dd/mm/yyyy] |
| **Deploy dự kiến** | [dd/mm/yyyy HH:mm] |
| **Môi trường** | Production |
| **Người đánh giá** | [Tên QC Lead] |
| **Phê duyệt cuối** | [Tên PM / PO / Tech Lead] |

---

## Kết quả Gate

| Gate | Chỉ số quan trọng | Kết quả |
|---|---|---|
| Gate 1 — Chất lượng test | Pass rate [x]% / Health Score [N] / S1 open: [N] | ✅ Pass / ❌ Fail |
| Gate 2 — UAT | Sign-off: [N/N] người / S1 UAT open: [N] | ✅ Pass / ❌ Fail / ⬜ Skip |
| Gate 3 — Bảo mật | S1 sec open: [N] / S2 sec open: [N] | ✅ Pass / ❌ Fail / ⬜ Skip |
| Gate 3.5 — Accessibility | Lighthouse: [N]/100 / S1 a11y: [N] | ✅ Pass / ❌ Fail / ⬜ Skip |
| Gate 4 — Hiệu năng | P95: [N]ms / Error rate: [x]% | ✅ Pass / ❌ Fail / ⬜ Skip |
| Gate 5 — Sẵn sàng deploy | Rollback plan, monitoring, thông báo | ✅ Pass / ❌ Fail |

---

## Bug còn open khi deploy

| Bug ID | Severity | Mô tả | Quyết định | Người phê duyệt |
|---|---|---|---|---|
| BUG-XXX | S2 | [Mô tả] | Accept risk | [Tên PO] |

---

## Rủi ro và Mitigation

| Rủi ro | Khả năng | Tác động | Mitigation |
|---|---|---|---|
| [Rủi ro] | Thấp / TB / Cao | [Mô tả] | [Hành động] |

---

## Rollback Plan

- **Trigger:** [Điều kiện kích hoạt rollback — ví dụ: error rate > 5% trong 10 phút đầu]
- **Thời gian rollback:** [N] phút
- **Người quyết định:** [Tên + contact]
- **Cách rollback:** [Revert deploy / Restore DB backup / Feature flag off]

---

## QUYẾT ĐỊNH

> ### ✅ GO — Tiến hành deploy theo lịch
> **Lý do:** Tất cả gate pass. Không còn S1 open. Health Score [N]/100 đạt exit criteria.

> ### ⚠️ GO CÓ ĐIỀU KIỆN — Deploy được, theo dõi chặt sau deploy
> **Điều kiện:** [Bug S2 BUG-XXX được accept risk bởi [Tên PO]. Rollback ngay nếu error rate > [N]%.]

> ### ❌ NO-GO — Dừng, chưa đủ điều kiện deploy
> **Lý do:** [S1 BUG-XXX còn open / Pass rate [x]% thấp hơn exit criteria [y]% / Gate UAT chưa có sign-off]
> **Hành động tiếp theo:** [Fix BUG-XXX, retest, đánh giá lại ngày [dd/mm]]

---

*Báo cáo này là cơ sở chính thức cho quyết định deploy. Mọi thay đổi sau khi ký phê duyệt cần approval lại.*
```

**Lưu file vào:** `output_paths.reports.gate` từ qa-config (default: `testing-output/reports/gate/`)
→ `reports/go-no-go-{project.sprint}-{yyyy-mm-dd}_{HHmm}.md`

## Completion Status

- **DONE** — Go/No-Go report hoàn chỉnh, quyết định rõ ràng, đã có phê duyệt
- **DONE_WITH_CONCERNS** — Quyết định GO nhưng có rủi ro cần theo dõi sau deploy
- **BLOCKED** — Không thể đánh giá do: {Thiếu test report / Chưa có UAT sign-off / Chưa có kết quả security test}
- **NEEDS_CONTEXT** — Cần bổ sung: {Exit criteria từ Test Plan / Danh sách bug còn open / Kết quả test cuối}




---

## Bước cuối — Tool Integration + Approval + Audit Log (Level 3)

### 1. Approval Request (L3 — BLOCKING trước khi publish)

AI dừng hoàn toàn sau khi gen report. Không push lên Confluence, không update Jira cho đến khi có approval:

```
---
🔴 APPROVAL REQUIRED — 13-go-no-go (Level 3 — PM/PO/Tech Lead)
Người phê duyệt:
  - PM: [team.pm từ qa-config]
  - Product Owner: [team.product_owner từ qa-config]
  - Tech Lead: [team.dev_lead từ qa-config]
Deadline: [ngày hiện tại + 4h]
Output: testing-output/reports/gate/go-no-go-{sprint}-{date}.md
Hành động bắt buộc:
  - Đọc QUYẾT ĐỊNH section trong report
  - Reply "GO" / "NO-GO" / "GO với điều kiện: [...]"
Sau khi nhận reply → AI sẽ publish lên Confluence và update Jira.
---
```

### 2. Post-approval Tool Integration

Chỉ thực hiện SAU KHI nhận được approval reply:

**Publish Go/No-Go report lên Confluence:**
```bash
python tools/confluence_publish_markdown.py \
  --file "testing-output/reports/gate/go-no-go-{sprint}-{date}.md" \
  --parent-page "{confluence.parent_pages.team_root}/Release Gates"
```

**Update Jira sprint:**
```bash
python tools/jira_sync.py --action transition \
  --issue "{sprint_ticket_id}" \
  --status "Ready for Release" \
  --comment "Go/No-Go: [GO/NO-GO]. Report: [Confluence link]"
```

**Nếu NO-GO:**
```bash
python tools/jira_sync.py --action comment \
  --issue "{sprint_ticket_id}" \
  --comment "NO-GO: [Lý do]. Cần fix: [bug IDs]. Deploy tạm hoãn."
```

### 3. Audit Log

```yaml
execution_record:
  id: "{yyyy-mm-dd}-{HHmm}-13-gng"
  timestamp: "{yyyy-mm-ddTHH:mm}"
  skill: "13-go-no-go"
  project: "{project.name}"
  sprint: "{project.sprint}"
  executor: "{executor}"
  input_summary: "Go/No-Go {sprint}: Pass {N}%, Health {N}/100, S1 open {N}, Deploy {date}"
  output_paths:
    - "testing-output/reports/gate/go-no-go-{sprint}-{date}.md"
  status: "DONE | DONE_WITH_CONCERNS | BLOCKED"
  requires_human_review: true
  reviewer: null
  reviewed_at: null
  sign_off_status: "PENDING"
```