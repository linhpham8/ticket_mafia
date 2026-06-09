---
name: 05-gen-tc-functional
description: >
  Tạo test case kiểm thử chức năng đầy đủ 12 nhóm theo chuẩn IEEE 29119 / ISTQB
  từ AC, BR, User Story. Trigger: viết testcase, gen TC, tạo test case chức năng,
  thiết kế testcase, test case functional. Output bắt buộc: đúng 1 file TSV chính có cột Test Level.
  Review coverage R1/R2/R3 là bước nội bộ để bổ sung TC còn thiếu trước khi xuất TSV cuối cùng.
---

# Functional Testcase Generation

> **BẮT BUỘC**: Đọc toàn bộ skill này TRƯỚC khi sinh bất kỳ TC nào. Không được bỏ qua bước nào.
> Đầu ra không qua đủ 12 nhóm + R1/R2/R3 + Rule Inventory là **không hợp lệ**.

## Đọc trước khi bắt đầu

- Đọc `project/qa-config.yaml` nếu tồn tại để lấy project code, module, output path, domain rules.
- Đọc `governance/GOVERNANCE.md` trước khi finalize hoặc publish.
- Governance gate: `L1` — không cần QA Lead review trước khi proceed.
- **KHÔNG** được đọc toàn bộ references ngay từ đầu; chỉ đọc khi cần xác minh edge case cụ thể.

## Inputs

- AC / User Story (bắt buộc)
- BR — Business Rules (nếu có)
- Checklist team (nếu có)
- Thông tin môi trường (nếu có)
- HLTC outline từ Skill 04 (tùy chọn, ưu tiên dùng khi có)

## Quy tắc đầu vào từ HLTC

- Nếu không có HLTC → sinh TC trực tiếp từ AC / BR / User Story.
- Nếu có HLTC → chỉ được sinh TC khi HLTC đang ghi `Kết quả gate: Approved` trong file.
- Không được dùng trạng thái "Approved" chỉ tồn tại trong chat — phải đọc file HLTC để xác nhận.
- Nếu HLTC chưa Approved: cập nhật file HLTC trước, sau đó mới sinh TC.
- Mọi nhánh trong HLTC đã Approved đều phải có các TC cover đầy đủ — không được bỏ sót.Với mỗi nhánh, sinh thêm case chi tiết hơn gồm edge case, boundary value, negative variant theo 12 nhóm kiểm thử ở Bước 2. Số lượng TC functional thường nhiều hơn số nhánh HLTC từ 2–5 lần.


## Workflow bắt buộc (theo thứ tự)

### Bước 0 — Kiểm tra file TC hiện có

Trước khi sinh TC mới:
1. Kiểm tra `testing-output/test-cases/functional/` xem đã có file TC cho module/sprint này chưa.
2. Nếu đã có → đọc file đó, hiểu cấu trúc, bổ sung thêm thay vì tạo file trùng.
3. Nếu chưa có → tiếp tục các bước dưới.

### Bước 1 — Lập Rule Inventory (BẮT BUỘC trước khi gen TC)

Trích toàn bộ Rule ID từ tài liệu requirements. Tạo bảng:

| Rule ID | Mô tả ngắn | Covered STT | Status | Nhóm | Gap |
|---|---|---|---|---|---|
| AC-01 | ... | | Chưa cover | | |

Quy tắc:
- Không được DONE nếu còn Rule nào: chưa có TC mapping (Covered STT rỗng), hoặc chưa ghi rõ `N/A + lý do` nếu không áp dụng.
- Mỗi Rule phải có tối thiểu 1 TC mapping.

### Bước 2 — Sinh TSV nháp (12 nhóm bắt buộc + Exploratory)

Tạo TC bao phủ đầy đủ 12 nhóm sau + phần Exploratory ở cuối. Không được bỏ sót nhóm nào có thể áp dụng:

| # | Nhóm | Tối thiểu bắt buộc |
|---|---|---|
| 1 | **AC-Based** | ≥1 positive + 1 negative cho mỗi AC |
| 2 | **BR-Based** | ≥1 TC cho mỗi BR quan trọng |
| 3 | **Basic Flow** | ≥1 E2E happy path end-to-end |
| 4 | **EP (Equivalence Partitioning)** | ≥1 valid + 1 invalid cho mỗi trường input |
| 5 | **BVA (Boundary Value Analysis)** | min, max, min−1, max+1 cho mỗi trường có giới hạn |
| 6 | **Decision Table / Pairwise / Data-Driven** | Mọi logic có ≥2 điều kiện phải có TC |
| 7 | **State Transition / Use Case** | Mọi transition hợp lệ + không hợp lệ |
| 8 | **Corner Cases & Error Guessing** | Idempotency, Race condition, Edge cases, Timeout |
| 9 | **Impact (Cross-feature)** | Sync, retry, rollback, API contract, tác động lên module khác |
| 10 | **Regression** | Luồng hiện có không bị ảnh hưởng bởi thay đổi mới |
| 11 | **Non-Functional** | Performance SLA, Security (OWASP), Reliability theo US |
| 12 | **Checklist-Based** | Bỏ qua nếu không có checklist trong input |
| ET | **Exploratory Testing** | Cuối file — **BẮT BUỘC**, không phụ thuộc vào checklist |

**Exploratory Testing — quy tắc bắt buộc:**
- Luôn thêm ≥2 rows Exploratory ở **cuối file TSV**, sau tất cả TC scripted.
- Cột STT: **số thứ tự tiếp nối** từ TC scripted cuối cùng (ví dụ: TC scripted cuối là 62 → ET rows là 63, 64).
- Cột Test Type: `Exploratory`.
- Cột Priority: `Low`.
- Cột Smoke / Auto: `N` (exploratory không script hóa).
- Cột Step summary: mô tả hướng khám phá (tự do, không cố định script).
- Cột Expected result: ghi chú điểm cần quan sát (không phải expected cụ thể).
- Cột Test Data: `—` nếu không có data cố định.
- Nội dung ET phải bao gồm ít nhất: (1) khám phá UX/hành vi từ góc nhìn người dùng lần đầu; (2) stress/edge input bất thường (string rất dài, ký tự đặc biệt, unicode, null byte, paste từ clipboard).

**Nhóm 6 — Data-Driven**: gộp nhiều tổ hợp dữ liệu vào 1 TC, liệt kê trong cột Test Data (dùng `\n` hoặc `;` phân cách), không tạo nhiều TC trùng logic.

**Nhóm 11 — Non-Functional tối thiểu**:
- Security: authentication boundary, authorization (RBAC), multi-tenancy isolation, OWASP Top 10 liên quan (SSRF, injection, broken access control)
- Performance: latency SLA (p95), throughput, graceful degradation
- Reliability: retry với idempotency key, rollback, heartbeat

### Bước 3 — Verify coverage nội bộ trước khi xuất (KHÔNG xuất bảng này ra output)

Tạo bảng nháp AC × Nhóm:
- Có TC → ghi STT TC
- Không có TC nhưng áp dụng được → **bổ sung TC ngay, không bỏ qua**
- Không áp dụng → ghi `N/A + lý do`

### Bước 4 — R1: Bản đồ bao phủ nội bộ (KHÔNG xuất ra file)

```
Mã yêu cầu | Mô tả yêu cầu | TC đã cover | Trạng thái | Nhóm kiểm thử đã có | Ghi chú
```

### Bước 5 — R2: Gap analysis nội bộ (KHÔNG xuất ra file)

```
Mã yêu cầu | Nhóm còn thiếu | Mô tả lỗ hổng | Đề xuất TC bổ sung | Priority | Câu hỏi làm rõ
```

