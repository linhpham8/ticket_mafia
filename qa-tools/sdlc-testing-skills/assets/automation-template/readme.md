# Mẫu Dự Án Automation Robot Framework

## Giới thiệu

Bộ khung này cung cấp **công cụ tự động hoá đa năng** cho:
- Kiểm thử UI Web bằng **SeleniumLibrary** hoặc **Browser (Playwright)**
- Kiểm thử API bằng **RESTinstance**
- Kiểm thử Mobile bằng **AppiumLibrary**

Mục tiêu là tạo một **cấu trúc dự án mẫu** chuẩn, dễ mở rộng và có sẵn các file resource mẫu cho từng công nghệ.

---STT	Summary	Test Level	Precondition	Test Data	Step summary	Expected result	Priority
EH-123 Nghỉ tang chế							
TC-001	[EH-123][AC1][BasicFlow] Verify luồng E2E tạo + duyệt + auto-confirm Nghỉ tang chế	e2e	"- CBNV VB PERNR=800110 (hoặc VE — BA chốt VE eligible)
- QLTT đăng nhập riêng để duyệt
- EH-113 định mức tang chế còn >= 3 ngày"	"PERNR=800110 (VB)
Loại Leave='Nghỉ tang chế'
Khoảng nghỉ: 20/05/2026 → 22/05/2026 (3 ngày = max)
Người phê duyệt=QLTT mặc định
Lý do='Tang chế gia đình', Comment='Tang chế ông nội'"	"1. Login CBNV PERNR=800110
2. Mở Homepage → tap module 'Nghỉ phép'
3. Tap 'Nghỉ tang chế'
4. Chọn khoảng nghỉ 20/05-22/05 (3 ngày max)
5. Nhập Lý do, Comment, chọn Người phê duyệt
6. Tap 'Gửi yêu cầu'
7. Logout, login QLTT
8. Mở pending list, tap 'Duyệt đồng ý'
9. Đợi auto-confirm
10. Verify SAP push mã PN03"	"- B6: state=Pending; CBNV nhận in-app notification
- B8: state=Approved (1 cấp đủ vì 3<10 ngày)
- B9: state=Confirmed
- B10: SAP có record mã PN03-Nghỉ việc riêng (hiếu, hỉ) với PERNR + khoảng nghỉ"	High
TC-002	[EH-123][AC1][Display] Verify form 'Nghỉ tang chế' hiển thị 6 fields	component	CBNV VA/VB/VE đăng nhập	"PERNR=800110
Form không submit, chỉ kiểm tra cấu trúc"	"1. Mở Nghỉ phép
2. Tap 'Nghỉ tang chế' để mở form
3. Đếm và verify từng field"	"- 6 fields hiển thị:
  Loại Leave (Dropdown, R, default 'Nghỉ tang chế')
  Nghỉ tang chế (Date picker, default current_date, min 0.5 ngày block 4h, max 3 ngày)
  Người phê duyệt (Dropdown, R, default theo EH-112)
  Định mức ngày nghỉ (Number readonly từ EH-113)
  Lý do (Dropdown, R)
  Comment (Text 500 ký tự, R)"	High
