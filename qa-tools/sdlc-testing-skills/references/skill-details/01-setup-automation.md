# Detailed Procedure: 01-setup-automation

> Token-saving archive of the previous full sub-skill body. Read only when the compact sub-skill needs exact legacy wording, templates, or edge-case procedures.

## ⚑ Kiểm tra trước khi báo DONE

- [ ] Cấu trúc 4-layer đầy đủ trong `testing-output/automation/`
- [ ] ENV_*.yaml đã tạo cho các môi trường cần thiết
- [ ] General.resource và base keyword scaffold đã có
- [ ] Append execution record vào `governance/audit-log.md`
- [ ] Cập nhật `project/session-state.yaml` → `last_execution`, `notes`

---

# Skill 00 — Setup Automation Project

## Mục đích

Tạo đầy đủ cấu trúc thư mục automation Robot Framework cho một project/module mới trong
`testing-output/automation/`, dựa trên template tại `assets/automation-template/`.

Chạy skill này **một lần duy nhất** khi bắt đầu viết automation cho project/module chưa từng có.

**Quy tắc ngôn ngữ:** Mô tả tiếng Việt có dấu. Technical terms/ID/file path không dấu.

---

## Đầu vào

| Thông tin | Bắt buộc | Tìm ở đâu |
|---|---|---|
| Tên project / mã project | ✅ | `qa-config.yaml` > `project.code` hoặc hỏi user |
| Module đầu tiên | Khuyến nghị | Hỏi user nếu không rõ |
| Tech type (ui/api/mobile/mixed) | ✅ | `qa-config.yaml` > `tools.automation` hoặc hỏi |

### Đọc qa-config trước
Nếu có `testing-output/qa-config.yaml`:
- `project.code` → ProjectName (viết hoa, ví dụ: `BTC`, `RealEstateOps`)
- `tools.automation.ui` / `tools.automation.api` → xác định framework

---

## Template source

```
assets/automation-template/
├── KeywordLibraries/CommonKeyword/    ← copy toàn bộ 7 files
├── KeywordLibraries/KeyCloak/         ← copy Api_KeyCloak_Token.resource
├── Libs/                              ← copy toàn bộ Python libs
├── Variables/ENV_*.yaml               ← copy 4 môi trường
├── .gitignore
└── requirements.txt
```

---

## Cấu trúc output

```
testing-output/automation/
├── .gitignore
├── requirements.txt
├── DataTest/
│   └── {Module}/
│       └── {feature}_data.yaml        # placeholder data file
├── KeywordLibraries/
│   ├── CommonKeyword/                 # copy từ template
│   │   ├── ApiCore.resource
│   │   ├── BrowserCore.resource
│   │   ├── CommonVariable.resource
│   │   ├── Utils.resource
│   │   ├── WebBaseLibraries.resource
│   │   ├── WebBrowserLibraries.resource
│   │   └── WebCore.resource
│   ├── KeyCloak/
│   │   └── Api_KeyCloak_Token.resource
│   └── {ProjectName}/                 # tạo mới
│       ├── HighLevelKeywords/
│       │   └── HighLevelKeywords_{Module}.resource   # scaffold
│       ├── LowLevelKeywords/
│       │   ├── UI_{Module}.resource                  # scaffold UI
│       │   ├── Api_{Module}.resource                 # scaffold API
│       │   └── NSP_UI_Utils.resource                 # copy từ template nếu UI
│       ├── VerificationKeywords/
│       │   └── VerificationKeywords_{Module}.resource # scaffold
│       └── {ProjectName}General.resource             # import hub
├── Libs/                              # copy từ template
├── Projects/
│   └── {Module}/
│       └── test_{Module}.robot        # scaffold test suite
└── Variables/
    ├── ENV_DEV.yaml                   # copy + thêm URL placeholder
    ├── ENV_QC.yaml
    ├── ENV_UAT.yaml
    └── ENV_PRD.yaml
```

---

## Nội dung scaffold các file

### `{ProjectName}General.resource`

