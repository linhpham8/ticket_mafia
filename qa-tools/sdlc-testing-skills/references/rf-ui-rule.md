---
name: rf-ui-rule
description: >
  Quy tắc bắt buộc khi sinh Robot Framework keyword cho UI testing dùng thư viện
  robotframework-browser (Playwright). Áp dụng cho mọi project UI web.
  Đọc file này trước khi sinh bất kỳ keyword UI nào.
---

# Robot Framework — Quy Tắc Chi Tiết Keyword UI (Browser/Playwright)

> Bắt buộc đọc khi sinh UI keyword với `robotframework-browser` (Playwright).
> Đọc song song với `rf-keyword-convention.md` (overview 3-layer).

---

## Kiến Trúc 4 Layer

```
LowLevelKeywords/UI_TenTrang.resource       ← 1 action đơn lẻ, không logic
HighLevelKeywords/HighLevel_TenTrang.resource ← ghép Low thành 1 luồng nghiệp vụ
VerificationKeywords/Verify_TenTrang.resource ← chỉ kiểm tra state/nội dung
{ProjectName}General.resource               ← hub import, test case chỉ dùng file này
```

---

## Layer 1 — LowLevel (`UI_TenTrang.resource`)

### File name
`UI_TenTrang.resource` — ví dụ: `UI_QuanLyNhanVien.resource`, `UI_DangNhap.resource`

### Naming convention
`Verb + Mô_tả + on + TenTrang + Page`

| Verb | Dùng khi |
|---|---|
| `Enter` | Nhập text vào input/textarea |
| `Click` | Click button, link, icon, menu item |
| `Select` | Chọn option trong dropdown/combobox |
| `Check` / `Uncheck` | Checkbox |
| `Upload` | Upload file |
| `Get` | Lấy text/attribute để dùng sau |

**Ví dụ đúng:**
- `Enter Ho va ten on Quan Ly Nhan Vien Page`
- `Click Button Tao Moi on Quan Ly Nhan Vien Page`
- `Select Trang Thai on Tao Moi Nhan Vien Page`

### Header bắt buộc
```robot
*** Settings ***
Documentation     Mô tả : Các keyword thao tác trên trang [Tên Trang]
...
...    Author: {tên tác giả}
Resource          ../../CommonKeyword/BrowserCore.resource
```

### Quy tắc bắt buộc
- Mỗi keyword chỉ thực hiện **1 action duy nhất** — không ghép 2 action vào 1 keyword
- Dùng `Browser.` prefix cho tất cả browser actions: `Browser.Fill Text`, `Browser.Click`, `Browser.Select Options By`
- **KHÔNG** chứa IF/FOR, assertion, hay gọi keyword khác
- **KHÔNG** dùng `Sleep` — dùng Wait strategy (xem phần Wait bên dưới)
- **KHÔNG** assert kết quả — đó là việc của VerificationKeywords

### Ví dụ đầy đủ
```robot
*** Settings ***
Documentation     Mô tả : Các keyword thao tác trên trang Quản lý nhân viên
...
...    Author: QA-Team
Resource          ../../CommonKeyword/BrowserCore.resource

*** Keywords ***
# ===== BỘ LỌC / FILTER =====

Enter Ho va ten on Quan Ly Nhan Vien Page
    [Documentation]    Nhập họ và tên vào ô lọc
    ...
    [Arguments]    ${ho_va_ten}
    Browser.Fill Text    [data-autoid='forms-input-table-sales_platform_user-inline-fullName']    ${ho_va_ten}

Click Trang Thai on Quan Ly Nhan Vien Page
    [Documentation]    Click dropdown Trạng thái lọc
    ...
    Browser.Click    [data-autoid='forms-select-table-sales_platform_user-inline-status']

Click Trang Thai on Trang Thai dropdown on Quan Ly Nhan Vien Page
    [Documentation]    Chọn một giá trị trong dropdown trạng thái lọc
    ...
    [Arguments]    ${trang_thai}
    Browser.Click    //div[@role="listbox"]//div[contains(text(),'${trang_thai}')]

# ===== ACTION BUTTONS =====

Click Button Tao Moi on Quan Ly Nhan Vien Page
    [Documentation]    Click nút Tạo mới trên trang danh sách
    ...
    Browser.Click    sd-button[title="Tạo mới"]

# ===== FORM TẠO MỚI =====

Enter Ho va ten on Tao Moi Nhan Vien Page
    [Documentation]    Nhập họ và tên trên form tạo mới
    ...
    [Arguments]    ${ho_va_ten}
    Browser.Fill Text    input[placeholder="Họ và tên"]    ${ho_va_ten}

Select Trang Thai value on Tao Moi Nhan Vien Page
    [Documentation]    Chọn trạng thái trong dropdown trên form tạo mới
    ...
    [Arguments]    ${trang_thai}
    Browser.Click    [data-autoid="forms-select-sales_platform_user_status"]
    Browser.Click    role=option[name="${trang_thai}"]

Click Button Luu on Tao Moi Nhan Vien Page
    [Documentation]    Click nút Lưu trên form tạo mới
    ...
    Browser.Click    [data-autoid="button-sales_platform_user_btn_save"]
```