TC-003	[EH-123][AC2][Decision] Verify HĐLĐ — VA, VB, VE eligible (BA override 2026-05-14)	component	8 CBNV với 8 loại HĐLĐ khác nhau	"[Case-VA] HĐLĐ XĐ thời hạn → visible
[Case-VB] HĐLĐ KXĐ thời hạn → visible
[Case-VE] HĐ thử việc → visible (BA chốt 2026-05-14 override Req gốc 'không thử việc')
[Case-VC] HĐLĐ mùa vụ → NOT visible (HĐ dịch vụ)
[Case-VD] Tập nghề → NOT visible
[Case-VF/VG/VH] HĐDV → NOT visible"	"1. Login lần lượt từng CBNV theo HĐLĐ
2. Mở Nghỉ phép
3. Mở dropdown Loại Leave
4. Verify visibility 'Nghỉ tang chế'"	"- VA, VB, VE: 'Nghỉ tang chế' visible (BA override Req gốc)
- VC, VD, VF, VG, VH (HĐ dịch vụ): NOT visible
- Đồng nhất LEAVE_MODULE_SUMMARY.md v1.1"	High
TC-004	[EH-123][BR][BVA] Verify min 0.5 ngày + max 3 ngày	component	"- CBNV VB
- Ca hành chính 8:00-17:00"	"PERNR=800110
[BVA-min-eq] Khoảng = 4h từ 8:00-12:00 → accept
[BVA-min-1] Khoảng = 3h59 → reject
[BVA-1d] Khoảng = 1 ngày full → accept
[BVA-max-eq] Khoảng = 3 ngày → accept
[BVA-max+1] Khoảng = 4 ngày → reject 'Tối đa 3 ngày'
[BVA-half-day] Khoảng = 0.5 ngày → accept"	"1. Submit từng case
2. Verify validate"	"- BVA-min-eq, BVA-1d, BVA-max-eq, BVA-half-day: accept
- BVA-min-1: error 'Tối thiểu 0.5 ngày'
- BVA-max+1: error 'Tối đa 3 ngày'"	High
TC-005	[EH-123][BR][CornerCase] Verify cảnh báo log vào ngày nghỉ/lễ tết	component	"- Có lễ 30/04, 01/05/2026
- Có CN trong khoảng test
- 'Loại trừ' = 'Có' (Req:32)"	"PERNR=800110
[Case-có-lễ] Khoảng = 30/04-02/05 (chứa lễ + CN)
[Case-có-CN] Khoảng = 17/05 (CN duy nhất)
[Case-không-lễ] Khoảng = 19/05-21/05 (T2-T4 thường)"	"1. Submit từng case
2. Quan sát warning popup"	"- Case-có-lễ, Case-có-CN: hiển thị cảnh báo 'Khoảng nghỉ chứa ngày lễ/cuối tuần'; vẫn cho submit nếu user confirm
- Case-không-lễ: submit OK không cảnh báo"	Medium
TC-006	[EH-123][AC2.Function][Decision] Verify cấp duyệt — vì max 3 ngày → luôn 1 cấp QLTT	component	"- CBNV VB
- Khoảng max = 3 ngày (cap theo BR)"	"PERNR=800110
Khoảng = 3 ngày (= max)"	"1. CBNV submit request 3 ngày
2. QLTT mở pending list, tap 'Duyệt đồng ý'
3. Verify state Approved
4. Verify KHÔNG có cấp 2/3 yêu cầu duyệt"	"- 1 cấp đủ Approve (vì max 3 < 10 ngày)
- BVA cấp 2 (>=10 ngày) và cấp 3 (>=30 ngày) KHÔNG áp dụng cho EH-123 do bị cap 3 ngày
- KHÔNG có cấp 2/3 trong pending list"	High
TC-007	[EH-123][AC3][StateTransition] Verify Gửi/Duyệt/Từ chối + SAP push PN03	integration	—	"PERNR=800110
[Case-approve] Khoảng 3 ngày → approved → SAP PN03
[Case-reject] Khoảng 3 ngày → QLTT từ chối với lý do → no SAP"	"1. Test Case-approve:
   1.1 CBNV submit
   1.2 QLTT duyệt
   1.3 Đợi auto-confirm
   1.4 Verify SAP PN03
2. Test Case-reject:
   2.1 CBNV submit
   2.2 QLTT từ chối với lý do 'Trùng kế hoạch dự án'
   2.3 Verify state Rejected, no SAP"	"- Case-approve: state chain Pending → Approved → Confirmed; SAP có record mã PN03
