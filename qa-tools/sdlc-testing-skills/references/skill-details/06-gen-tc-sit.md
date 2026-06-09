# Detailed Procedure: 06-gen-tc-sit

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

- [ ] Đủ nhóm SIT: API contract, retry/rollback, async event, service dependency, auth
- [ ] R1/R2/R3 review coverage đã chạy, gap đã merge
- [ ] TSV 18+ cột đúng format, không còn ô trống không giải thích
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `notes`

---

# Skill 06 - Gen Test Case SIT

## Quick Reference

| | |
|---|---|
| **Input bắt buộc** | API spec / sequence diagram / service dependency map |
| **Input khuyến nghị** | HLTC outline (skill 04 nếu có) + qa-config.yaml |
| **Output** | TC SIT (18 cột), bao gồm retry/rollback/timeout scenarios |
| **Khác với skill 05** | Focus integration flow, không phải functional của từng service riêng lẻ |
| **Time estimate** | 45–90 phút / API group |
| **Sign-off** | L1 — Auto (nhưng cần 07-review-tc sau khi viết xong) |

> **Token optimization:** Nếu user chỉ hỏi về 1 API endpoint cụ thể, gen TC cho endpoint đó mà không cần đọc toàn bộ skill. Đọc đầy đủ khi gen SIT cho cả integration flow (multiple services).

---


## Quy tắc đầu vào từ HLTC

- Nếu không có HLTC, Skill 06 phải sinh SIT TC trực tiếp từ API spec, sequence diagram, service dependency map, ticket và các tài liệu đầu vào hiện có.
- HLTC là đầu vào ưu tiên khi đã tồn tại, không phải điều kiện bắt buộc để bắt đầu mọi yêu cầu SIT.
- Nếu có HLTC, Skill 06 chỉ được phép sinh SIT TC khi HLTC đang ở trạng thái `Approved`.
- Không được sinh SIT TC nếu file HLTC vẫn ghi `Kết quả gate: Not Approved`, kể cả khi trong hội thoại có nói rằng đã Approved.
- Nếu context mới nhất cho thấy HLTC đã được Approved nhưng file chưa cập nhật:
  - dừng bước sinh SIT TC
  - cập nhật lại chính file HLTC để đổi `Kết quả gate` sang `Approved`
  - chỉ sau đó mới tiếp tục sinh SIT TC
- Nguồn sự thật ưu tiên là file HLTC đã được cập nhật gần nhất, không dùng trạng thái Approved chỉ tồn tại trong chat.

> Nếu có HLTC outline từ Skill 04 (qa-core/04-test-design-high-level):
> - Mọi nhánh trong HLTC (`Kết quả gate: Approved`) đều phải có ít nhất 1 SIT TC cover — không được bỏ sót bất kỳ nhánh integration nào.
> - SIT TC không cần map 1-1 với HLTC node — 1 nhánh HLTC có thể cần nhiều SIT TC để cover đầy đủ integration scenario, failure path, retry/rollback.
> - Số lượng SIT TC phải đủ để cover toàn bộ luồng tích hợp theo API spec, service dependency, timeout/retry spec — không bị giới hạn bởi số lượng nhánh trong HLTC.
> - Nếu HLTC và API spec / sequence diagram mâu thuẫn: ưu tiên spec mới nhất, ghi chú rõ mâu thuẫn trong output.
> - HLTC chỉ dùng để chốt phạm vi high-level và tránh bỏ sót nhánh; SIT TC chi tiết phải bám theo đầy đủ nội dung API contract, service dependency map.

## Nguyên tắc bắt buộc

