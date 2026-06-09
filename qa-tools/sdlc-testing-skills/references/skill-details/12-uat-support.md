# Detailed Procedure: 12-uat-support

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## Kiem tra truoc khi bao DONE

> L3 - Stakeholder Approval BLOCKING (SLA: 48h). Sau khi gen UAT Summary: DUNG. Khong gui cho user cho den khi PO/Business sign off. Xem muc Approval cuoi file.

- [ ] UAT Guide + Feedback Summary + Sign-off Tracker day du
- [ ] Moi bug phat sinh UAT da phan loai (blocking/non-blocking)
- [ ] Approval L3 da nhan: ghi ten nguoi approve va ngay
- [ ] Append execution record vao governance/audit-log.md
- [ ] Cap nhat project/session-state.yaml -> last_execution, pending_sign_offs

---







## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| Danh sách user story / tính năng cần UAT | ✅ |
| Danh sách người dùng tham gia UAT (tên, role, phòng ban) | ✅ |
| Môi trường UAT (URL, tài khoản) | ✅ |
| Thời gian UAT (ngày bắt đầu – kết thúc) | ✅ |
| Acceptance criteria từ ticket / Test Plan | Khuyến nghị |
| Template feedback đang dùng (nếu có) | Khuyến nghị |

Nếu project có `qa-config.yaml` → đọc trước:
- `uat.required` → xác nhận UAT có bắt buộc không
- `uat.stakeholders` → danh sách người tham gia và sign-off
- `environments.uat.url` → URL môi trường UAT
- `test_accounts` → tài khoản test cho người dùng UAT
- `tools.communication.channel` → kênh nhận feedback

Thiếu thông tin bắt buộc → ghi `[Cần bổ sung]`, hỏi lại.

---

## Bước 1 — Chuẩn bị tài liệu hướng dẫn UAT

Tạo tài liệu cho **end user** — không phải tester kỹ thuật. Ngôn ngữ phải:
- Đơn giản, không dùng thuật ngữ kỹ thuật (không viết "test case", "regression", "API")
- Mô tả hành động theo góc nhìn người dùng ("Bạn vào trang X, bấm nút Y...")
- Có hình ảnh / video hướng dẫn nếu tính năng phức tạp

Cấu trúc tài liệu hướng dẫn:

### 1.1 Thông tin chung
- Mục đích UAT: "Chúng tôi cần bạn thử các tính năng mới và xác nhận chúng hoạt động đúng với nghiệp vụ của bạn."
- Thời gian: [ngày bắt đầu – kết thúc]
- Cách phản hồi: [link form / email / Slack channel]
- Người liên hệ khi cần hỗ trợ: [tên, contact]

### 1.2 Kịch bản kiểm tra (Scenario)

Với mỗi tính năng, viết scenario theo format:

```
Kịch bản [N]: [Tên kịch bản — viết theo nghiệp vụ]

Bối cảnh: [Mô tả tình huống người dùng đang gặp]

Bạn cần làm:
  1. Truy cập [URL cụ thể]
  2. [Hành động cụ thể]
  3. [Hành động tiếp theo]

Kết quả mong đợi: [Điều bạn nên thấy sau khi hoàn thành]

Câu hỏi phản hồi:
  - Kịch bản này có hoạt động như bạn mong đợi không? (Có / Không / Một phần)
  - Nếu Không hoặc Một phần: Mô tả điều chưa đúng?
  - Tính năng này có giúp ích cho công việc hàng ngày của bạn không?
```

### 1.3 Cách ghi nhận vấn đề

Hướng dẫn người dùng báo cáo vấn đề:
- Chụp màn hình khi gặp lỗi
- Ghi rõ: đang làm gì, thấy gì, mong đợi gì
- Ghi rõ: tên trình duyệt, thiết bị (nếu liên quan)

---

## Bước 2 — Theo dõi tiến độ UAT

Tạo tracking sheet cho mỗi người tham gia:

| Người dùng | Phòng ban | Kịch bản 1 | Kịch bản 2 | Kịch bản 3 | Sign-off |
|---|---|---|---|---|---|
| [Tên] | [Phòng] | ✅ Pass / ❌ Fail / ⏳ Chưa thử | ... | ... | ⏳ Pending |

**Escalate khi:** người dùng chưa feedback sau 2 ngày → nhắc nhở chủ động.

---

## Bước 3 — Tổng hợp và phân loại feedback

Khi nhận feedback từ người dùng, phân loại theo:

### Loại 1 — Bug thực sự (cần fix trước go-live)
- Tính năng không hoạt động đúng acceptance criteria
- Lỗi chặn luồng nghiệp vụ quan trọng
- **Action:** Chuyển sang QA team, tạo bug ticket với severity

### Loại 2 — Yêu cầu thay đổi (Change Request)
- Tính năng hoạt động đúng spec nhưng người dùng muốn khác
- Ví dụ: "Tôi muốn cột này hiển thị trước cột kia"
- **Action:** Log vào backlog, KHÔNG fix trong sprint này. Ghi nhận để Product review.

### Loại 3 — Hiểu nhầm / Cần hướng dẫn thêm
- Người dùng báo "lỗi" nhưng thực ra là do chưa biết cách dùng
- **Action:** Hướng dẫn lại, cập nhật tài liệu hướng dẫn nếu cần