### Bước 6 — R3: TC bổ sung từ gap (KHÔNG xuất ra file riêng)

```
STT | Summary | Test Level | Precondition | Test Data | Step summary | Expected result | Priority | Story Linkages | Test Type | Smoke | Auto | Phụ thuộc TC | Teardown | Trace | Note
```

- STT tiếp nối STT của TSV chính.
- Cột `Note`: ghi `GAP: [Mã yêu cầu] - [Nhóm]`.
- **Sau khi có R3: bổ sung TCs này vào cuối TSV chính** — không giữ R3 tách riêng.

### Bước 7 — Self-review chất lượng bắt buộc (KHÔNG bỏ qua)

Trước khi lưu file, quét toàn bộ từng TC trong TSV và kiểm tra theo bảng sau. Mọi TC vi phạm phải được sửa ngay — không được xuất file có lỗi:

| Tiêu chí | Hành động khi fail |
|---|---|
| Priority dùng `High`/`Medium`/`Low` — không dùng P1/P2/P3 | Đổi sang đúng format |
| Khi Priority = `High` → Smoke = `Y` | Sửa Smoke = Y hoặc hạ Priority xuống Medium |
| Auto ≥80% toàn file; mọi `Auto = N` có lý do trong cột Trace | Đặt lại Auto = Y nếu TC có thể assert được; nếu giữ N thì ghi lý do |
| Expected result không chứa cụm mơ hồ: "hoạt động đúng", "thành công", "hiển thị bình thường" | Viết lại cụ thể: HTTP code, field value, trạng thái entity |
| Trace field không trống và map về Rule ID tồn tại trong Rule Inventory | Bổ sung Trace hoặc sửa Rule ID sai |
| Test Data không chứa placeholder: `[dữ liệu hợp lệ]`, `[giá trị bất kỳ]`, `...` | Điền giá trị cụ thể |
| Teardown không để `-` nếu TC có tạo/sửa/xóa dữ liệu | Bổ sung bước teardown |
| Có ≥2 ET rows ở cuối file với STT là số nguyên tiếp nối, Test Type=Exploratory, Auto=N | Thêm ET rows nếu thiếu |

Kết quả self-review: **liệt kê ngắn gọn số TC đã sửa và vấn đề nào** (ví dụ: "Sửa 3 TC Priority P1→High, 1 TC Expected result mơ hồ"). Nếu không có vi phạm, ghi "Self-review: OK — không có vi phạm".

### Bước 8 — Hoàn thiện và lưu TSV chính

Merge R3 vào TSV chính. Kiểm tra toàn bộ checklist trước khi báo DONE.

## Format output TSV

Header bắt buộc (15 cột, đúng thứ tự):
```
STT	Summary	Test Level	Precondition	Test Data	Step summary	Expected result	Priority	Story Linkages	Test Type	Smoke	Auto	Phụ thuộc TC	Teardown	Trace
```

### Quy tắc format bắt buộc

| Cột | Giá trị hợp lệ | Quy tắc |
|---|---|---|
| STT | Số nguyên tiếp nối: `1`, `2`, `3`... (kể cả ET rows) | Không dùng `TC-001`; ET rows tiếp nối STT cuối |
| Test Level | `component` / `integration` / `e2e` | Chữ thường; không dùng `unit` |
| Priority | `High` / `Medium` / `Low` | Không dùng `P1/P2/P3` |
| Smoke | `Y` / `N` | Không dùng `Yes/No` |
| Auto | `Y` / `N` | Mặc định `Y`; chỉ `N` khi thuộc danh sách ngoại lệ bên dưới |
| Test Data | Dữ liệu cụ thể | Không dùng `[dữ liệu hợp lệ]` hoặc placeholder |
| Expected result | Kết quả cụ thể, verify được | Không mơ hồ |
| Teardown | Bước dọn dẹp cụ thể | Không được để `-` nếu TC tạo/sửa/xóa dữ liệu |