---

## Layer 2 — HighLevel (`HighLevelKeywords_TenTrang.resource`)

### File name
`HighLevelKeywords_TenTrang.resource` — ví dụ: `HighLevelKeywords_QuanLyNhanVien.resource`

### Naming convention
`Action_tổng_hợp + on + TenTrang + Page`

**Ví dụ đúng:**
- `Search Nhan Vien by Ho va ten on Quan Ly Nhan Vien Page`
- `Fill Form Tao Moi Nhan Vien on Tao Moi Nhan Vien Page`
- `Select Trang Thai on Quan Ly Nhan Vien Page`

### Header bắt buộc
```robot
*** Settings ***
Documentation     Mô tả : Các keyword high level cho trang [Tên Trang]
...
...    Author: {tên tác giả}
Resource    ../../{ProjectName}/LowLevelKeywords/UI_TenTrang.resource
```

### Quy tắc bắt buộc
- Ghép nhiều LowLevel keywords thành **1 luồng nghiệp vụ hoàn chỉnh**
- Được dùng IF/FOR để xử lý conditional logic
- Tham số optional dùng giá trị mặc định: `${param}=${EMPTY}` hoặc `${param}=${None}`
- Import đúng LowLevel resource tương ứng trong Settings
- Gọi `Focus mouse out` sau khi nhập liệu vào input (để trigger blur/validate)
- Gọi `Wait for networkidle on NSP Page` sau action cần chờ API phản hồi

### Ví dụ đầy đủ
```robot
*** Settings ***
Documentation     Mô tả : Các keyword high level cho trang Quản lý nhân viên
...
...    Author: QA-Team
Resource    ../../RealEstateOps/LowLevelKeywords/UI_QuanLyNhanVien.resource
Resource    ../LowLevelKeywords/NSP_UI_Utils.resource

*** Keywords ***
Search Nhan Vien by Ho va ten on Quan Ly Nhan Vien Page
    [Documentation]    Tìm kiếm nhân viên theo họ và tên
    ...    Arguments: ${ho_va_ten} — họ tên cần tìm
    [Arguments]    ${ho_va_ten}
    Enter Ho va ten on Quan Ly Nhan Vien Page    ${ho_va_ten}
    Focus mouse out
    Wait for networkidle on NSP Page

Select Trang Thai on Quan Ly Nhan Vien Page
    [Documentation]    Chọn một hoặc nhiều trạng thái lọc. Nhiều giá trị phân cách bằng dấu phẩy (,)
    ...    Arguments: ${trang_thai} — vd: "Hoạt động" hoặc "Hoạt động,Ngừng hoạt động"
    [Arguments]    ${trang_thai}
    Click Trang Thai on Quan Ly Nhan Vien Page
    ${values}    Split String    ${trang_thai}    ,
    FOR    ${item}    IN    @{values}
        ${item_trimmed}    Strip String    ${item}
        Click Trang Thai on Trang Thai dropdown on Quan Ly Nhan Vien Page    ${item_trimmed}
    END
    Focus mouse out
    Wait for networkidle on NSP Page

Fill Form Tao Moi Nhan Vien on Tao Moi Nhan Vien Page
    [Documentation]    Luồng tạo mới nhân viên: click Tạo mới → nhập thông tin → Lưu
    ...    Arguments:
    ...        ${ho_va_ten}     — họ và tên nhân viên
    ...        ${email}         — email nhân viên
    ...        ${so_dien_thoai} — số điện thoại (optional)
    ...        ${trang_thai}    — Hoạt động / Ngừng hoạt động (default: Hoạt động)
    [Arguments]    ${ho_va_ten}    ${email}    ${so_dien_thoai}=${EMPTY}    ${trang_thai}=Hoạt động
    Click Button Tao Moi on Quan Ly Nhan Vien Page
    Enter Ho va ten on Tao Moi Nhan Vien Page    ${ho_va_ten}
    Enter Email on Tao Moi Nhan Vien Page    ${email}
    Select Trang Thai value on Tao Moi Nhan Vien Page    ${trang_thai}
    IF    '${so_dien_thoai}' != '${EMPTY}'
        Enter So Dien Thoai on Tao Moi Nhan Vien Page    ${so_dien_thoai}
    END
    Click Button Luu on Tao Moi Nhan Vien Page
```