1. Thiếu API spec hoặc service dependency map → ghi `[Cần bổ sung]`, dừng.
2. Không gen TC functional đơn lẻ, refer sang Skill 05 (gen-tc-functional) nếu cần.
3. Expected result của rollback phải chỉ rõ trạng thái cuối của từng entity bị ảnh hưởng.
4. Khi tạo SIT testcase, chỉ cần gen 1 bảng SIT duy nhất, đúng format chuẩn, đủ coverage, không sinh file review coverage (R1/R2/R3) hoặc file review.tsv.
5. Review coverage/gap analysis là bước nội bộ, không xuất file phụ; chỉ xuất 1 file SIT duy nhất sau khi đã đảm bảo đủ coverage.
6. Nội dung testcase phải viết bằng tiếng Việt có dấu; chỉ giữ không dấu cho mã kỹ thuật như endpoint, status code, field name.

## Khác biệt so với Skill 05 (gen-tc-functional)

Skill này không gen TC functional đơn lẻ. Tập trung hoàn toàn vào:
- Luồng xuyên suốt nhiều service/module
- API contract và schema validation
- Failure scenarios: timeout, 4xx, 5xx, network partition
- Retry logic và idempotency ở tầng integration
- Rollback / compensating transaction
- Async event: message queue, webhook, event-driven flow
- Data consistency sau khi chuỗi API hoàn thành


## Format output

Xuất theo format SIT chuyên biệt, bám theo file mẫu Excel, chỉ xuất 1 file duy nhất:

1. Dòng 1 là dòng group header:
```tsv
                    Hệ thống A           Hệ thống B
```

2. Dòng 2 là header dữ liệu 19 cột (bổ sung cột Automation Level/Test Level gợi ý):
```tsv
No	Testcase ID	Test Summary	Precondition	Test Data	Steps	Expected Result	Actual Result	Test Result	Expected Result	Actual Result	Test Result	Final Result	Priority	ID Bugs	Link evidence	Màn hình test	Thời gian test	Automation Level
```

3. Dòng section/subsection:
- Cho phép chèn các dòng nhóm nghiệp vụ như `1. Truy vấn hợp lệ`, `1.1. Tài khoản truy vấn tồn tại`
- Các dòng này chỉ điền cột `No`, các cột còn lại để trống
- Dùng để chia nhóm test case theo nghiệp vụ thay vì in phẳng toàn bộ danh sách

4. Dòng test case chi tiết:
- `No`: dùng số thứ tự theo section, ví dụ `1`, `2`, `3`
- `Testcase ID`: theo format `="<PREFIX>_"&A[row]` nếu người dùng yêu cầu giữ công thức Excel; nếu chỉ xuất text thì dùng giá trị tĩnh như `INQ_OI_1`
- `Test Summary`: mô tả ngắn gọn, gắn rõ điều kiện nghiệp vụ và kỳ vọng chính, prefix `[TL:{level}]` ở đầu
- `Precondition`, `Test Data`, `Steps`: ghi chi tiết, cho phép xuống dòng trong cùng ô
- Cụm `Expected Result` / `Actual Result` / `Test Result` phía `Hệ thống A`: dùng cho kiểm chứng phía hệ thống gọi, UI, API Gateway hoặc upstream system
- Cụm `Expected Result` / `Actual Result` / `Test Result` phía `Hệ thống B`: dùng cho kiểm chứng phía hệ thống nhận xử lý, middleware, service downstream hoặc core integration layer
- `Final Result`, `ID Bugs`, `Link evidence`, `Màn hình test`, `Thời gian test`: để trống khi gen test case mới, chỉ điền nếu người dùng yêu cầu prefill
- `Automation Level`: điền `integration` mặc định, hoặc `e2e` nếu kiểm chứng xuyên suốt nhiều hệ thống

5. Quy ước nội dung:
- Mỗi test case phải có ít nhất một expected result ở cụm cột `Hệ thống A` hoặc `Hệ thống B`
- Nếu flow có xác minh ở cả hai phía, điền đủ cả hai cụm cột
- Nếu chỉ xác minh ở một phía, cụm còn lại để trống
- `Priority` dùng `High|Medium|Low`
- Không dùng format TSV 14 cột của Skill 05 cho SIT, trừ khi người dùng yêu cầu rõ `QMetry/Jira import format`

