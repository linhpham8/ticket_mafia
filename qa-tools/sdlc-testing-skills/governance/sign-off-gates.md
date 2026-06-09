# Sign-Off Gates — QA Skill Suite

Định nghĩa gate phê duyệt của con người cho từng skill. AI **không được** tự đánh dấu Completion Status là `DONE` cho các skill Level 2/3 mà không có xác nhận rõ ràng từ người dùng.

---

## Bảng gate theo skill

| Skill | Level | Người phê duyệt | SLA | Điều kiện DONE |
|---|---|---|---|---|
| 01-review-requirements | L1 — Auto | Không cần | — | AI tự hoàn thành |
| 02-test-plan | L1 — Auto | Không cần | — | AI tự hoàn thành |
| 03-sprint-test-plan | L1 — Auto | Không cần | — | AI tự hoàn thành |
| 04-test-design-high-level | L1 — Auto | Không cần | — | AI tự hoàn thành (gate HLTC là nội bộ) |
| 05-gen-tc-functional | L1 — Auto | Không cần | — | AI tự hoàn thành |
| 06-gen-tc-sit | L1 — Auto | Không cần | — | AI tự hoàn thành |
| 07-review-tc | L2 — QA Review | QA Lead | 24h | QA Lead xác nhận coverage đủ |
| 08-gen-data-test | L1 — Auto | Không cần | — | AI tự hoàn thành |
| 09-check-result | L2 — QA Review | QA Lead | 4h | QA Lead xem và confirm daily report |
| 10-test-report | L2 — QA Review | QA Lead | 8h | QA Lead review và ký sprint report |
| 11-demo-preparation | L1 — Auto | Không cần | — | AI tự hoàn thành |
| 12-uat-support | **L3 — Stakeholder** | Product Owner + Business Rep | 48h | Stakeholder sign UAT sign-off form |
| 13-go-no-go | **L3 — Stakeholder** | PM / PO / Tech Lead | 4h | Decision được ký bởi người có thẩm quyền |
| 14-smoke-production | **L3 — Ops** | QC Lead + On-call Dev | 30min | Xác nhận STABLE/ROLLBACK trong 30 phút |
| qa-automation/01 | L1 — Auto | Không cần | — | AI tự hoàn thành |
| qa-automation/02 | L2 — Dev Review | QC Lead + Dev | 24h | Code review + run thử không bị lỗi |
| qa-specialist/01-03 | L2 — QA Review | QA Lead | 24h | QA Lead review report |

---

## Định nghĩa Level

### Level 1 — Auto-complete
AI hoàn thành output, tự đánh dấu DONE. Không cần approval.
Áp dụng: skills thiết kế và chuẩn bị (01-08 ngoại trừ 07).

### Level 2 — QA Review Required
AI hoàn thành output và emit **sign-off request**. DONE chỉ sau khi QA Lead/reviewer xác nhận.
AI không được tự chuyển sang skill tiếp theo mà chưa có xác nhận.

**Sign-off request format (AI emit khi kết thúc skill L2):**
```
---
⏳ SIGN-OFF REQUEST — [Skill Name]
Người cần review: [QA Lead name từ qa-config]
SLA: [N] giờ
Output đã lưu tại: [path]
Hành động cần thiết: Xem output → reply "Approved" hoặc "Cần chỉnh sửa: [nội dung]"
---
```

### Level 3 — Stakeholder Approval Required
AI hoàn thành output và **dừng hoàn toàn**. Không proceed bất kỳ action nào (kể cả push lên Confluence, cập nhật Jira) cho đến khi có approval.

**Approval request format (AI emit khi kết thúc skill L3):**
```
---
🔴 APPROVAL REQUIRED — [Skill Name] — BLOCKING
Người phê duyệt: [Tên + vai trò]
Deadline: [yyyy-mm-dd HH:mm]
Output đã lưu tại: [path]
Hành động bắt buộc: Đọc output → xác nhận "GO" / "NO-GO" / "Cần chỉnh sửa"
Không có hành động nào tiếp theo cho đến khi nhận được phản hồi.
---
```

---

## Escalation khi quá SLA

| Tình huống | Hành động |
|---|---|
| L2 review quá 24h không nhận được | AI nhắc nhở người dùng, không tự proceed |
| L3 approval quá deadline | AI escalate lên PM/sponsor, ghi vào audit log |
| Người phê duyệt không available | Theo chuỗi escalation trong `qa-config.yaml > team` |

---

## Audit log integration

Sau mỗi sign-off/approval:
- AI cập nhật `governance/audit-log.md`:
  - `sign_off_status`: `APPROVED` hoặc `REJECTED`
  - `reviewer`: tên người phê duyệt
  - `reviewed_at`: ngày phê duyệt
