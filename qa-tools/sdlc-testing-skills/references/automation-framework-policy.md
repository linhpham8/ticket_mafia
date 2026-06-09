# Automation Framework Policy (Robot Framework + Playwright)

Mục tiêu: Chuẩn kiến trúc đầy đủ cho automation script, dùng để tham chiếu, review và onboarding.

## Phạm vi

1. Robot Framework là framework chạy test chính.
2. Hỗ trợ API + UI + SIT.
3. UI ưu tiên Browser library (Playwright engine).
4. Script sinh từ Functional/SIT test case.
5. Data-driven, không hardcode.
6. Hỗ trợ đa môi trường.

## Kiến trúc 4 lớp

1. Layer 1: Test Cases
- Chỉ gọi high-level keywords.
- Không SQL trực tiếp.

2. Layer 2: High-Level Keywords
- Mô tả flow nghiệp vụ.
- Được assert nghiệp vụ.

3. Layer 3: Low-Level Keywords
- Thao tác kỹ thuật nguyên tử.
- Không assert nghiệp vụ.

4. Layer 4: Libraries/Connectors
- Robot libs + custom Python libs + connectors.

## Quy tắc phụ thuộc

1. Layer 1 -> Layer 2 -> Layer 3 -> Layer 4.
2. Cấm Layer 1 gọi trực tiếp Layer 3/4.
3. Cấm Layer 3 assert nghiệp vụ.

## Dữ liệu và môi trường

1. Data đặt tại `testing-output/automation/DataTest/` (CSV/JSON/YAML).
2. Không hardcode URL, token, credential, secret.
3. Dùng `Variables/ENV_<ENV>.yaml` cho DEV/QC/UAT/STG.

## Naming và output path chuẩn

1. Test suite:
- `testing-output/automation/Projects/<NhomChucNang>/<Feature>.robot`

2. High-level:
- `testing-output/automation/KeywordLibraries/<Module>/HighLevelKeywords/<Module>_High.resource`

3. Low-level:
- `testing-output/automation/KeywordLibraries/<Module>/LowLevelKeywords/<Module>_Low.resource`

4. Verification:
- `testing-output/automation/KeywordLibraries/<Module>/VerificationKeywords/<Module>_Verification.resource`

5. Dữ liệu:
- `testing-output/automation/DataTest/<Module>/<Feature>_data.<csv|json|yaml>`

6. Kết quả:
- `testing-output/reports/<yyyy-mm-dd>/<run-id>/`

Quy tắc thêm:
1. Tên thư mục trong `Projects/` phải theo nhóm chức năng/nghiệp vụ (Auth, Payment, Order...).
2. Loại test (api/ui/sit/smoke/regression) phân loại bằng tags, không phân loại bằng thư mục `Projects/`.

## Rule cho AI sinh script

1. Bắt buộc tạo mapping matrix trước khi code.
2. Mỗi expected result phải có verify step tương ứng.
3. Thiếu data hoặc môi trường: dừng và yêu cầu bổ sung.
4. Trước bàn giao phải pass DoD dạng pass/fail.