**Quy tắc Test Level trong `Test Summary` (bắt buộc):**
- Nhúng prefix theo format mặc định: `[TL:{level}]`, ví dụ `[TL:integration]`, `[TL:e2e]`, `[TL:component]`
- Prefix `[TL:{level}]` phải đặt ở đầu cột `Test Summary`, ví dụ: `[TL:integration] Đồng bộ trạng thái đơn hàng sang CRM thành công`
- Giá trị `{level}` lấy theo `automation_rules.test_level_policy.mapping_rules` trong `qa-config.yaml` nếu có
- Nếu không có config, mặc định SIT flow thường là `integration`; chỉ dùng `e2e` khi có kiểm chứng xuyên suốt nhiều hệ thống từ điểm vào đến kết quả cuối
- Không dùng `unit` trong `Test Summary`
Xuất theo format SIT chuyên biệt, bám theo file mẫu Excel:

1. Dòng 1 là dòng group header:
```tsv
						Hệ thống A			Hệ thống B
```

2. Dòng 2 là header dữ liệu 18 cột:
```tsv
No	Testcase ID	Test Summary	Precondition	Test Data	Steps	Expected Result	Actual Result	Test Result	Expected Result	Actual Result	Test Result	Final Result	Priority	ID Bugs	Link evidence	Màn hình test	Thời gian test
```

3. Dòng section/subsection:
- Cho phép chèn các dòng nhóm nghiệp vụ như `1. Truy vấn hợp lệ`, `1.1. Tài khoản truy vấn tồn tại`
- Các dòng này chỉ điền cột `No`, các cột còn lại để trống
- Dùng để chia nhóm test case theo nghiệp vụ thay vì in phẳng toàn bộ danh sách

4. Dòng test case chi tiết:
- `No`: dùng số thứ tự theo section, ví dụ `1`, `2`, `3`
- `Testcase ID`: theo format `="<PREFIX>_"&A[row]` nếu người dùng yêu cầu giữ công thức Excel; nếu chỉ xuất text thì dùng giá trị tĩnh như `INQ_OI_1`
- `Test Summary`: mô tả ngắn gọn, gắn rõ điều kiện nghiệp vụ và kỳ vọng chính
- `Precondition`, `Test Data`, `Steps`: ghi chi tiết, cho phép xuống dòng trong cùng ô
- Cụm `Expected Result` / `Actual Result` / `Test Result` phía `Hệ thống A`: dùng cho kiểm chứng phía hệ thống gọi, UI, API Gateway hoặc upstream system
- Cụm `Expected Result` / `Actual Result` / `Test Result` phía `Hệ thống B`: dùng cho kiểm chứng phía hệ thống nhận xử lý, middleware, service downstream hoặc core integration layer
- `Final Result`, `ID Bugs`, `Link evidence`, `Màn hình test`, `Thời gian test`: để trống khi gen test case mới, chỉ điền nếu người dùng yêu cầu prefill

5. Quy ước nội dung:
- Mỗi test case phải có ít nhất một expected result ở cụm cột `Hệ thống A` hoặc `Hệ thống B`
- Nếu flow có xác minh ở cả hai phía, điền đủ cả hai cụm cột
- Nếu chỉ xác minh ở một phía, cụm còn lại để trống
- `Priority` dùng `High|Medium|Low`
- Không dùng format TSV 14 cột của Skill 05 cho SIT, trừ khi người dùng yêu cầu rõ `QMetry/Jira import format`

