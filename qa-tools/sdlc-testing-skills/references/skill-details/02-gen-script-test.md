# Detailed Procedure: 02-gen-script-test

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

> ⚠️ **L2 — Dev + QA Lead review bắt buộc.** Script chưa được merge/chạy CI cho đến khi nhận "Approved". Xem mục Sign-off cuối file.

- [ ] Script tuân thủ 4-layer: TC chỉ gọi HighLevel keyword, không gọi Browser.* trực tiếp
- [ ] Không hardcode URL, credential, secret — tất cả từ ENV_*.yaml
- [ ] Data test lấy từ DataTest file, không inline trong script
- [ ] Dùng `Browser.Wait For Elements State`, không dùng Sleep
- [ ] Sign-off L2 đã emit (Dev + QA Lead)
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `pending_sign_offs`

---

# Skill 06 — Gen Script Test

## Quick Reference

| | |
|---|---|
| **Input bắt buộc** | TC file (TSV/MD) đã approve từ skill 05/06/07 |
| **Input khuyến nghị** | qa-config.yaml + test data từ skill 08 |
| **Output** | .robot / .py / .ts / .java files sẵn CI |
| **Framework mặc định** | Robot Framework (nếu không specify) |
| **Điều kiện tiên quyết** | qa-automation/01 (setup-automation) đã chạy lần đầu |
| **Time estimate** | 15–30 phút / TC (phụ thuộc độ phức tạp) |
| **Sign-off** | L2 — Dev + QA Lead review script trước khi merge |

> **Token optimization:** Nếu chỉ gen script cho 1-3 TC, AI có thể gen trực tiếp từ TC content mà không cần đọc toàn bộ skill file. Đọc đầy đủ khi gen script cho cả module hoặc cần setup keyword mới.

---

## Tài liệu bắt buộc phải đọc trước khi sinh script

1. `references/ai-execution-spec.md` (bắt buộc — mọi framework)
2. `references/rf-keyword-convention.md` (bắt buộc — khi framework là Robot Framework)
3. `references/automation-framework-policy.md` (tham chiếu khi cần)

Nếu chưa đọc `ai-execution-spec.md` thì không được bắt đầu sinh code.
Nếu framework là Robot Framework và chưa đọc `rf-keyword-convention.md` thì không được sinh keyword.
Nếu thiếu file tham chiếu bắt buộc trong repo hiện tại thì trả `NEEDS_CONTEXT`, nêu rõ file thiếu và yêu cầu user cung cấp hoặc xác nhận dùng fallback.

## Đầu vào

| Thông tin | Bắt buộc |
|---|---|
| Danh sách TC cần automation (STT hoặc file) | ✅ |
| Tech stack / framework | ✅ nếu chưa có `qa-config.yaml` |
| Base URL / API endpoint | ✅ nếu chưa có `qa-config.yaml` |
| Auth mechanism (Bearer, API Key, Session...) | ✅ nếu chưa có `qa-config.yaml` |
| Data test (từ skill 08 — qa-core/08-gen-data-test — hoặc cung cấp trực tiếp) | Khuyến nghị |

Nếu project có `qa-config.yaml` → đọc các field sau trước, không hỏi lại (ưu tiên hơn input người dùng):

| Field | Dùng cho |
|---|---|
| `tools.automation.ui` | Danh sách framework UI (playwright/cypress/selenium/robotframework) |
| `tools.automation.api` | Danh sách framework API (pytest/restassured/postman-newman/robotframework) |
| `environments.staging.url` | Base URL mặc định |
| `environments.staging.auth_required` | Có cần setup auth không |
| `test_accounts` | Accounts dùng trong beforeAll / fixture |
| `automation_rules.test_level_policy` | Rule mapping test level: component/integration/e2e |

Nếu chưa có config → hỏi user về tech stack và base URL trước khi gen.

Quy tắc fallback khi không có `qa-config.yaml`:
- Dùng thông tin user cung cấp trực tiếp làm nguồn chính.
- Nếu thiếu framework cụ thể, mặc định đề xuất Robot Framework và chờ user xác nhận trước khi sinh script.

Nếu thiếu một trong các mục sau thì trả **NEEDS_CONTEXT** và dừng:
1. Danh sách test case nguồn (Functional hoặc SIT)
2. Module/feature
3. Môi trường mục tiêu
4. Dữ liệu test hoặc quy tắc setup/cleanup
5. Test Level cho từng TC (hoặc policy đủ để suy ra level)

## Quy tắc chọn TC và xử lý ưu tiên

### Quy tắc 1 — Ưu tiên TC có đánh dấu automation