**Ưu tiên Priority:**
- `High`: luồng chính (happy path, basic flow), security critical, data integrity — phải pass trước khi release
- `Medium`: boundary, EP, integration, state transition, regression — cần pass trong sprint
- `Low`: exploratory, edge case ít gặp, UX cosmetic, BVA phụ

**Quy tắc Auto — mặc định `Y`, target ≥80% toàn file:**

`Auto = Y` khi TC có:
- Input/output xác định rõ (API, form field, response body)
- Expected result cụ thể, có thể assert bằng code
- Không phụ thuộc vào phán đoán chủ quan của người test

`Auto = N` **chỉ** khi thuộc một trong các trường hợp sau:
- TC yêu cầu đánh giá chủ quan về UX, màu sắc, layout, trải nghiệm
- TC phụ thuộc vào thiết bị vật lý, phần cứng hoặc môi trường không kiểm soát được
- TC là Exploratory (luôn `N`)
- TC kiểm tra race condition phức tạp, khó reproduce nhất quán trong CI/CD
- TC yêu cầu thao tác thủ công phức tạp trên Visual Builder drag-and-drop UI mà chưa có automation framework hỗ trợ

Khi đặt `Auto = N`, phải ghi lý do ngắn vào cột `Trace` (ví dụ: `Manual-UX`, `Manual-VB-DragDrop`, `Manual-HW`).

**Test Level mặc định:**
- Functional flow đầy đủ, nhiều service → `e2e`
- Logic đơn điểm, một màn hình/endpoint, ít phụ thuộc → `component`
- Tích hợp 2–3 service → `integration`

**Smoke = Y** chỉ khi: TC độc lập, không phụ thuộc TC khác, thời gian thực thi ngắn.

**Separator TSV**: chỉ dùng `|` pipe đơn — tuyệt đối không dùng `\|`.

**Ngôn ngữ**: Viết bằng tiếng Việt có dấu; giữ nguyên tiếng Anh cho mã kỹ thuật (ID, endpoint, field name, status code, HTTP method, keyword hệ thống).

### Đường dẫn lưu file

`testing-output/test-cases/functional/tc-{module}-{sprint}.tsv`
→ Ưu tiên dùng `output_paths.test_cases.functional` từ qa-config nếu có.

### Ràng buộc bắt buộc khi ghi file TSV

- **KHÔNG được thêm comment lines (`#`) vào đầu file TSV** — file phải bắt đầu bằng header row ngay dòng 1. Comment metadata về HLTC source chỉ được ghi trong chat, không ghi vào file.
- **Cột `Test Level` BẮT BUỘC phải có giá trị** trong mỗi data row (`e2e` / `integration` / `component`) — không được để trống, không được bỏ qua. File TSV phải có đúng 15 tab-separated values trên mỗi data row. Nếu thiếu `Test Level`, toàn bộ cột sau đó sẽ bị lệch 1 vị trí và không upload được lên QMetry.

## 14 Nguyên tắc bắt buộc

1. Thiếu AC hoặc Basic Flow → ghi `[Cần bổ sung]`, dừng, không tự suy diễn.
2. TSV chỉ dùng `|` (pipe đơn), tuyệt đối không dùng `\|`.
3. Data-Driven: gộp thành 1 TC, liệt kê tổ hợp dữ liệu trong cột Test Data, không tạo TC trùng logic.
4. Teardown: không để `-` nếu TC có tạo / sửa / xóa dữ liệu.
5. `Smoke = Y` chỉ khi TC độc lập và thời gian thực thi ngắn.
6. Không tạo TC trùng lặp nội dung dù khác tên.
7. Expected result phải cụ thể, verify được — không mơ hồ.
8. Test Data phải cụ thể — không dùng placeholder như `[dữ liệu hợp lệ]`.
9. TC phải tương thích Robot Framework nếu có nhu cầu automation.
10. Luôn chạy full flow: gen TSV nháp → R1/R2/R3 → bổ sung gap → mới DONE. Không dừng sau khi có TSV nháp.
11. Không được DONE nếu R1/R2/R3 còn gap chưa merge vào TSV chính.
12. Nội dung TC viết tiếng Việt có dấu; giữ nguyên code kỹ thuật bằng tiếng Anh.
13. Kiểm tra file TC đã có trước khi tạo mới — tránh tạo file trùng.
14. Priority = `High`/`Medium`/`Low`; Auto mặc định `Y` — chỉ `N` khi UX chủ quan, hardware, Visual Builder drag-drop, race condition khó reproduce, hoặc Exploratory; target Auto ≥80% toàn file; ET rows STT tiếp nối, ở cuối file.

