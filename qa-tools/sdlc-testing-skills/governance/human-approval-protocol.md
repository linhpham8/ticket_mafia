# Human Approval Protocol

Quy trình phê duyệt của con người cho QA skill outputs. Tài liệu này dành cho **AI** (biết khi nào cần dừng và yêu cầu approval) và **QA Lead / PM** (biết họ cần làm gì).

---

## Cho AI — Khi nào dừng và yêu cầu approval

### Rule 1: Không tự proceed qua L3 gates
Sau khi hoàn thành output của skill 12, 13, 14 → dừng hoàn toàn, emit approval request, chờ phản hồi từ người dùng.

### Rule 2: Không push artifacts cho đến khi được approved
Các tool integration (Confluence push, Jira update, QMetry import) chỉ được thực hiện sau khi:
- L2: QA Lead confirm
- L3: Stakeholder approve

### Rule 3: Ghi audit log ngay sau khi hoàn thành
Dù DONE hay BLOCKED, luôn append execution_record vào `governance/audit-log.md`.

### Rule 4: Rollback không cần approval
Trong skill 14-smoke-production, nếu kết luận ROLLBACK → không cần chờ approval, notify ngay và ghi log.

---

## Cho QA Lead / PM — Cách phê duyệt

### Khi nhận Sign-Off Request (L2):

1. Mở file output tại path được chỉ định
2. Kiểm tra theo checklist của skill tương ứng
3. Reply vào chat AI:
   - `"Approved"` → AI cập nhật audit log và proceed
   - `"Approved với ghi chú: [nội dung]"` → AI cập nhật log và proceed  
   - `"Cần chỉnh sửa: [nội dung cụ thể]"` → AI sửa và request review lại

### Khi nhận Approval Request (L3):

1. Đọc đầy đủ output (go-no-go report / UAT sign-off / smoke result)
2. Kiểm tra tất cả gate đã pass chưa
3. Reply:
   - **Go-no-go**: `"GO"` / `"NO-GO"` / `"GO với điều kiện: [...]"`
   - **UAT**: `"Signed off"` / `"Cần fix trước: [bug IDs]"`
   - **Smoke**: `"STABLE"` / `"ROLLBACK"` / `"MONITOR [N] phút"`
4. AI sẽ:
   - Cập nhật audit log với approval
   - Thực hiện tool integration (push artifacts)
   - Tiếp tục luồng tiếp theo (hoặc dừng nếu NO-GO/ROLLBACK)

---

## Traceability matrix

Mọi quyết định L3 phải traceable từ:
```
Requirement → Test Case → Test Execution → Bug → Go/No-Go Decision → Deploy
```

AI maintain traceability bằng cách:
- Trace field trong mọi TC (link đến US/AC ID)
- Bug ID trong daily report link đến TC fail
- Go/No-Go report reference sprint report + UAT result
- Audit log link các execution record với nhau

---

## Danh sách người phê duyệt (cấu hình tại qa-config.yaml)

```yaml
team:
  qc_lead: "Tên QC Lead"
  dev_lead: "Tên Dev Lead"
  pm: "Tên PM"
  product_owner: "Tên PO"
  stakeholders:
    - name: "Tên"
      role: "Business Analyst / End User Rep / ..."
      uat_required: true
```

Nếu `qa-config.yaml` chưa có → AI hỏi người dùng cung cấp tên người phê duyệt trước khi emit approval request.