Nếu user không chỉ định cụ thể TC nào cần gen script:
- Ưu tiên nhặt các TC từ file Functional (`testing-output/test-cases/functional/`) **và** SIT (`testing-output/test-cases/sit/`) có cột `Auto=Y` (hoặc tương đương).
- Không tự nhặt TC có `Auto=N` trừ khi user yêu cầu rõ.
- Nếu không có TC nào có `Auto=Y` → báo user và hỏi có muốn gen cho toàn bộ TC không trước khi tiếp tục.

### Quy tắc 2 — Làm theo chỉ định của user

Nếu user chỉ định rõ (danh sách TC theo STT, nhóm rule, module, file cụ thể, hoặc bất kỳ phạm vi nào):
- Làm đúng theo chỉ định đó — không áp đè bằng Quy tắc 1.
- Không tự thêm hoặc bỏ TC ngoài phạm vi user đã chỉ định.
- Nếu TC user chỉ định có `Auto=N`, vẫn gen nhưng ghi chú trong mapping matrix.

### Quy tắc 3 — Hỏi lại khi thiếu thông tin cấu hình

Khi thiếu bất kỳ thông tin bắt buộc nào dưới đây mà `qa-config.yaml` không cung cấp:
- **API endpoint / domain**: hỏi rõ URL base và path cụ thể của module cần test.
- **Tài khoản test**: hỏi username/role cần dùng (không hỏi password — yêu cầu user inject qua env var hoặc secrets).
- **Auth mechanism**: hỏi loại auth (Bearer token, API key, session cookie) và cách lấy token.
- **DB / environment**: hỏi môi trường đích (staging/UAT) nếu chưa rõ.

**Không được tự giả định giá trị cho các thông tin trên.** Liệt kê rõ từng mục còn thiếu và hỏi user trước khi sinh bất kỳ dòng code nào.

## Framework được hỗ trợ

> **Ưu tiên chính: Robot Framework** — dùng unified API + UI automation (keyword-driven, dễ maintain, phù hợp QA)

| Framework | Ngôn ngữ | Phù hợp với | Ghi chú |
|---|---|---|---|
| **Robot Framework** | Python | UI, API, E2E (unified) | ✅ **Ưu tiên — cả API + UI trong 1 framework** |
| Playwright | JS / TS | UI E2E, API | UI-focus, API kém hơn Robot |
| Pytest + Requests | Python | API, Backend | API-only |
| RestAssured | Java | API, Spring Boot | API-only, Java-specific |
| Cypress | JS | UI E2E, Component | UI-only, JavaScript |
| k6 | JS | Performance script độc lập | Skill 11 dùng JMeter mặc định; k6 script gen tự do nhưng không có template tích hợp trong skill 11 |

**Phạm vi mobile native:**
- ✅ Hỗ trợ Robot Framework + AppiumLibrary cho Android/iOS native app.
- Khi test type là mobile, bắt buộc đọc thêm phần **Mobile Appium** bên dưới.
- Mobile web/PWA chạy trên browser → vẫn dùng Browser library (Playwright) bình thường.

---

## Mobile Appium — Quy tắc bổ sung

Áp dụng khi `tools.automation.mobile` có trong qa-config hoặc user yêu cầu test mobile native.

### Import và Setup

```robot
*** Settings ***
Library    AppiumLibrary    run_on_failure=AppiumLibrary.Capture Page Screenshot
Library    ../../Libs/ScrollAppMoblie.py         # Android scroll
Library    ../../Libs/ScrollIOSMoblie.py          # iOS scroll
```

### Capabilities — đọc từ `Variables/CONFIG_MOBILE.yaml`

```yaml
# CONFIG_MOBILE.yaml — KHÔNG hardcode trong test
PLATFORM_NAME:     Android                        # hoặc iOS
APP_PACKAGE:       com.example.app
APP_ACTIVITY:      .MainActivity
DEVICE_NAME:       emulator-5554
APPIUM_URL:        http://localhost:4723/wd/hub
```

### Locator Priority (Mobile)

1. `accessibility_id=element-accessibility-id` ← ưu tiên nhất
2. `id=com.package.name:id/element_id`
3. `xpath=//android.widget.Button[@text='Đăng nhập']`
4. `class chain` / `predicate string` (iOS)

### LowLevel Mobile Keywords — pattern

```robot
*** Keywords ***
Tap Button Ten on TenTrang Screen
    [Documentation]    Nhấn button Ten trên màn hình TenTrang
    Wait Until Element Is Visible    accessibility_id=ten-button    timeout=10s
    Click Element    accessibility_id=ten-button

Enter Text Ten on TenTrang Screen
    [Arguments]    ${value}
    Wait Until Element Is Visible    id=com.package:id/input_ten    timeout=10s
    Clear Text    id=com.package:id/input_ten
    Input Text    id=com.package:id/input_ten    ${value}

Swipe Up to Find More on TenTrang Screen
    Scroll Down    0.5    0.2    500        # dùng ScrollAppMoblie.py
```