---

## Layer 3 — VerificationKeywords (`VerificationKeywords_TenTrang.resource`)

### File name
`VerificationKeywords_TenTrang.resource` — ví dụ: `VerificationKeywords_QuanLyNhanVien.resource`

### Naming convention
`Verify + Mô_tả + on + TenTrang + Page`

**Ví dụ đúng:**
- `Verify Nhan Vien hien thi on Quan Ly Nhan Vien Page`
- `Verify Trang Thai Nhan Vien on Quan Ly Nhan Vien Page`
- `Verify Thong bao loi hien thi on Dang Nhap Page`

### Header bắt buộc
```robot
*** Settings ***
Documentation     Mô tả : Các keyword verify trên trang [Tên Trang]
...
...    Author: {tên tác giả}
Resource          ../../CommonKeyword/BrowserCore.resource
```
> Import `BrowserCore.resource` — **KHÔNG** import LowLevel.

### Quy tắc bắt buộc
- Dùng `Browser.Wait For Elements State` để verify element **hiện/ẩn/enabled**
- Dùng `Browser.Get Text` + `Should Contain` / `Should Be Equal As Strings` để verify **nội dung text**
- **KHÔNG** chứa IF/FOR hay business logic — chỉ verify state và giá trị
- **KHÔNG** import LowLevel resource

### Hai pattern verify

**Pattern A — Verify element visibility:**
```robot
Browser.Wait For Elements State    <locator>    state=visible    timeout=${TIMEOUT}
Browser.Wait For Elements State    <locator>    state=hidden     timeout=${TIMEOUT}
Browser.Wait For Elements State    <locator>    state=detached   timeout=${TIMEOUT}
```

**Pattern B — Verify text content:**
```robot
${text}    Browser.Get Text    <locator>
Should Contain    ${text}    ${expected_value}
# hoặc:
Should Be Equal As Strings    ${text}    ${expected_value}
```