- Case-reject: state Pending → Rejected; KHÔNG có SAP push; CBNV nhận notification kèm lý do"	High
TC-008	[EH-123][CornerCase] Verify backdate kỳ hiện tại + trước (TBD) + KHÔNG vắt năm	component	Hôm nay = 14/05/2026	"PERNR=800110
[Case-current] Khoảng bắt đầu 10/05 → accept
[Case-prev] Khoảng bắt đầu 20/04 → accept
[Case-old] Khoảng bắt đầu 10/03 → reject
[Case-cross-year] 28/12/2025-30/12/2025 (vắt sang 01/01/2026) → reject"	"1. Submit từng case
2. Verify validate"	"- Case-current, Case-prev: accept
- Case-old: reject 'Vượt kỳ backdate'
- Case-cross-year: reject 'Không cho phép log vắt năm'"	Medium
TC-009	[EH-123][Impact] Verify EH-113 định mức cập nhật 'Đã sử dụng' sau Confirmed (KHÔNG impact EH-93 quỹ)	integration	"- Trước Confirmed: EH-113 'Đã sử dụng'=0
- Request 3 ngày đã Confirmed
- EH-93 (5 quỹ thông thường) KHÔNG bị thay đổi vì Tang chế không trong 5 quỹ"	"PERNR=800110
Khoảng = 3 ngày, đã Confirmed"	"1. Snapshot EH-113 + EH-93 trước
2. Confirm request (qua TC-007 Case-approve)
3. Snapshot sau"	"- EH-113 'Đã sử dụng'+=3
- EH-93 (5 quỹ) KHÔNG thay đổi (Tang chế không trong 5 quỹ này)
- Field 'Định mức' trong form Tang chế phản ánh số mới khi mở lại"	High
TC-010	[EH-123][CornerCase] Verify SAP push fail → idempotency	integration	Mock SAP EH-35 trả 500	"PERNR=800110
Request Approved 3 ngày"	"1. CBNV submit + QLTT duyệt → Approved
2. Mock SAP fail
3. Trigger auto-confirm
4. Verify state KHÔNG chuyển Confirmed
5. Mock SAP recovery
6. Trigger retry
7. Verify state + SAP records"	"- B4: state giữ Approved
- B7: state Confirmed sau retry; SAP có 1 record duy nhất
- Đồng bộ Q8 leave-business-flow"	High
TC-011	[EH-123][AC1][BVA] Verify Comment 500	component	—	"PERNR=800110
[BVA-eq] 500 ký tự
[BVA-over] 501 ký tự
[BVA-empty] '' (rỗng)"	"1. Nhập Comment từng case
2. Submit"	"- BVA-eq: OK
- BVA-over: error 'Tối đa 500 ký tự' hoặc auto-truncate (cần BA confirm)
- BVA-empty: error 'Comment bắt buộc'"	Medium
TC-012	[EH-123][AC1.Function] Verify filter + xóa người phê duyệt	component	Dropdown người phê duyệt mở	"[Case-mã] Search PERNR
[Case-tên] Search tên 'Nguyễn'
[Case-empty] Search rỗng
[Case-xóa] Tap X bên người đã chọn"	"1. Mở dropdown
2. Test 4 case search
3. Chọn người + tap X xóa
4. Verify field reset"	"- Case-mã/tên: filter đúng
- Case-empty: hiển thị danh sách mặc định
- Case-xóa: field về empty"	Medium
TC-013	[EH-123][CornerCase] Verify multi request cùng năm — limit số lần	component	CBNV PERNR=800110 đã có 1 request Tang chế Confirmed năm 2026 (3 ngày)	"PERNR=800110
[Case-2nd-trong-năm] Submit lần 2 cùng năm với khoảng 3 ngày"	"1. Submit request lần 2 trong cùng năm
2. Verify validate"	"- Cần BA confirm rule: có giới hạn số lần Tang chế/năm không (vd: 3 lần/năm)
- Default behavior: cho submit, validate qua EH-113 định mức (nếu định mức cộng dồn)
- Hoặc reject nếu BA spec strict limit"	Low
TC-014	[EH-123][Regression] Verify không ảnh hưởng pending khác	component	CBNV PERNR=800110 có 2 pending requests loại khác (WFH, Đi trễ)	"PERNR=800110
Khoảng tang chế = 3 ngày"	"1. Snapshot 2 pending khác
2. Submit + duyệt request Tang chế
3. Verify pending cũ"	- Pending cũ giữ nguyên state	Medium
TC-015	[EH-123][Non-Functional][Security] Verify cross-PERNR	component	Endpoint POST /v1/leave-request	"[Case-no-token] No Authorization
[Case-cross-create] PERNR_caller=800110, body PERNR=800111
[Case-self-approve] CBNV submit + tự duyệt request mình"	"1. Gửi từng case qua API
2. Verify response status code"	"- Case-no-token: HTTP 401
- Case-cross-create: HTTP 403 hoặc auto-override theo token
- Case-self-approve: HTTP 403"	High
TC-016	[EH-123][Checklist-Based][Mobile] Verify form trên iPhone SE 4.7\" + Layout/Color/Objects	e2e	Device iPhone SE 4.7\"	"PERNR=800110
Test toàn form"	"1. Mở app trên iPhone SE
2. Tap Nghỉ phép → 'Nghỉ tang chế'
3. Test Date picker, dropdown
4. Quan sát layout, color, touch target"	"- Form visible đầy đủ trên SE
- Date picker không overflow
- Touch target nút Submit + X xóa >= 44x44pt
- Color contrast WCAG AA >= 4.5:1"	Low
[Exploratory Testing]	[EH-123] Charter: BA override Req gốc 'không thử việc' → verify VE thật sự eligible end-to-end	"- CBNV VE thử việc thực sự đăng nhập
- Test full flow Tang chế"	"Tự do:
- Login VE
- Verify visibility 'Nghỉ tang chế' trong dropdown
- Submit form
- Verify QLTT duyệt được
- Verify SAP push thành công với flag VE
- Test edge case CBNV vừa kết thúc HĐ thử việc trong khi pending"	"Tự do:
- VE eligibility BA override
- SAP behavior với VE flag
- Edge case khi VE chuyển sang chính thức giữa pending"	"Ghi chú:
- VE eligibility BA override
- HĐ status change race
Time-box: 30 phút"	High	"EH-123
LEAVE_MODULE_SUMMARY.md v1.1"