## Outputs

- Đúng 1 file TSV chính `tc-*.tsv`
- Không sinh file R1/R2/R3 riêng — mọi kết quả review phải merge vào TSV chính

## Completion Status

| Status | Điều kiện |
|---|---|
| `DONE` | TSV đúng format + R1/R2/R3 không còn gap chưa merge + Rule Inventory đầy đủ |
| `DONE_WITH_CONCERNS` | TSV đã hoàn tất nhưng còn assumption hoặc điểm cần BA xác nhận |
| `BLOCKED` | Thiếu AC hoặc Basic Flow; hoặc HLTC chưa ghi `Kết quả gate: Approved` trong file |
| `NEEDS_CONTEXT` | AC/BR không đủ để gen hoặc đối chiếu review — liệt kê câu hỏi bổ sung |

## Checklist xác nhận trước khi DONE

### Format
- [ ] Đúng thư mục `testing-output/test-cases/functional/` hoặc path override từ qa-config
- [ ] Tên file đúng pattern: `tc-{module}-{sprint}.tsv`
- [ ] File TSV bắt đầu bằng header row ngay dòng 1 — **không có comment `#` lines**
- [ ] Đúng 15 cột theo header chuẩn, có cột `Test Level`
- [ ] Mỗi data row có đúng **15 tab-separated values** — `Test Level` không được trống
- [ ] STT dùng số nguyên tiếp nối toàn file kể cả ET rows — không dùng `TC-001` hay label text
- [ ] Priority dùng `High`/`Medium`/`Low` — không dùng P1/P2/P3
- [ ] Smoke/Auto dùng `Y`/`N`, Test Level chữ thường (`component`/`integration`/`e2e`)
- [ ] Auto = `Y` cho ≥80% TC; mọi `Auto = N` ghi lý do trong cột Trace
- [ ] Có ≥2 rows Exploratory Testing ở cuối file: STT tiếp nối, Test Type=Exploratory, Auto=N

### Coverage
- [ ] Đã lập Rule Inventory — mọi Rule ID đã cover hoặc ghi N/A + lý do
- [ ] Đủ 12 nhóm kiểm thử bắt buộc (Checklist-Based có thể N/A nếu không có checklist)
- [ ] Đã có TC cho nhóm Impact (cross-feature, API contract, retry/rollback)
- [ ] Đã có TC Non-Functional: Security (OWASP), Performance (SLA), Reliability

### Quality gates
- [ ] Đã chạy đủ R1/R2/R3, mọi gap đã merge vào TSV chính
- [ ] Không còn file output review coverage riêng
- [ ] Teardown điền đủ cho mọi TC có tạo/sửa/xóa dữ liệu
- [ ] Không còn placeholder trong Test Data hoặc Expected result
- [ ] Đã append execution record vào `governance/audit-log.md`
- [ ] Đã cập nhật `project/session-state.yaml` → `last_execution`, `sprint_progress.tc_total`

## Stop Conditions

- Required input thiếu và không thể suy diễn từ artifacts hiện có.
- Task yêu cầu publish ra ngoài nhưng chưa có governance approval.
- Action nằm ngoài scope của skill này.