### Ví dụ đầy đủ
```robot
*** Settings ***
Documentation     Mô tả : Các keyword verify trên trang Quản lý nhân viên
...
...    Author: QA-Team
Resource          ../../CommonKeyword/BrowserCore.resource

*** Keywords ***
# ===== VERIFY TRANG DANH SÁCH =====

Verify Nhan Vien hien thi on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra nhân viên hiển thị trong bảng danh sách theo họ và tên
    ...
    [Arguments]    ${ten_nhan_vien}
    Browser.Wait For Elements State    //td//a[contains(text(),'${ten_nhan_vien}')]    state=visible    timeout=${TIMEOUT}

Verify Nhan Vien khong hien thi on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra nhân viên KHÔNG hiển thị trong bảng danh sách
    ...
    [Arguments]    ${ten_nhan_vien}
    Browser.Wait For Elements State    //td//a[contains(text(),'${ten_nhan_vien}')]    state=detached    timeout=${TIMEOUT}

Verify Trang Thai Nhan Vien on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra trạng thái của nhân viên trong bảng theo tên nhân viên
    ...
    [Arguments]    ${ten_nhan_vien}    ${trang_thai}
    Browser.Wait For Elements State
    ...    //td//a[contains(text(),'${ten_nhan_vien}')]/ancestor::tr//td[contains(text(),'${trang_thai}')]
    ...    state=visible    timeout=${TIMEOUT}

Verify Table Nhan Vien is loaded on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra bảng danh sách đã load xong (ít nhất 1 dòng dữ liệu)
    ...
    Browser.Wait For Elements State    //table//tr[contains(@class,'row')]    state=visible    timeout=${TIMEOUT}

Verify Ket Qua Tim Kiem Empty on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra bảng danh sách trống (không có kết quả tìm kiếm)
    ...
    Browser.Wait For Elements State    text=Không có kết quả phù hợp    state=visible

# ===== VERIFY FORM CHI TIẾT =====

Verify Ho Va Ten on Chi Tiet Nhan Vien Page
    [Documentation]    Kiểm tra họ và tên hiển thị đúng trên trang chi tiết
    ...
    [Arguments]    ${ho_va_ten}
    Browser.Wait For Elements State    sd-input[autoid="sales_platform_user_full_name"] div.T14M:has-text("${ho_va_ten}")    state=visible

Verify Trang Thai on Chi Tiet Nhan Vien Page
    [Documentation]    Kiểm tra trạng thái hiển thị đúng trên trang chi tiết (dùng Get Text)
    ...
    [Arguments]    ${trang_thai}
    ${text}    Browser.Get Text    sd-select[autoid="sales_platform_user_status"] >> span.c-badge-title >> nth=0
    Should Be Equal As Strings    ${text}    ${trang_thai}
```

---

## Layer 4 — General Resource (`{ProjectName}General.resource`)

Hub tập trung import toàn bộ HighLevel + Verification của project.

```robot
*** Settings ***
# Auto-generated — thêm import khi tạo module mới
Resource    ../../KeywordLibraries/{ProjectName}/HighLevelKeywords/HighLevelKeywords_Login.resource
Resource    ../../KeywordLibraries/{ProjectName}/HighLevelKeywords/HighLevelKeywords_QuanLyNhanVien.resource
Resource    ../../KeywordLibraries/{ProjectName}/VerificationKeywords/VerificationKeywords_Login.resource
Resource    ../../KeywordLibraries/{ProjectName}/VerificationKeywords/VerificationKeywords_QuanLyNhanVien.resource
```

**Test case chỉ import 1 dòng:**
```robot
Resource    ../../KeywordLibraries/{ProjectName}/{ProjectName}General.resource
```

> Khi tạo module mới **phải cập nhật** file General — không để test case tự import trực tiếp HighLevel/Verification.

---

## Layer 5 — Test Case (`test_TenModule.robot`)

```robot
*** Settings ***
Resource    ../../KeywordLibraries/{ProjectName}/{ProjectName}General.resource

*** Test Cases ***
NSP-TC-001 Tim kiem nhan vien theo ten thanh cong
    [Documentation]    Kiểm tra tìm kiếm nhân viên theo tên hiển thị đúng kết quả
    [Tags]    smoke    regression    quan-ly-nhan-vien
    Search Nhan Vien by Ho va ten on Quan Ly Nhan Vien Page    Nguyen Van A
    Verify Nhan Vien hien thi on Quan Ly Nhan Vien Page    Nguyen Van A

NSP-TC-002 Tao moi nhan vien thanh cong
    [Documentation]    Kiểm tra tạo mới nhân viên với đầy đủ thông tin
    [Tags]    regression    quan-ly-nhan-vien
    Fill Form Tao Moi Nhan Vien on Tao Moi Nhan Vien Page
    ...    ho_va_ten=Test User Autotest
    ...    email=test.autotest@company.com
    ...    trang_thai=Hoạt động
    Verify Nhan Vien hien thi on Quan Ly Nhan Vien Page    Test User Autotest
    Verify Trang Thai Nhan Vien on Quan Ly Nhan Vien Page    Test User Autotest    Hoạt động
```

---

## Locator Priority (thứ tự ưu tiên)