### HighLevel Mobile Keywords — pattern

```robot
*** Keywords ***
Login with valid credentials on Login Screen
    [Arguments]    ${username}    ${password}
    Tap Button Dang Nhap on Login Screen
    Enter Text Username on Login Screen    ${username}
    Enter Text Password on Login Screen    ${password}
    Tap Button Xac Nhan on Login Screen
    Wait Until Element Is Visible    accessibility_id=home-screen    timeout=15s
```

### Suite Setup/Teardown Mobile

```robot
*** Settings ***
Suite Setup       Open Mobile Application
Suite Teardown    Close All Applications

*** Keywords ***
Open Mobile Application
    Open Application    ${APPIUM_URL}
    ...    platformName=${PLATFORM_NAME}
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    automationName=UiAutomator2
    ...    noReset=False
```

### Output path Mobile

```
testing-output/automation/
├── Projects/{Module}/
│   └── test_{Module}_Mobile.robot
├── KeywordLibraries/{Module}/
│   ├── LowLevelKeywords/
│   │   └── Mobile_{Module}.resource        # Mobile LowLevel
│   ├── HighLevelKeywords/
│   │   └── HighLevelKeywords_{Module}.resource
│   └── VerificationKeywords/
│       └── VerificationKeywords_{Module}.resource
└── Variables/
    └── CONFIG_MOBILE.yaml                  # capabilities per env
```

### DoD bổ sung cho Mobile

- [ ] Capabilities lấy từ `CONFIG_MOBILE.yaml` — KHÔNG hardcode
- [ ] Wait Until Element Is Visible thay cho Sleep
- [ ] Scroll dùng `ScrollAppMoblie.py` (Android) hoặc `ScrollIOSMoblie.py` (iOS)
- [ ] `AppiumLibrary.Capture Page Screenshot` cho `run_on_failure`
- [ ] Mỗi test reset app state qua `noReset=False` hoặc cleanup keyword
- [ ] Tag `mobile` và `android`/`ios` cho từng test case

---

## Nguyên tắc sinh code

- **Page Object Model** cho UI test — tách locator ra khỏi test logic
- **Assertion rõ ràng** — không dùng `expect(true).toBe(true)`
- **Data-driven** — đọc data từ file/fixture, không hardcode trong test
- **CI-ready** — chạy được với `npm test` / `pytest` / `mvn test` không cần config thêm
- **Cleanup** — mỗi test tự cleanup data sau khi chạy (`afterEach` / `teardown`)
- **Độc lập** — test không phụ thuộc thứ tự chạy với test khác
- **Mô tả rõ** — `describe` / `it` / `test name` phản ánh đúng kịch bản TC

## Chuẩn AI-first bắt buộc

Trước khi sinh code phải tạo **mapping matrix**.

Khi trả kết quả phải có đúng 3 phần:
1. Mapping matrix (TC nguồn -> script)
2. Danh sách file output theo path chuẩn
3. DoD pass/fail checklist

Không có mapping matrix thì không sinh script.

## Cấu trúc thư mục output

**Lưu vào:** `output_paths.automation` từ qa-config (default: `testing-output/automation/`)

```
testing-output/automation/
├── fixtures/          # test data files (JSON/CSV)
│   └── {feature}.json
├── pages/             # Page Objects (UI — Playwright/Cypress)
│   └── {PageName}.ts
├── specs/             # test files (Playwright/Cypress)
│   └── {feature}.spec.ts
├── robot/             # Robot Framework suites
│   ├── {feature}.robot
│   └── resources/{feature}-keywords.resource
├── tests/api/         # API tests (Pytest)
│   └── test_{feature}.py
└── helpers/           # utils, auth setup
    └── auth.ts
```

Trong project dùng kiến trúc chuẩn Robot Framework, ưu tiên output path sau:

1. `testing-output/automation/Projects/<NhomChucNang>/<Feature>_<Kenh>.robot`
2. `testing-output/automation/KeywordLibraries/<Module>/HighLevelKeywords/<Module>_High.resource`
3. `testing-output/automation/KeywordLibraries/<Module>/LowLevelKeywords/<Module>_Low.resource`
4. `testing-output/automation/KeywordLibraries/<Module>/VerificationKeywords/<Module>_Verification.resource`
5. `testing-output/automation/DataTest/<Module>/<Feature>_data.<csv|json|yaml>`