**Quy tắc Test Level trong `Test Summary` (bắt buộc):**
- Nhúng prefix theo format mặc định: `[TL:{level}]`, ví dụ `[TL:integration]`, `[TL:e2e]`, `[TL:component]`
- Prefix `[TL:{level}]` phải đặt ở đầu cột `Test Summary`, ví dụ: `[TL:integration] Đồng bộ trạng thái đơn hàng sang CRM thành công`
- Giá trị `{level}` lấy theo `automation_rules.test_level_policy.mapping_rules` trong `qa-config.yaml` nếu có
- Nếu không có config, mặc định SIT flow thường là `integration`; chỉ dùng `e2e` khi có kiểm chứng xuyên suốt nhiều hệ thống từ điểm vào đến kết quả cuối
- Không dùng `unit` trong `Test Summary`

## Lưu ý đặc biệt

- Với async flow: mô tả rõ trong Precondition trạng thái queue/topic cần có
- Với rollback: Expected result phải chỉ rõ trạng thái cuối của từng entity bị ảnh hưởng
- Không gen TC functional đơn lẻ, refer sang Skill 05 (gen-tc-functional) nếu cần
- Ưu tiên nhóm testcase theo nghiệp vụ/luồng tích hợp giống file mẫu thay vì nhóm thuần theo loại kỹ thuật
- Nếu người dùng cung cấp file mẫu Excel mới hơn, ưu tiên file mẫu đó hơn template reference trong repo

**Lưu file vào:** `output_paths.test_cases.sit` từ qa-config, mặc định `testing-output/test-cases/sit/`
→ `testing-output/test-cases/sit/sit-{module}-{project.sprint}.tsv`


**Không cần xuất thêm bảng gợi ý Test Level cho automation, chỉ cần bổ sung trường Automation Level vào file SIT chính.**

## Bước verify coverage trước khi xuất

**Chạy bắt buộc, không xuất bảng này ra output.**

Tạo bảng nháp **Luồng nghiệp vụ x Nhóm SIT**. Hàng là các luồng nghiệp vụ tích hợp thực tế giữa các hệ thống, ví dụ:
- `Luồng đặt vé COD`
- `Luồng hoàn tiền`
- `Luồng sync trạng thái sang CRM`

Với mỗi ô:
- Có TC → ghi ID TC
- Không có TC nhưng áp dụng được → bổ sung TC ngay, không bỏ qua
- Không áp dụng → ghi `N/A + lý do`

| Luồng nghiệp vụ | SIT-1 Happy | SIT-2 Contract | SIT-3 Failure | SIT-4 Retry/Idem | SIT-5 Rollback | SIT-6 Async | SIT-7 Consistency | SIT-8 Compat |
|---|---|---|---|---|---|---|---|---|
| [Tên luồng 1] | ? | ? | ? | ? | ? | ? | ? | ? |
| [Tên luồng 2] | ? | ? | ? | ? | ? | ? | ? | ? |


Chỉ xuất bảng SIT khi đã đảm bảo đủ coverage các nhóm SIT, không còn ô trống chưa xử lý.

---

## Bước tiếp theo bắt buộc - Review coverage (R1 -> R2 -> R3)

## Completion Status

Báo cáo sau khi đã xuất bảng SIT đúng format, đủ coverage, không còn gap chưa xử lý:

- `DONE`: Bảng SIT đúng format, đủ coverage các nhóm SIT, không còn gap chưa xử lý
- `BLOCKED`: không thể gen do thiếu API spec, thiếu sequence diagram, hoặc service dependency không rõ
- `NEEDS_CONTEXT`: cần bổ sung thêm API spec, mô tả luồng nghiệp vụ tích hợp, hoặc SLA timeout threshold

## Checklist xác nhận lưu file đúng chuẩn

- [ ] Đã lưu file vào đúng thư mục `testing-output/test-cases/sit/` hoặc path override từ qa-config
- [ ] Tên file đúng pattern: `sit-{module}-{sprint}.tsv` hoặc theo naming convention project
- [ ] Nội dung file gồm: bảng SIT 19 cột (bổ sung Automation Level), đủ nhóm kiểm thử, exploratory
- [ ] Đã kiểm tra lại version, module, sprint trong tên file nếu có
