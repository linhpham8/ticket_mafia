---
name: 06-gen-tc-sit
description: >
  Tạo test case kiểm thử tích hợp (SIT) tập trung vào integration flow, API contract,
  retry/rollback, async event, service dependency. Trigger: SIT, integration test,
  kiểm thử tích hợp, API contract test, service integration, luồng liên module.
  Output bắt buộc: bảng SIT 19 cột + review coverage R1/R2/R3 + merge TC bổ sung từ R3
  vào bảng chính. Không được kết thúc sớm.
---

# SIT Testcase Generation

> **BẮT BUỘC**: Đọc toàn bộ skill này TRƯỚC khi sinh bất kỳ TC nào. Không bỏ qua bước nào.

## Khác biệt với Skill 05 (gen-tc-functional)

Skill này **không** gen TC functional đơn lẻ (refer sang Skill 05 nếu cần).
Tập trung hoàn toàn vào:
- Luồng xuyên suốt nhiều service/module
- API contract và schema validation
- Failure scenarios: timeout, 4xx, 5xx, network partition
- Retry logic và idempotency ở tầng integration
- Rollback / compensating transaction
- Async event: message queue, webhook, event-driven flow
- Data consistency sau khi chuỗi API hoàn thành

## Đọc trước khi bắt đầu

- Đọc `project/qa-config.yaml` nếu tồn tại.
- Đọc `governance/GOVERNANCE.md` trước khi finalize.
- Governance gate: `L1` — không cần QA Lead review trước khi proceed.

## Inputs

- API spec / sequence diagram / service dependency map (bắt buộc)
- HLTC outline từ Skill 04 (khuyến nghị khi có)
- qa-config.yaml (nếu có)

Nếu thiếu API spec hoặc service dependency map → ghi `[Cần bổ sung]`, dừng.

## Quy tắc đầu vào từ HLTC

- Nếu không có HLTC → sinh SIT TC trực tiếp từ API spec, sequence diagram, service dependency map.
- Nếu có HLTC → chỉ được sinh TC khi HLTC đang ghi `Kết quả gate: Approved` trong file.
- Không được dùng trạng thái "Approved" chỉ tồn tại trong chat — phải đọc file HLTC để xác nhận.
- Nếu HLTC chưa Approved: cập nhật file HLTC trước, sau đó mới sinh SIT TC.
- Nếu HLTC và API spec/sequence diagram mâu thuẫn: ưu tiên spec mới nhất, ghi chú mâu thuẫn trong output.

## Workflow bắt buộc (theo thứ tự)

### Bước 1 — Map integration topology

- Xác định: systems, contracts, events, data handoff, idempotency, retry, timeout, rollback, monitoring points.
- Tạo danh sách các luồng nghiệp vụ tích hợp thực tế (ví dụ: "Luồng deploy agent", "Luồng sync trạng thái").

### Bước 2 — Sinh bảng SIT nháp (8 nhóm bắt buộc)

Phân loại TC theo 8 nhóm SIT:

| # | Nhóm SIT | Tối thiểu |
|---|---|---|
| SIT-1 | **Happy path** | ≥1 E2E integration flow thành công cho mỗi luồng nghiệp vụ |
| SIT-2 | **API Contract** | Schema validation, response structure, header, auth token |
| SIT-3 | **Failure scenarios** | 4xx, 5xx, timeout, network partition cho mỗi service call |
| SIT-4 | **Retry & Idempotency** | Retry với cùng idempotency key; không duplicate data |
| SIT-5 | **Rollback / Compensating** | Expected result phải chỉ rõ trạng thái cuối từng entity bị ảnh hưởng |
| SIT-6 | **Async Event** | Queue/topic state trong Precondition; verify message consumed |
| SIT-7 | **Data Consistency** | Data integrity sau chuỗi API hoàn thành; eventual consistency |
| SIT-8 | **Compatibility** | Backward compat với version cũ; breaking change detection |

### Bước 3 — Verify coverage nội bộ (KHÔNG xuất ra output)

Tạo bảng nháp **Luồng nghiệp vụ × Nhóm SIT**:

| Luồng nghiệp vụ | SIT-1 | SIT-2 | SIT-3 | SIT-4 | SIT-5 | SIT-6 | SIT-7 | SIT-8 |
|---|---|---|---|---|---|---|---|---|
| [Tên luồng 1] | ? | ? | ? | ? | ? | ? | ? | ? |

- Có TC → ghi ID TC
- Không có TC nhưng áp dụng được → **bổ sung TC ngay**
- Không áp dụng → ghi `N/A + lý do`

Chỉ xuất bảng SIT khi đã đảm bảo đủ coverage, không còn ô trống chưa xử lý.

### Bước 4 — R1/R2/R3 coverage review (KHÔNG xuất ra file riêng)

Chạy 3 lượt review nội bộ:

**R1 — Bản đồ bao phủ:**
```
Luồng nghiệp vụ | API/Event liên quan | TC đã cover | Trạng thái | Nhóm SIT đã có | Ghi chú
```

**R2 — Gap analysis:**
```
Luồng nghiệp vụ | Nhóm còn thiếu | Mô tả lỗ hổng | Đề xuất TC bổ sung | Priority | Câu hỏi làm rõ
```