Quy tắc phân nhóm:
- Dùng thư mục Projects theo nhóm chức năng/nghiệp vụ (Auth, Payment, Order, Search...).
- Phân loại test theo loại (api/ui/sit/smoke/regression) bằng Tags, không dùng thư mục Projects để phân loại.

## Checklist trước khi xuất

- [ ] Code chạy được với lệnh mặc định của framework
- [ ] Có `beforeAll` / `afterEach` setup và teardown
- [ ] Assertion đủ cụ thể (status code, response body, UI element)
- [ ] Không hardcode credential — dùng `process.env` hoặc fixture
- [ ] Comment giải thích bước phức tạp
- [ ] Ghi rõ version dependency trong comment đầu file

## Output format cố định

### 1) Mapping Matrix

| TC nguồn | Loại | Test Level | Tiền điều kiện | Bước nghiệp vụ | Kết quả mong đợi | File test suite | High-level keyword | Low-level keyword | Dữ liệu dùng | Môi trường |
|---|---|---|---|---|---|---|---|---|---|---|

### 2) File Output Plan

- `<path 1>`
- `<path 2>`
- `<path 3>`

### 3) DoD Pass/Fail

**Chung (mọi framework):**
- [ ] Đã map đầy đủ TC nguồn sang script
- [ ] Mỗi dòng mapping có Test Level (component/integration/e2e)
- [ ] Đúng output path chuẩn
- [ ] Không hardcode dữ liệu nhạy cảm
- [ ] Có tags smoke/regression/module
- [ ] Có data file tách riêng
- [ ] Dùng env config thay URL cố định
- [ ] Smoke path chạy được trên ít nhất 1 môi trường

**Robot Framework — bổ sung (đọc `references/rf-keyword-convention.md`):**
- [ ] Keyword đặt tên đúng convention từng layer (Low/High/Verification)
- [ ] LowLevel mỗi keyword chỉ có 1 action — không chứa logic IF/FOR
- [ ] HighLevel ghép Low thành luồng nghiệp vụ — không gọi trực tiếp Browser.*
- [ ] VerificationKeywords chỉ dùng `Browser.Wait For Elements State` — không assert nghiệp vụ
- [ ] File header có `Documentation` + `Author` đúng format
- [ ] Locator ưu tiên `data-autoid` → chain (`>>`) → id → xpath → css → text
- [ ] Không dùng Sleep — thay bằng `Browser.Wait For Elements State` hoặc `Wait For Load State`
- [ ] General resource file được cập nhật import module mới
- [ ] Test case chỉ import General resource (không import trực tiếp Low/High/Verification)

Trạng thái: `PASS` hoặc `FAIL`

## CI/CD integration guidance (mức cơ bản)

Mục tiêu của output là CI-ready. Nếu project yêu cầu tích hợp cụ thể, thêm 1 file mẫu theo hệ thống CI hiện có:

- **GitHub Actions**: `.github/workflows/test-automation.yml`
- **GitLab CI**: `.gitlab-ci.yml`
- **Jenkins**: `Jenkinsfile`

Checklist tối thiểu cho CI:
1. Cài dependency + cache (npm/pip/maven)
2. Inject biến môi trường (`BASE_URL`, token, secret) qua secret store của CI
3. Chạy test command mặc định theo framework
4. Xuất artifact report (junit/html/log) để truy vết

Nếu user chưa yêu cầu pipeline cụ thể, chỉ ghi mục này như guidance; không tự tạo file CI chi tiết.

---

## Sign-off Request (L2)

```
---
⏳ SIGN-OFF REQUEST — qa-automation/02-gen-script-test (Level 2 — Dev + QA Lead)
Người review Dev: [team.dev_lead từ qa-config]
Người review QA: [team.qc_lead từ qa-config]
SLA: 24 giờ
Output: testing-output/automation/Projects/.../*.robot
Checklist review: Script chạy được, 4-layer compliance, không hardcode secret
Action: Reply "Approved" hoặc "Cần fix: [nội dung]"
---
```

Sau khi nhận Approved → cập nhật `project/session-state.yaml`: xóa item khỏi `pending_sign_offs`.

---

## Completion Status

- **DONE** — Script chạy được với lệnh mặc định, có setup/teardown, assertion đủ cụ thể, không hardcode credential
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng: {Một số TC phức tạp chưa automation được / Thiếu data fixture / CI config cần điều chỉnh thêm}
- **BLOCKED** — Không thể gen do: {Thiếu tech stack xác nhận / Không có base URL / Auth mechanism chưa rõ}
- **NEEDS_CONTEXT** — Cần bổ sung: {Danh sách TC cần automation / Framework sử dụng / Base URL và auth mechanism}
