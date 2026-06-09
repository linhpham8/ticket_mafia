# Detailed Procedure: 05-gen-tc-functional

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

- [ ] Đủ 12 nhóm kiểm thử — không thiếu nhóm nào
- [ ] R1/R2/R3 review coverage đã chạy, mọi gap đã merge vào TSV chính
- [ ] TSV 15 cột đúng header, không còn placeholder
- [ ] HLTC ở trạng thái `Approved` nếu có HLTC làm đầu vào
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `sprint_progress.tc_total`

---

# Skill 05 - Gen Test Case Functional


## Quy tắc đầu vào từ HLTC

- Nếu không có HLTC, Skill 05 phải sinh Functional TC trực tiếp từ AC / BR / User Story và các tài liệu đầu vào hiện có.
- HLTC là đầu vào ưu tiên khi đã tồn tại, không phải điều kiện bắt buộc để bắt đầu mọi yêu cầu.
- Nếu có HLTC, Skill 05 chỉ được phép sinh Functional TC khi HLTC đang ở trạng thái `Approved`.
- Không được sinh Functional TC nếu file HLTC vẫn ghi `Kết quả gate: Not Approved`, kể cả khi trong hội thoại có nói rằng đã Approved.
- Nếu context mới nhất cho thấy HLTC đã được Approved nhưng file chưa cập nhật:
  - dừng bước sinh Functional TC
  - cập nhật lại chính file HLTC để đổi `Kết quả gate` sang `Approved`
  - chỉ sau đó mới tiếp tục sinh Functional TC
- Nguồn sự thật ưu tiên là file HLTC đã được cập nhật gần nhất, không dùng trạng thái Approved chỉ tồn tại trong chat.

## Nguyên tắc bắt buộc

1. Thiếu AC hoặc Basic Flow → ghi `[Cần bổ sung]`, dừng, không tự suy diễn.
2. TSV output chỉ dùng `|` (pipe đơn), tuyệt đối không dùng `\|`.
3. Data-Driven: gộp thành 1 TC, liệt kê tổ hợp dữ liệu trực tiếp trong cột Test Data (dùng `|` phân cách), không tạo nhiều TC trùng logic và không dùng bảng dataset cuối file.
4. Teardown: không để `-` nếu TC có tạo / sửa / xóa dữ liệu.
5. `Smoke = Y` chỉ khi TC độc lập và thời gian thực thi ngắn.
6. Không tạo TC trùng lặp nội dung dù khác tên.
7. Kết quả mong muốn phải cụ thể, verify được.
8. Dữ liệu test phải cụ thể, không dùng `[dữ liệu hợp lệ]`.
9. Automation context: TC được gen phải khả dụng cho Robot Framework nếu có nhu cầu automation.
10. Dù user chỉ nhắn ngắn như "tạo testcase", vẫn phải chạy full flow: gen TSV nháp → review coverage nội bộ R1/R2/R3 → bổ sung TC thiếu vào TSV chính → mới được báo DONE.
11. Không được dừng ở bước gen TSV nháp; nếu review coverage nội bộ còn gap chưa merge vào TSV chính thì mặc định là chưa hoàn thành.
12. Nội dung testcase phải viết bằng tiếng Việt có dấu; chỉ giữ nguyên không dấu cho mã kỹ thuật như ID, endpoint, field name, status code, keyword hệ thống.
13. Chỉ xuất đúng 1 file đầu ra là TSV chính; không sinh file review coverage riêng.

## Điều kiện hoàn thành bắt buộc theo inventory rule

- Trước khi sinh TC, BẮT BUỘC phải trích toàn bộ Rule ID từ tài liệu requirements (ví dụ: GhepRule.md) và lập inventory rule.
- Phải tạo bảng inventory: | Rule ID | Covered STT | Status | Gap | cho toàn bộ rule.
- Không được DONE nếu còn bất kỳ Rule nào:
  - chưa có TC nào mapping (Covered STT rỗng)
  - chưa ghi rõ N/A + lý do nếu rule không áp dụng
