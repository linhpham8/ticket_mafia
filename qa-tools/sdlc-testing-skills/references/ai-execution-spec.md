# AI Execution Spec (Automation Script)

Mục tiêu: Bản ngắn bắt buộc dùng khi yêu cầu AI sinh automation script.

## 1. 10 luật bắt buộc

1. Theo kiến trúc 4 lớp.
2. Test case không gọi trực tiếp low-level/libraries.
3. Không SQL trực tiếp trong test case.
4. Low-level không assert nghiệp vụ.
5. Mỗi expected result có verify tương ứng.
6. Không hardcode URL, token, credential, secret.
7. Dữ liệu dùng từ file DataTest.
8. UI dùng Browser/Playwright và wait thay sleep.
9. Output path phải đúng chuẩn.
10. Trước bàn giao phải pass DoD checkbox.

Phạm vi test level:
1. component
2. integration
3. e2e

Ghi chú:
- Unit test nằm ngoài phạm vi skill suite này (thuộc dev workflow).

## 2. Quy ước đầu vào

1. Bộ test case nguồn: Functional hoặc SIT.
2. Metadata: module, loại test, ưu tiên, môi trường.
3. Dữ liệu test: input, expected, setup/cleanup.

## 3. Quy ước đầu ra

1. Test suite Robot:
- testing-output/automation/Projects/<NhomChucNang>/<Feature>_<Kenh>.robot
2. High-level keywords:
- testing-output/automation/KeywordLibraries/<Module>/HighLevelKeywords/<Module>_High.resource
3. Low-level keywords:
- testing-output/automation/KeywordLibraries/<Module>/LowLevelKeywords/<Module>_Low.resource
4. Verification keywords:
- testing-output/automation/KeywordLibraries/<Module>/VerificationKeywords/<Module>_Verification.resource
5. Data file:
- testing-output/automation/DataTest/<Module>/<Feature>_data.<csv|json|yaml>
6. Nếu cần: ENV file mới:
- testing-output/automation/Variables/ENV_<ENV>.yaml

Quy tắc:
1. Thư mục trong Projects phải theo nhóm chức năng/nghiệp vụ (Auth, Payment, Order...).
2. Loại test (api/ui/sit/smoke/regression) phân loại bằng tags, không phân loại bằng tên thư mục Projects.

## 4. Mẫu mapping matrix

| TC nguồn | Loại | Test Level | Tiền điều kiện | Bước nghiệp vụ | Kết quả mong đợi | File test suite | High-level keyword | Low-level keyword | Dữ liệu dùng | Môi trường |
|---|---|---|---|---|---|---|---|---|---|---|
| FUNC_LOGIN_01 | Functional | e2e | User active | Đăng nhập hợp lệ | Vào Dashboard | testing-output/automation/Projects/Auth/Login_UI.robot | Login With Valid User | Ui Input Username, Ui Click Login | testing-output/automation/DataTest/Auth/login_valid.csv | DEV, QC |

## 5. DoD pass/fail

- [ ] Có mapping matrix đầy đủ.
- [ ] Mỗi dòng mapping có Test Level (component/integration/e2e).
- [ ] Có đủ file theo output path chuẩn.
- [ ] Không hardcode dữ liệu nhạy cảm.
- [ ] Test case không gọi low-level/libraries trực tiếp.
- [ ] Low-level không assert nghiệp vụ.
- [ ] Có tags smoke/regression/module.
- [ ] UI không dùng sleep cố định.
- [ ] Có data file tách riêng.
- [ ] Dùng ENV config thay URL cố định.
- [ ] Smoke path chạy được ở ít nhất 1 môi trường.

Nếu còn bất kỳ mục nào chưa tick thì trạng thái là FAIL.