```robot
*** Settings ***
Documentation    General resource hub cho {ProjectName}.
...              Test case chỉ cần import file này để có tất cả keywords.
...              Thêm import mới khi tạo module mới.

Resource    ../../CommonKeyword/BrowserCore.resource
Resource    ../../CommonKeyword/ApiCore.resource
Resource    ../../CommonKeyword/Utils.resource
Resource    ../../CommonKeyword/CommonVariable.resource

# === THÊM MODULE MỚI VÀO ĐÂY ===
# Resource    ../HighLevelKeywords/HighLevelKeywords_{Module}.resource
# Resource    ../VerificationKeywords/VerificationKeywords_{Module}.resource
```

### `LowLevelKeywords/UI_{Module}.resource` (scaffold)

```robot
*** Settings ***
Documentation    LowLevel UI keywords cho màn hình {Module}.
...              1 keyword = 1 action. KHÔNG dùng IF/FOR. KHÔNG có assertion nghiệp vụ.
...              Tất cả Browser.* action prefix với Browser.

Resource          ../../CommonKeyword/BrowserCore.resource

*** Keywords ***
# TODO: Thêm keyword cho từng element trên trang
# Pattern: {Action} {ElementName} on {Module} Page
#
# Ví dụ:
# Enter Ten on {Module} Page
#     [Arguments]    ${value}
#     Browser.Fill Text    [data-autoid='input-ten']    ${value}
#
# Click Button Luu on {Module} Page
#     Browser.Click    [data-autoid='btn-luu']
#
# Click Trang Thai Dropdown on {Module} Page
#     Browser.Click    [data-autoid='dropdown-trang-thai']
```

### `LowLevelKeywords/Api_{Module}.resource` (scaffold)

```robot
*** Settings ***
Documentation    LowLevel API keywords cho module {Module}.
...              Mỗi keyword call 1 API endpoint. Set RESPONSE vào test variable.
...              KHÔNG assert trong low-level.

Resource          ../../CommonKeyword/ApiCore.resource

*** Keywords ***
# TODO: Thêm keyword cho từng API endpoint
# Pattern: Api {METHOD} /v1/{path}
#
# Ví dụ:
# Api POST /v1/{module}
#     [Arguments]    ${payload}    ${token}
#     &{headers}=    Create Dictionary    Authorization=Bearer ${token}    Content-Type=application/json
#     METHOD POST    /v1/{module}    ${payload}    headers=${headers}
#     Set Test Variable    ${RESPONSE}    ${response}
#
# Api GET /v1/{module}/{id}
#     [Arguments]    ${id}    ${token}
#     &{headers}=    Create Dictionary    Authorization=Bearer ${token}
#     METHOD GET    /v1/{module}/${id}    headers=${headers}
#     Set Test Variable    ${RESPONSE}    ${response}
```

### `HighLevelKeywords/HighLevelKeywords_{Module}.resource` (scaffold)

```robot
*** Settings ***
Documentation    HighLevel keywords cho module {Module}.
...              Ghép nhiều LowLevel keywords thành 1 business flow.
...              CÓ THỂ dùng IF/FOR. KHÔNG gọi trực tiếp Browser.* hay REST.

Resource    ../LowLevelKeywords/UI_{Module}.resource
Resource    ../LowLevelKeywords/Api_{Module}.resource
Resource    ../LowLevelKeywords/NSP_UI_Utils.resource

*** Keywords ***
# TODO: Thêm keyword mô tả business flow
# Pattern: {ActionSummary} on {Module} Page
#
# Ví dụ:
# Search {Module} by Ten on {Module} Page
#     [Arguments]    ${ten}=${EMPTY}
#     Enter Ten on {Module} Page    ${ten}
#     Wait for networkidle on NSP Page
#     Wait for loading table on NSP Page
```

### `VerificationKeywords/VerificationKeywords_{Module}.resource` (scaffold)