**R3 — TC bổ sung từ gap:**
```
No | Testcase ID | Test Summary | Precondition | Test Data | Steps | Expected Result (A) | Actual Result (A) | Test Result (A) | Expected Result (B) | Actual Result (B) | Test Result (B) | Final Result | Priority | ID Bugs | Link evidence | Màn hình test | Thời gian test | Automation Level | Note
```
- Cột `Note`: ghi `GAP: [Luồng] - [Nhóm SIT]`
- **Sau khi có R3: merge TC này vào bảng SIT chính** — không giữ R3 tách riêng.

### Bước 5 — Hoàn thiện và lưu bảng SIT

## Format output SIT (19 cột)

**Dòng 1 — Group header:**
```
					Hệ thống A			Hệ thống B
```

**Dòng 2 — Header dữ liệu:**
```
No	Testcase ID	Test Summary	Precondition	Test Data	Steps	Expected Result	Actual Result	Test Result	Expected Result	Actual Result	Test Result	Final Result	Priority	ID Bugs	Link evidence	Màn hình test	Thời gian test	Automation Level
```

**Dòng section/subsection:**
- Chèn dòng nhóm nghiệp vụ: `1. Truy vấn hợp lệ`, `1.1. Tài khoản tồn tại`
- Chỉ điền cột `No`, các cột còn lại để trống.

### Quy tắc điền từng cột

| Cột | Quy tắc |
|---|---|
| `No` | Số thứ tự theo section: `1`, `2`, `3`... |
| `Testcase ID` | Text tĩnh như `INQ_OI_1`; hoặc công thức Excel nếu user yêu cầu |
| `Test Summary` | Prefix `[TL:{level}]` ở đầu, ví dụ `[TL:integration] Đồng bộ trạng thái...` |
| `Test Data` | Dữ liệu cụ thể — không dùng placeholder |
| `Expected Result (A)` | Phía hệ thống gọi: UI, API Gateway, upstream system |
| `Expected Result (B)` | Phía hệ thống nhận: middleware, service downstream |
| `Final Result`, `ID Bugs`, `Link evidence`, `Màn hình test`, `Thời gian test` | Để trống khi gen mới |
| `Automation Level` | `integration` mặc định; `e2e` khi kiểm chứng xuyên suốt nhiều hệ thống |
| `Priority` | `High` / `Medium` / `Low` |

**Test Level trong Test Summary:**
- `[TL:integration]`: SIT flow thông thường (2–3 services)
- `[TL:e2e]`: xuyên suốt nhiều hệ thống từ điểm vào đến kết quả cuối
- Không dùng `unit`
- Ưu tiên dùng `automation_rules.test_level_policy.mapping_rules` từ qa-config nếu có.

**Mỗi TC phải có ít nhất 1 expected result** ở cụm A hoặc B. Nếu có xác minh cả hai phía → điền đủ cả hai.

**Với async flow**: mô tả rõ trong Precondition trạng thái queue/topic cần có.

**Với rollback**: Expected result phải chỉ rõ trạng thái cuối của từng entity bị ảnh hưởng.

## 6 Nguyên tắc bắt buộc

1. Thiếu API spec hoặc service dependency map → ghi `[Cần bổ sung]`, dừng.
2. Không gen TC functional đơn lẻ — refer sang Skill 05 nếu cần.
3. Expected result của rollback phải chỉ rõ trạng thái cuối từng entity.
4. R1/R2/R3 là bước nội bộ — không xuất file review riêng; chỉ xuất 1 file SIT duy nhất sau khi đảm bảo đủ coverage.
5. Nội dung TC viết tiếng Việt có dấu; giữ nguyên tiếng Anh cho mã kỹ thuật (endpoint, status code, field name).
6. Ưu tiên nhóm TC theo luồng nghiệp vụ/integration flow, không nhóm thuần theo loại kỹ thuật.

## Đường dẫn lưu file

`testing-output/test-cases/sit/sit-{module}-{sprint}.tsv`
→ Ưu tiên `output_paths.test_cases.sit` từ qa-config nếu có.

## Completion Status

| Status | Điều kiện |
|---|---|
| `DONE` | Bảng SIT 19 cột đúng format + R1/R2/R3 không còn gap chưa merge |
| `BLOCKED` | Thiếu API spec, thiếu sequence diagram, hoặc service dependency không rõ |
| `NEEDS_CONTEXT` | Cần bổ sung API spec, mô tả luồng, hoặc SLA timeout threshold |

## Checklist trước khi DONE

- [ ] File lưu đúng `testing-output/test-cases/sit/` hoặc path override từ qa-config
- [ ] Tên file đúng pattern: `sit-{module}-{sprint}.tsv`
- [ ] Bảng SIT 19 cột với group header đúng format
- [ ] Đủ 8 nhóm SIT (SIT-1 đến SIT-8), các nhóm không áp dụng ghi N/A + lý do
- [ ] Đã chạy R1/R2/R3 — mọi gap đã merge vào bảng chính
- [ ] Không còn file output R1/R2/R3 riêng
- [ ] Teardown / rollback expected result đầy đủ
- [ ] Đã append execution record vào `governance/audit-log.md`
- [ ] Đã cập nhật `project/session-state.yaml` → `last_execution`

## Stop Conditions

- Thiếu input bắt buộc và không thể suy diễn từ artifacts hiện có.
- Task yêu cầu publish ra ngoài nhưng chưa có governance approval.
- Action nằm ngoài scope của skill này.
