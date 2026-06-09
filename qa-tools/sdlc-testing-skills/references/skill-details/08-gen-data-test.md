# Detailed Procedure: 08-gen-data-test

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

- [ ] Mọi TC đều có data hoặc N/A với lý do rõ ràng
- [ ] Không có dòng data orphan (TC_ID không tồn tại trong danh sách TC đầu vào)
- [ ] Teardown script/SQL có cho mọi TC tạo/sửa/xóa data
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `notes`

---

# Skill 05 — Gen Data Test

## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| Danh sách TC (từ skill 05/06 hoặc file hiện có) | ✅ |
| Mô tả các trường dữ liệu (type, constraint, format) | ✅ |
| Thông tin môi trường (DB type, API endpoint) | Khuyến nghị |
| Yêu cầu PII / data sensitivity | Khuyến nghị |
| Test Plan (`testing-output/test-plan/Test_Plan_*.md`) | Tùy chọn — đọc nếu file tồn tại |

> **Nếu Test Plan tồn tại**, bắt buộc đọc các section sau trước khi sinh data:
>
> - **Mục 3b — Chiến lược sinh test data**: lấy thông tin golden dataset, loại data cần sinh (BVA/EP/normalize/threshold), công cụ gen, cách teardown, và traceability
> - **Mục 3a — Mutation strategy** (nếu có): lấy cách mutate từ golden dataset thay vì tự tạo data từ đầu
>
> **Quy tắc áp dụng:**
> - Nếu test plan định nghĩa golden dataset → dùng làm base, không tự gen lại từ đầu
> - Nếu test plan định nghĩa mutation strategy → áp dụng khi sinh BVA/EP, thay 1 tiêu chí mỗi lần mutate từ golden
> - Nếu test plan định nghĩa cách teardown → ưu tiên theo đó thay vì mặc định DELETE/UPDATE
> - Nếu test plan mâu thuẫn với nguyên tắc sinh data mặc định của skill → **test plan thắng**, ghi chú rõ trong output
> - Nếu test plan không đề cập đến một loại data cụ thể → dùng nguyên tắc mặc định của skill

## Chiến lược sinh data — Thứ tự ưu tiên nguồn

Skill 05 xác định chiến lược sinh data theo thứ tự sau:

**Ưu tiên 1 — Test Plan có Mục 3b:**
Nếu file Test Plan tồn tại **và** Mục 3b có nội dung chiến lược data cụ thể → làm theo hoàn toàn (golden dataset, mutation strategy, teardown approach). Không tự phát minh lại.

**Ưu tiên 2 — Fallback khi không có Test Plan hoặc Mục 3b trống:**
Nguồn chính là **file TC Functional (skill 05 — gen-tc-functional)**. Quy trình:
1. Đọc toàn bộ danh sách TC từ file functional TSV
2. Với mỗi TC: phân tích cột `Test Data`, `Precondition`, `Step summary`, `Expected result` để xác định data cần sinh
3. Bổ sung domain rule từ `qa-config.yaml` (`project.domain`) để áp dụng constraint phù hợp
4. Bổ sung thông tin từ requirements/AC nếu TC chưa đủ chi tiết về constraint

> **Quy tắc mapping bắt buộc:**
> - Mỗi TC phải có ít nhất 1 dòng data trong Master dataset (trừ trường hợp ghi `N/A` có lý do trong TC Coverage Map)
> - 1 TC có thể có nhiều dòng data nếu kịch bản yêu cầu nhiều biến thể (BVA sub-values, EP partitions, normalize variants)
> - Mọi dòng data phải có `TC_ID` tương ứng — không được có dòng data orphan không map về TC nào
> - Số dòng data phụ thuộc nội dung kịch bản: TC ghi cụ thể → 1 dòng; TC ghi chung → sinh đủ biến thể cần thiết để cover kịch bản

## Config (tuỳ chọn — đọc nếu cần áp dụng domain rule)

> **Thứ tự ưu tiên nguồn thông tin:** Test Plan (Mục 3b/3a) > TC Functional file > qa-config.yaml > nguyên tắc mặc định của skill.

Nếu có `qa-config.yaml` và người dùng chưa cung cấp đủ domain/environment context, chỉ đọc:

| Field | Dùng cho |
|---|---|
| `project.domain` | Chọn domain-specific rule (Luhn cho fintech, TEST_ prefix cho ecommerce, synthetic cho healthcare) |
| `environments.staging.url` | URL trong teardown script nếu cần call API reset |
| `security.focus` | Xác định trường dữ liệu nhạy cảm cần generate PII-safe |

## Nguyên tắc sinh data

- **Cụ thể tuyệt đối** — không dùng `[dữ liệu hợp lệ]`, `[tên hợp lệ]`
- **PII-safe** — dùng synthetic data, không dùng data thật từ production
- **BVA** — sinh đủ: min, max, min−1, max+1 cho mọi trường số/ngày/chuỗi có giới hạn
- **EP** — ít nhất 1 giá trị đại diện mỗi partition hợp lệ và không hợp lệ
- **Realistic** — data phải trông như thật (tên người, số điện thoại, email đúng format)
- **Độc lập** — mỗi bộ data test phải tự reset được, không phụ thuộc thứ tự chạy TC

## Format output — 1 file TSV duy nhất

**Quy tắc cơ bản:** 1 dòng = 1 bộ dataset hoàn chỉnh. 1 TC có thể có nhiều dòng nếu cần nhiều biến thể (BVA sub-values, EP partitions, Data-Driven scenarios).

Header:
```tsv
TC_ID	Dataset_ID	Test_Data	Loại	Teardown	Ghi chú
```

Mô tả cột:
- `TC_ID`: mã TC tương ứng (`TC-001`, `TC-002`…)
- `Dataset_ID`: mã dòng dataset, đánh số global hoặc theo TC (`DS-001`, `DS-002`…)
- `Test_Data`: toàn bộ field=value của bộ data trên 1 dòng, dùng `; ` làm dấu phân cách giữa các field (ví dụ: `FIELD_A=value1; FIELD_B=value2; FIELD_C=(trống)`). Không tách thành nhiều dòng.
- `Loại`: `BVA-min` / `BVA-max` / `BVA-min-1` / `BVA-max+1` / `EP-valid` / `EP-invalid` / `Corner` / `Normal` — ghi loại đặc trưng nhất của cả bộ data
- `Teardown`: câu SQL hoặc API call để reset data sau TC; ghi `—` nếu TC không tạo/sửa/xóa data
- `Ghi chú`: mô tả kịch bản, field mutate (nếu là negative/BVA), kỳ vọng engine xử lý

**Lưu file vào:** `output_paths.test_data` từ qa-config (default: `testing-output/test-data/`)
→ `testing-output/test-data/data-{module}-{project.sprint}.tsv`

## Bước verify coverage nội bộ (bắt buộc trước khi lưu file, không xuất ra output)

Trước khi lưu TSV, kiểm tra nội bộ:
- Mọi `TC_ID` trong danh sách đầu vào phải có ít nhất 1 dòng trong TSV
- TC không cần data cố định (Exploratory, Smoke độc lập, UI tĩnh) → ghi `N/A` + lý do vào cột `Ghi chú` của dòng đại diện
- Không có TC nào thiếu data mà không có lý do → nếu còn thiếu, bổ sung trước khi lưu
- Không có dòng data orphan — mọi dòng phải có `TC_ID` hợp lệ trỏ về TC trong danh sách đầu vào

## Lưu ý theo domain

- **Fintech**: sinh số tài khoản, số thẻ theo Luhn algorithm; không dùng số thật
- **Ecommerce**: sinh SKU, order code có prefix TEST_ để dễ cleanup
- **Healthcare**: data phải tuân HIPAA nếu context đề cập — dùng synthetic hoàn toàn

## Completion Status

- **DONE** — File TSV duy nhất đủ data cho mọi TC; mọi TC có data hoặc N/A có lý do; cột Teardown đầy đủ cho TC tạo/sửa/xóa data
- **DONE_WITH_CONCERNS** — TSV đã lưu nhưng còn TC thiếu data vì thiếu constraint (cần BA/Dev bổ sung) hoặc Teardown chưa cover rollback partial
- **BLOCKED** — Không thể gen do: {Chưa có TC danh sách / Không rõ constraint trường dữ liệu / Thiếu DB schema}
- **NEEDS_CONTEXT** — Cần bổ sung: {Danh sách TC / Mô tả các trường (type, min, max, format) / DB type để gen teardown SQL}