- Mỗi Rule phải có tối thiểu 1 TC mapping (không chỉ mỗi nhóm coverage có đại diện).
- Review coverage nội bộ (R1/R2/R3) phải merge mọi gap vào TSV chính, mapping rõ từng Rule ID.
- Không được báo DONE nếu chưa đủ per-rule coverage inventory.

## Checklist xác nhận hoàn thành (bổ sung)

- [ ] Đã trích toàn bộ Rule ID từ requirements, lập inventory rule
- [ ] Mỗi Rule ID đã có tối thiểu 1 TC mapping hoặc ghi rõ N/A + lý do
- [ ] Không còn Rule nào chưa cover hoặc chưa trace
- [ ] Review coverage nội bộ đã merge mọi gap vào TSV chính

## Đầu vào

- AC / User Story (bắt buộc)
- BR - Business Rules (nếu có)
- Checklist team (nếu có)
- Thông tin môi trường (nếu có)
- HLTC outline từ Skill 04 (qa-core/04-test-design-high-level) (tùy chọn, ưu tiên dùng khi có)

> Nếu có HLTC outline từ Skill 04 (qa-core/04-test-design-high-level):
> - Mọi nhánh trong HLTC (`Kết quả gate: Approved`) đều phải có ít nhất 1 TC cover — không được bỏ sót bất kỳ nhánh nào đã được Approved.
> - Functional TC không cần map 1-1 với HLTC node — 1 nhánh HLTC có thể cần nhiều TC chi tiết để cover đầy đủ AC, EP, BVA, negative case.
> - Số lượng Functional TC phải đủ để cover toàn bộ nội dung US, AC, BR, spec API — không bị giới hạn bởi số lượng nhánh trong HLTC.
> - Nếu HLTC outline và AC/BR mâu thuẫn: ưu tiên AC/BR mới nhất, ghi chú rõ mâu thuẫn trong output.
> - Trước khi gen TC, bắt buộc kiểm tra file HLTC đang ghi `Kết quả gate: Approved`; nếu chưa Approved thì không được đi tiếp.
> - HLTC chỉ dùng để chốt phạm vi high-level và tránh bỏ sót nhánh; TC chi tiết phải bám theo đầy đủ nội dung US, AC, spec API.

## 12 nhóm bắt buộc

Đọc `../../references/tc-template.tsv` để lấy format chuẩn đầu ra.

| # | Nhóm | Tối thiểu |
|---|---|---|
| 1 | AC-Based | >=1 positive + 1 negative mỗi AC |
| 2 | BR-Based | >=1 TC mỗi BR quan trọng |
| 3 | Basic Flow | E2E happy path |
| 4 | EP | >=1 valid + 1 invalid mỗi trường input |
| 5 | BVA | min, max, min-1, max+1 |
| 6 | Decision Table / Pairwise / Data-Driven | Logic >=2 điều kiện |
| 7 | State Transition / Use Case | Transition hợp lệ + không hợp lệ |
| 8 | Corner Cases & Error Guessing | Idempotency, Race condition, Edge |
| 9 | Impact | Sync, retry, rollback, API contract |
| 10 | Regression | Luồng hiện có không bị ảnh hưởng |
| 11 | Non-Functional | Performance, Security, Reliability, tùy US |
| 12 | Checklist-Based | Bỏ qua nếu không có checklist trong input |

## Format output

Header TSV chính:
```tsv
STT	Summary	Test Level	Precondition	Test Data	Step summary	Expected result	Priority	Story Linkages	Test Type	Smoke	Auto	Phụ thuộc TC	Teardown	Trace
```

**Quy tắc Test Level:**
- Ghi giá trị vào cột `Test Level`: `component`, `integration`, `e2e`
- Không bắt buộc nhúng prefix `[TL:{level}]` vào `Summary`
- Nếu input cũ có prefix `[TL:{level}]` trong `Summary`, phải chuẩn hóa sang cột `Test Level` riêng
- Nếu không có config, mặc định:
  - Functional flow đầy đủ → `e2e`
  - Functional logic đơn điểm, một màn hình/endpoint, ít phụ thuộc → `component`
- Không dùng `unit`