| Thứ tự | Loại | Cú pháp | Ghi chú |
|---|---|---|---|
| 1 | data-autoid | `[data-autoid='ten-element']` | Ưu tiên cao nhất — stable nhất |
| 2 | id | `id=ten-id` | Dùng khi có id cố định |
| 3 | Chain selector | `parent >> child >> nth=0` | Rất khuyến khích — mix nhiều loại |
| 4 | XPath | `//tag[@attr='value']` | Khi cần traverse DOM phức tạp |
| 5 | CSS | `div.class-name` | CSS selector tiêu chuẩn |
| 6 | Text | `text=Nội dung` hoặc `"Nội dung"` | Cuối cùng — dễ vỡ khi đổi label |

### Chain Selector (`>>`) — ưu tiên dùng

```robot
# Lấy input đầu tiên trong table
table[role="table"] >> input >> nth=0

# Nút cha của text
text=Tên dự án >> .. >> button

# Mix CSS + XPath
css=div.header >> xpath=//button[@type='submit']

# data-autoid chain
[data-autoid='table-list'] >> tbody >> tr >> nth=1 >> td >> nth=2
```

### Lưu ý Strict Mode
- **Strict Mode** mặc định **bật** — locator tìm thấy nhiều element → FAIL.
- Phải dùng `nth=` hoặc chain selector để cô lập.
- Selector bắt đầu `//` hoặc `..` → tự động là XPath.
- Selector trong `"..."` → tự động là Text selector.
- **Shadow DOM**: `css=` tự động pierce shadow roots (tốt cho Angular/Material).
- **Iframe**: dùng `>>>` để chuyển frame: `id=iframe-name >>> css=button`.
- Escape `#` thành `\#` nếu dùng CSS ID selector.

---

## Wait Strategy (không dùng Sleep)

| Keyword | Khi nào dùng |
|---|---|
| `Browser.Wait For Elements State <sel> state=visible timeout=Xs` | Chờ element xuất hiện |
| `Browser.Wait For Elements State <sel> state=hidden timeout=Xs` | Chờ element ẩn đi |
| `Browser.Wait For Elements State <sel> state=detached timeout=Xs` | Chờ element bị remove khỏi DOM |
| `Browser.Wait For Load State networkidle timeout=25s` | Chờ network idle sau action |
| `Wait for networkidle on NSP Page` | Sau khi nhập liệu + focus out (dùng trong HighLevel) |
| `Wait for loading table on NSP Page` | Đợi bảng data load xong |
| `Focus mouse out` | Click ra ngoài để đóng dropdown/combobox |

> **Chỉ dùng Sleep khi thật sự cần** (ví dụ: animation cố định không có sự kiện DOM).
> Nếu dùng Sleep phải ghi comment lý do.

---

## Quy Trình Tạo Module Mới (6 bước)

1. **Scan trang** — Xác định tất cả field, button, dropdown, table, modal trên trang
2. **Tạo LowLevel** — `UI_TenTrang.resource` — mỗi element 1 keyword action
3. **Tạo HighLevel** — `HighLevelKeywords_TenTrang.resource` — ghép Low thành luồng nghiệp vụ
4. **Tạo Verification** — `VerificationKeywords_TenTrang.resource` — verify state + nội dung
5. **Cập nhật General** — Thêm import HighLevel + Verification vào `{ProjectName}General.resource`
6. **Tạo Test Case** — `test_TenModule.robot` import General, viết TC dùng HighLevel + Verification

---

## Checklist Trước Khi Xuất

- [ ] LowLevel: mỗi keyword chỉ có 1 action, không IF/FOR, không assertion
- [ ] HighLevel: import đúng LowLevel, gọi `Focus mouse out` + wait sau action
- [ ] Verification: dùng `Wait For Elements State` (visibility) hoặc `Get Text` (content), không IF/FOR
- [ ] General: đã thêm import HighLevel + Verification của module mới
- [ ] Test Case: chỉ import General resource, không import trực tiếp Low/High/Verify
- [ ] Locator: ưu tiên `data-autoid` → chain → id → xpath → css → text
- [ ] Không dùng Sleep
- [ ] Header Documentation + Author đúng format trong mọi .resource file

---

## Tài liệu tham chiếu

- RF Browser library docs: https://marketsquare.github.io/robotframework-browser/Browser.html
- Playwright locators: https://playwright.dev/docs/locators
- Playwright other locators: https://playwright.dev/docs/other-locators