## Cấu trúc thư mục thực tế

```
robot-base-autotest/
│
├─ .git/                     # Lịch sử Git
├─ .gitlab-ci.yml           # CI/CD (GitLab)
├─ .vscode/                  # Cấu hình VSCode
├─ DataTest/                 # Dữ liệu test (CSV, JSON, …)
├─ ExternalSystem/           # Mock / wrapper cho hệ thống bên ngoài
├─ KeywordLibraries/        # Thư viện từ khóa Robot Framework
│   ├─ CommonKeyword/        # Các keyword chung cho Web, API, Mobile
│   │   ├─ ApiCore.resource
│   │   ├─ BrowserCore.resource
│   │   ├─ CommonVariable.resource
│   │   ├─ Utils.resource
│   │   ├─ WebBaseLibraries.resource
│   │   ├─ WebBrowserLibraries.resource
│   │   └─ WebCore.resource
│   ├─ KeyCloak/            # Keyword liên quan đến KeyCloak (auth)
│   └─ RealEstateOps/       # Keyword cho nghiệp vụ bất động sản(ví dụ)
├─ Libs/                     # Thư viện Python hỗ trợ (helpers, utils)
├─ Projects/                 # Các dự án con / suite lớn
├─ Report/                   # Báo cáo kết quả (HTML, XML)
├─ Variables/                # Biến toàn cục (URL, credentials, env)
│   └─ *.yaml                # Định nghĩa biến dưới dạng YAML
│
├─ .gitignore                # Các file/dir bỏ qua Git
├─ quick_*.bat               # Script batch tiện lợi để chạy nhanh
├─ project.test.js           # Ví dụ test JavaScript (không bắt buộc)
├─ requirements.txt          # Phụ thuộc Python
├─ readme.md                # <‑‑ Tài liệu dự án (bạn đang đọc)
└─ results/                 # Thư mục lưu kết quả chạy test
```

## Yêu cầu môi trường

1. **Python 3.9+**
2. **Node.js** (cần cho Browser/Playwright)
3. **Java 11+** (tùy chọn, nếu muốn dùng Selenium Java bindings)
4. **Android/iOS SDK** (đối với Appium)
5. Trình duyệt Chrome / Firefox / Edge (đối với Selenium)

## Cài đặt

```bat
:: Clone repository
git clone https://gitlab.id.vin/qc/robot-base-autotest.git
cd robot-base-autotest

:: Tạo môi trường ảo Python - Tùy chọn nếu - hoặc dùng bản cài mặc định
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

:: Cài đặt Playwright browsers (chỉ cần nếu dùng Browser library)
rfbrowser init   :: tải về các trình duyệt Playwright tự động
```

> **Mẹo**: `requirements.txt` đã bao gồm các package:
> `robotframework`, `robotframework-seleniumlibrary`, `robotframework-browser`, `restinstance`, `robotframework-appiumlibrary`.

## Chạy test

```bat
:: Chạy toàn bộ suite
robot -d results tests\
```

### Hướng dẫn chạy qua IDE (VSCode)
- Thông tin tại trang: https://onemount.atlassian.net/wiki/spaces/om/pages/1716817581/Run+Tests+Using+Visual+Studio+Code



## Ví dụ sử dụng (trong `KeywordLibraries/CommonKeyword`)

### SeleniumLibrary

```robot
*** Settings ***
Resource   ../../KeywordLibraries/CommonKeyword/WebCore.resource

*** Test Cases ***
Mở trình duyệt và đăng nhập
    Open Browser    ${BASE_URL}    Chrome
    Login With Credentials    ${USERNAME}    ${PASSWORD}
    Capture Page Screenshot    ${OUTPUT_DIR}\login.png
```

### Browser (Playwright)

```robot
*** Settings ***
Resource   ../../KeywordLibraries/CommonKeyword/BrowserCore.resource

*** Test Cases ***
Mở trang Playwright
    New Browser    headless=False
    New Page    ${BASE_URL}
    Fill Text    input[name="user"]    ${USERNAME}
    Click    button[type="submit"]
    Wait For Elements State    h1.title    visible
```

### RESTinstance (API)

```robot
*** Settings ***
Resource   ../../KeywordLibraries/CommonKeyword/ApiCore.resource

*** Test Cases ***
Lấy thông tin thành viên
    ${member}=    Api PSS Get member by id    12345
    Log    ${member}
```

### AppiumLibrary (Mobile)