**Lưu file vào:** `output_paths.test_cases.functional` từ qa-config, mặc định `testing-output/test-cases/functional/`
→ `testing-output/test-cases/functional/tc-{module}-{project.sprint}.tsv`

**Output cuối cùng:**
- Chỉ 1 file TSV chính `tc-*.tsv`
- Mọi kết quả review coverage nội bộ phải được merge vào chính file này trước khi kết thúc

## Bước verify coverage trước khi xuất

**Chạy bắt buộc trước khi xuất TSV, không xuất bảng này ra output.**

Tạo bảng nháp AC x Nhóm. Với mỗi ô:
- Có TC → ghi STT TC
- Không có TC nhưng áp dụng được → bổ sung TC ngay, không bỏ qua
- Không áp dụng cho AC này → ghi `N/A + lý do`

## Bước tiếp theo bắt buộc - Review coverage nội bộ (R1 -> R2 -> R3)

> Skill 05 chưa hoàn thành cho đến khi review coverage nội bộ đã chạy xong và toàn bộ gap đã được merge vào TSV chính.
> Không báo DONE, không dừng, không hỏi người dùng; tự chạy ngay sau khi tạo TSV nháp.

### R1 - Bản đồ bao phủ nội bộ

Header nội bộ:
```tsv
Mã yêu cầu	Mô tả yêu cầu	TC đã cover	Trạng thái	Nhóm kiểm thử đã có	Ghi chú
```

### R2 - Gap analysis nội bộ

Header nội bộ:
```tsv
Mã yêu cầu	Nhóm còn thiếu	Mô tả lỗ hổng	Đề xuất TC bổ sung	Priority	Câu hỏi làm rõ
```

### R3 - TC bổ sung nội bộ

Header nội bộ:
```tsv
STT	Summary	Test Level	Precondition	Test Data	Step summary	Expected result	Priority	Story Linkages	Test Type	Smoke	Auto	Phụ thuộc TC	Teardown	Trace	Note
```

Quy tắc:
- STT tiếp nối STT của TSV chính
- Cột `Note`: ghi `GAP: [Mã yêu cầu] - [Nhóm]`
- Sau khi có R3, bổ sung các TC này vào cuối TSV chính trước dòng Exploratory
- Không xuất riêng R1/R2/R3 ra file

## Completion Status

- `DONE`: TSV đúng format chuẩn và review coverage nội bộ không còn gap chưa merge
- `DONE_WITH_CONCERNS`: TSV đã hoàn tất nhưng còn assumption hoặc điểm cần BA xác nhận
- `BLOCKED`: không thể gen do thiếu AC hoặc thiếu Basic Flow
- `BLOCKED`: không thể gen do HLTC chưa được cập nhật `Kết quả gate: Approved`
- `NEEDS_CONTEXT`: tài liệu AC/BR không đủ để gen hoặc đối chiếu review, cần liệt kê câu hỏi bổ sung

## Checklist xác nhận lưu file đúng chuẩn (bắt buộc)

### 1. Format
- [ ] Đúng thư mục `testing-output/test-cases/functional/` hoặc path override từ qa-config
- [ ] Tên file đúng pattern: `tc-{module}-{sprint}.tsv` hoặc theo naming convention project
- [ ] Đúng header chuẩn 15 cột, có cột `Test Level`
- [ ] Có đầy đủ exploratory và teardown nếu có tạo/sửa/xóa dữ liệu

### 2. Coverage 12 nhóm
- [ ] Đã có test case cho tất cả 12 nhóm kiểm thử bắt buộc (AC-Based, BR-Based, Basic Flow, EP, BVA, Data-Driven, State Transition, Corner Cases, Impact, Regression, Non-Functional, Checklist-Based nếu có checklist)

### 3. Quality gates
- [ ] Đã chạy đủ R1/R2/R3, mọi gap đã được bổ sung vào TSV chính
- [ ] Không còn file output review coverage riêng
- [ ] Đã kiểm tra lại version, module, sprint trong tên file nếu có

**Lưu ý bắt buộc:** Agent phải đọc toàn bộ skill này trước khi sinh bất kỳ test case nào. Output không qua đủ 12 nhóm + R1/R2/R3 là không hợp lệ.