### Loại 4 — Enhancement / Nice-to-have
- Góp ý cải thiện không bắt buộc
- **Action:** Log vào backlog với nhãn "Enhancement"

---

## Bước 4 — Quản lý Sign-off

UAT chỉ kết thúc khi có sign-off rõ ràng từ người có thẩm quyền.

**Điều kiện sign-off:**
- [ ] Tất cả kịch bản bắt buộc đã được thử bởi ít nhất [N]% người dùng
- [ ] Không còn bug Loại 1 nào open
- [ ] Các Change Request đã được Product Owner xem xét và phân loại
- [ ] Người dùng key stakeholder đã ký xác nhận

**Form sign-off tối thiểu:**

```
Tôi, [Tên], [Chức vụ], xác nhận đã tham gia UAT cho [Tên tính năng / Sprint]
từ ngày [dd/mm] đến ngày [dd/mm/yyyy].

Kết quả: ✅ Chấp thuận / ❌ Chưa chấp thuận (lý do: ...)

Điều kiện deploy (nếu chưa chấp thuận hoàn toàn): [...]

Ký: _______________ Ngày: _______________
```

---

## Format output — UAT Feedback Summary

```markdown




| Trường | Giá trị |
|---|---|
| **Thời gian UAT** | [dd/mm] – [dd/mm/yyyy] |
| **Người tham gia** | [N] người / [N] phòng ban |
| **Kịch bản** | [N] kịch bản |
| **Tổng feedback nhận** | [N] |

---

## Kết quả theo kịch bản

| Kịch bản | Pass | Fail | Một phần | Chưa thử |
|---|---:|---:|---:|---:|
| Kịch bản 1: [Tên] | [N] | [N] | [N] | [N] |

---

## Phân loại feedback

| Loại | Số lượng | Ghi chú |
|---|---:|---|
| Bug thực sự (cần fix) | [N] | [Ticket IDs] |
| Change Request | [N] | [Chuyển backlog] |
| Hiểu nhầm / cần hướng dẫn | [N] | |
| Enhancement | [N] | |

---

## Bug phát sinh từ UAT

| Bug ID | Mô tả | Người báo | Severity | Trạng thái |
|---|---|---|---|---|
| BUG-UAT-001 | [Mô tả] | [Tên] | S1/S2/S3 | Open / Fixed |

---

## Sign-off Status

| Người dùng | Phòng ban | Trạng thái | Ghi chú |
|---|---|---|---|
| [Tên] | [Phòng] | ✅ Signed / ❌ Rejected / ⏳ Pending | [Điều kiện nếu có] |

**Kết luận:**
- ✅ UAT đạt — Có thể tiến hành go-live
- ⚠️ UAT đạt có điều kiện — Cần fix [N] bug trước go-live, [N] CR đưa vào sprint sau
- ❌ UAT chưa đạt — [Lý do cụ thể]
```

---

## Completion Status

- **DONE** — Tài liệu UAT đầy đủ, feedback đã tổng hợp, sign-off đã nhận
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng: {Một số người dùng chưa thử / Còn Change Request chưa phân loại / Sign-off conditional}
- **BLOCKED** — Không thể tiến hành do: {Môi trường UAT chưa sẵn sàng / Người dùng không tham gia / Không có acceptance criteria}
- **NEEDS_CONTEXT** — Cần bổ sung: {Danh sách người tham gia / Acceptance criteria / Thời gian UAT}




---

## Bước cuối — Sign-off + Audit Log (Level 3 — Stakeholder)

### 1. Publish UAT Summary lên Confluence

```bash
python tools/confluence_publish_markdown.py \
  --file "testing-output/reports/gate/uat-summary-{sprint}.md" \
  --parent-page "{confluence.parent_pages.team_root}/UAT"
```

### 2. Approval Request (L3 — BLOCKING)

AI dừng hoàn toàn. Không proceed bất kỳ bước nào cho đến khi nhận approval:

```
---
🔴 APPROVAL REQUIRED — 12-uat-support (Level 3 — Stakeholder)
Người phê duyệt:
  - Product Owner: [team.product_owner từ qa-config]
  - Business Rep: [team.stakeholders[] có uat_required=true]
Deadline: [ngày hiện tại + 48h]
Output: testing-output/reports/gate/uat-summary-{sprint}.md
Hành động bắt buộc:
  - Đọc UAT Sign-off Status table
  - Reply "Signed off" (nếu đạt) hoặc "Cần fix trước: [bug IDs]"
Không có hành động nào tiếp theo cho đến khi nhận phản hồi.
---
```

### 3. Audit Log

```yaml
execution_record:
  id: "{yyyy-mm-dd}-{HHmm}-12-uat"
  timestamp: "{yyyy-mm-ddTHH:mm}"
  skill: "12-uat-support"
  project: "{project.name}"
  sprint: "{project.sprint}"
  executor: "{executor}"
  input_summary: "UAT {sprint}: {N} users, {N} scenarios, {N} bugs phát sinh"
  output_paths:
    - "testing-output/reports/gate/uat-summary-{sprint}.md"
  status: "DONE | DONE_WITH_CONCERNS | BLOCKED"
  requires_human_review: true
  reviewer: null
  reviewed_at: null
  sign_off_status: "PENDING"
```