#### Prerequisites

```bat
:: Cài Appium server
npm install -g appium
appium driver install uiautomator2   :: Android
appium driver install xcuitest       :: iOS

:: Cài Python dependencies
pip install robotframework-appiumlibrary

:: Kiểm tra ADB nhận device
adb devices
```

Yêu cầu: **Android SDK** (biến `ANDROID_HOME`) + device kết nối USB hoặc emulator đang chạy.

#### Cấu hình capabilities — `Variables/CONFIG_MOBILE.yaml`

Không hardcode capabilities trong test. Khai báo tất cả trong file YAML:

```yaml
# Variables/CONFIG_MOBILE.yaml
APPIUM_URL:     http://localhost:4723/wd/hub
PLATFORM_NAME:  Android                          # hoặc iOS
DEVICE_NAME:    emulator-5554                    # serial từ `adb devices`
APP_PACKAGE:    com.example.app
APP_ACTIVITY:   .MainActivity
AUTOMATION_NAME: UiAutomator2                    # hoặc XCUITest cho iOS
NO_RESET:       False
```

#### Khởi động Appium server

```bat
:: Khởi động thủ công (terminal riêng)
appium --base-path /wd/hub

:: Kiểm tra server đang chạy
curl http://localhost:4723/wd/hub/status
```

Framework cũng hỗ trợ tự khởi động Appium qua `Libs/RobotSTF.py` khi dùng STF device farm (xem mục STF bên dưới).

#### Cấu trúc test file

```robot
*** Settings ***
Library    AppiumLibrary    run_on_failure=AppiumLibrary.Capture Page Screenshot
Library    ../../Libs/ScrollAppMoblie.py
Library    ../../Libs/ScrollIOSMoblie.py
Variables  ../../Variables/CONFIG_MOBILE.yaml

Suite Setup       Open Mobile Application
Suite Teardown    Close All Applications

*** Keywords ***
Open Mobile Application
    Open Application    ${APPIUM_URL}
    ...    platformName=${PLATFORM_NAME}
    ...    deviceName=${DEVICE_NAME}
    ...    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}
    ...    automationName=${AUTOMATION_NAME}
    ...    noReset=${NO_RESET}

*** Test Cases ***
TC001 - Đăng nhập thành công
    [Tags]    mobile    android    smoke
    Wait Until Element Is Visible    accessibility_id=username-input    timeout=10s
    Input Text    accessibility_id=username-input    ${USERNAME}
    Input Text    accessibility_id=password-input    ${PASSWORD}
    Click Element    accessibility_id=login-button
    Wait Until Element Is Visible    accessibility_id=home-screen    timeout=15s
```

#### Locator priority

| Ưu tiên | Locator | Ví dụ |
|---|---|---|
| 1 | `accessibility_id` | `accessibility_id=login-button` |
| 2 | `id` | `id=com.example:id/btn_login` |
| 3 | `xpath` | `xpath=//android.widget.Button[@text='Đăng nhập']` |
| 4 | `class chain` / `predicate string` | iOS only |

#### Chạy test

```bat
:: Chạy 1 suite mobile
robot -d results -v ENV:QC Projects/YourModule/test_YourModule_Mobile.robot

:: Chạy theo tag
robot -d results --include mobile Projects/

:: Chạy song song (nhiều device)
pabot --processes 2 -v ENV:QC --include mobile --outputdir results Projects/
```

#### STF Device Farm (dùng chung trong team)

Khi không có device cục bộ, dùng `Libs/RobotSTF.py` để lock device từ farm `http://10.124.57.232`:

```robot
*** Settings ***
Library    Libs/RobotSTF.py

*** Test Cases ***
Run On STF Device
    ${device}=    Lock Device    requirements={"version":"10"}
    Setup Appium    ${device}
    Open Application    ${appium_remote}
    ...    platformName=Android    appPackage=${APP_PACKAGE}
    ...    appActivity=${APP_ACTIVITY}    automationName=UiAutomator2
    [Teardown]    Release Device    ${device}
```

Cần biến môi trường `STF_TOKEN` trước khi chạy:

```bat
set STF_TOKEN=your_token_here
robot -d results Projects/YourModule/test_Mobile.robot
```

#### Quy tắc bắt buộc

- Dùng `Wait Until Element Is Visible` — **KHÔNG** dùng `Sleep`
- Scroll dùng `ScrollAppMoblie.py` (Android) hoặc `ScrollIOSMoblie.py` (iOS)
- Capabilities lấy từ `CONFIG_MOBILE.yaml` — **KHÔNG** hardcode trong test
- Tag mỗi test case với `mobile` và `android`/`ios`