```robot
*** Settings ***
Documentation    Verification keywords cho module {Module}.
...              Chỉ kiểm tra UI state. KHÔNG có business logic. KHÔNG gọi LowLevel.
...              Dùng Browser.Wait For Elements State hoặc Should Be Equal.

Resource    ../../CommonKeyword/BrowserCore.resource

*** Keywords ***
# TODO: Thêm verification keyword
# Pattern: Verify {Description} on {Module} Page
#
# Ví dụ:
# Verify Ten hien thi on {Module} Page
#     [Arguments]    ${ten}
#     Browser.Wait For Elements State    text=${ten}    visible    timeout=10s
#
# Verify Table is Not Empty on {Module} Page
#     Browser.Wait For Elements State    [data-autoid='table-row']    visible    timeout=10s
```

### `Projects/{Module}/test_{Module}.robot` (scaffold)

```robot
*** Settings ***
Documentation    Test suite cho module {Module} — {ProjectName}.
...              Import chỉ {ProjectName}General.resource.
...              Test case chỉ gọi HighLevel và Verification keywords.

Resource    ../../../KeywordLibraries/{ProjectName}/{ProjectName}General.resource

Suite Setup      Open Browser And Login
Suite Teardown   Close Browser

*** Variables ***
${ENV}           DEV

*** Test Cases ***
# TODO: Thêm test cases
# Pattern: TC{N}: [Positive/Negative] Mô tả test case
#
# Ví dụ:
# TC01: [Positive] Tìm kiếm thành công theo tên
#     [Tags]    smoke    regression    {module}
#     Search {Module} by Ten on {Module} Page    Nguyễn Văn A
#     Verify Ten hien thi on {Module} Page       Nguyễn Văn A

*** Keywords ***
Open Browser And Login
    # TODO: Implement login flow
    Log    Open browser và đăng nhập vào hệ thống
```

### `DataTest/{Module}/{feature}_data.yaml` (scaffold)

```yaml
# Test data cho module {Module}
# Không hardcode credential — dùng biến môi trường cho sensitive data

valid_data:
  - name: Nguyễn Văn A
    email: test.user.a@example.com
    phone: "0912345678"

invalid_data:
  - case: empty_name
    name: ""
    expected_error: Họ và tên không được để trống
  - case: invalid_email
    email: not-an-email
    expected_error: Email không hợp lệ
```

---

## Quy tắc copy file

| Hành động | Điều kiện |
|---|---|
| Copy file từ template | File chưa tồn tại trong testing-output/automation/ |
| Bỏ qua (không ghi đè) | File đã tồn tại |
| Tạo scaffold mới | File là placeholder cho module mới |
| Hỏi user | File tồn tại nhưng khác với template đáng kể |

---

## Báo cáo kết quả

```
✅ Automation khởi tạo thành công cho {ProjectName}

📁 Đã tạo:
  - testing-output/automation/KeywordLibraries/CommonKeyword/  (7 files từ template)
  - testing-output/automation/KeywordLibraries/{ProjectName}/  (scaffold mới)
  - testing-output/automation/Libs/                            (N Python libs)
  - testing-output/automation/Projects/{Module}/               (scaffold test suite)
  - testing-output/automation/Variables/ENV_*.yaml             (4 môi trường)

⚠️  Files cần cập nhật:
  1. Variables/ENV_DEV.yaml    → điền URL{PROJECT_CODE} thật
  2. Variables/ENV_QC.yaml     → điền URL{PROJECT_CODE} thật
  3. testing-output/qa-config.yaml → điền thông tin project (nếu chưa có)

🚀 Bước tiếp theo:
  Chạy Skill 06 (gen-script-test) để generate scripts từ test cases trong:
  testing-output/test-cases/functional/
```

---

## Trạng thái hoàn thành

- **DONE** — Cấu trúc đầy đủ, scaffold files tạo xong
- **DONE_WITH_CONCERNS** — Hoàn thành nhưng có file không copy được (ghi rõ)
- **NEEDS_CONTEXT** — Thiếu: tên project / qa-config.yaml
- **SKIPPED** — testing-output/automation/ đã có đầy đủ cấu trúc, không cần init lại
