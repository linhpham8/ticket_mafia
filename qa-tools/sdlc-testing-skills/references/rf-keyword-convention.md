# Robot Framework — Quy Tắc Keyword 3-Layer

> Skill 06 đọc file này khi sinh Robot Framework script.
> Áp dụng cho mọi project dùng `robotframework-browser` (Playwright) làm UI library.

---

## Kiến trúc 3 Layer

```
LowLevelKeywords/     ← 1 action nhỏ nhất, không logic
HighLevelKeywords/    ← ghép Low thành 1 luồng nghiệp vụ
VerificationKeywords/ ← chỉ verify state của element/data
```

---

## Layer 1 — LowLevel (`UI_TenTrang.resource`)

**File name:** `UI_TenTrang.resource`
(ví dụ: `UI_QuanLyNhanVien.resource`, `UI_DangNhap.resource`)

**Naming convention:** `Verb + Mô tả + on Ten Trang Page`
- `Enter Ho va ten on Quan Ly Nhan Vien Page`
- `Click Trang Thai on Quan Ly Nhan Vien Page`
- `Select Ngay Sinh on Quan Ly Nhan Vien Page`

**Quy tắc bắt buộc:**
- Mỗi keyword chỉ làm **1 action nhỏ nhất** (Enter, Click, Select, Get Text...)
- Dùng `Browser.` prefix cho tất cả browser actions: `Browser.Fill Text`, `Browser.Click`...
- **Không** chứa logic điều kiện (IF/FOR)
- **Không** assert nghiệp vụ
- **Không** dùng Sleep — dùng Wait thay thế (xem phần Wait)

**Header bắt buộc:**
```robot
*** Settings ***
Documentation     Mô tả : Các keyword thao tác trên trang [Tên Trang]
...
...    Author: {tên tác giả}
Resource          ../../CommonKeyword/BrowserCore.resource
```

**Ví dụ:**
```robot
Enter Ten on [TenTrang] Page
    [Documentation]    Nhập tên vào ô tên trên trang [TenTrang]
    ...
    [Arguments]    ${ten}
    Browser.Fill Text    [data-autoid='input-ten']    ${ten}

Click Luu on [TenTrang] Page
    [Documentation]    Click nút Lưu trên trang [TenTrang]
    ...
    Browser.Click    [data-autoid='btn-luu']
```

---

## Layer 2 — HighLevel (`HighLevelKeywords_TenTrang.resource`)

**File name:** `HighLevelKeywords_TenTrang.resource`

**Naming convention:** `Action tổng hợp + on Ten Trang Page`
- `Search Nhan Vien by Ten on Quan Ly Nhan Vien Page`
- `Select Trang Thai on Quan Ly Nhan Vien Page`
- `Fill Form Tao Moi on Quan Ly Nhan Vien Page`

**Quy tắc bắt buộc:**
- Ghép nhiều LowLevel keywords thành **1 luồng nghiệp vụ hoàn chỉnh**
- Được dùng IF/FOR để xử lý logic
- Tham số có giá trị mặc định khi phù hợp: `${param}=${EMPTY}`
- Import LowLevel tương ứng:

```robot
*** Settings ***
Resource    ../../{ProjectName}/LowLevelKeywords/UI_TenTrang.resource
```

**Ví dụ:**
```robot
Search by Ten on [TenTrang] Page
    [Documentation]    Tìm kiếm theo tên trên trang [TenTrang]
    ...    Arguments: ${ten} — tên cần tìm
    [Arguments]    ${ten}
    Enter Ten on [TenTrang] Page    ${ten}
    Focus mouse out
    Wait for networkidle on NSP Page
```

---

## Layer 3 — Verification (`VerificationKeywords_TenTrang.resource`)

**File name:** `VerificationKeywords_TenTrang.resource`

**Naming convention:** `Verify + Mô tả + on Ten Trang Page`
- `Verify Ten hien thi on Quan Ly Nhan Vien Page`
- `Verify Trang Thai la on Quan Ly Nhan Vien Page`
- `Verify Thong bao loi hien thi on Dang Nhap Page`

**Quy tắc bắt buộc:**
- Dùng `Browser.Wait For Elements State` để verify element hiện/ẩn/enabled (không dùng Sleep thay thế)
- Được dùng `Browser.Get Text` + `Should Contain` / `Should Be Equal As Strings` để assert nội dung text
- **Không** chứa business logic điều kiện (IF/FOR) — chỉ kiểm tra trạng thái và giá trị
- Import `BrowserCore.resource` (không import LowLevel)

**Header bắt buộc:**
```robot
*** Settings ***
Documentation     Mô tả : Các keyword verify trên trang [Tên Trang]
...
...    Author: {tên tác giả}
...
Resource          ../../CommonKeyword/BrowserCore.resource
```

**Ví dụ:**
```robot
Verify Ten hien thi on [TenTrang] Page
    [Documentation]    Kiểm tra tên hiển thị đúng trên trang [TenTrang]
    ...
    [Arguments]    ${ten}
    Browser.Wait For Elements State    //td[contains(text(),'${ten}')]    state=visible    timeout=10s

Verify Thong bao loi hien thi on [TenTrang] Page
    [Documentation]    Kiểm tra thông báo lỗi xuất hiện
    ...
    [Arguments]    ${noi_dung_loi}
    Browser.Wait For Elements State    text=${noi_dung_loi}    state=visible    timeout=5s
```

---

## General Resource File

Mỗi project dùng 1 file hub tập trung import toàn bộ HighLevel + Verification:

**File:** `{ProjectName}General.resource`

```robot
*** Settings ***
# Auto-generated — thêm import khi tạo module mới
Resource    ../../KeywordLibraries/{ProjectName}/HighLevelKeywords/HighLevelKeywords_TenTrang.resource
Resource    ../../KeywordLibraries/{ProjectName}/VerificationKeywords/VerificationKeywords_TenTrang.resource
```

**Test case chỉ import 1 dòng:**
```robot
Resource    ../../KeywordLibraries/{ProjectName}/{ProjectName}General.resource
```

> Khi tạo module mới **phải cập nhật** file General để test case có thể dùng ngay.

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

### Lưu ý quan trọng

- **Strict Mode** mặc định **bật** — locator tìm thấy nhiều element → FAIL. Phải dùng `nth=` hoặc chain để cô lập.
- Selector bắt đầu `//` hoặc `..` → tự động là XPath.
- Selector trong `"..."` → tự động là Text selector.
- **Shadow DOM**: `css=` tự động pierce shadow roots (tốt cho Angular/Material).
- **Iframe**: dùng `>>>` để chuyển frame: `id=iframe-name >>> css=button`.
- Escape `#` thành `\#` nếu dùng CSS ID selector.

---

## Wait Strategy (không dùng Sleep)

| Thay Sleep bằng | Khi nào dùng |
|---|---|
| `Browser.Wait For Elements State selector state=visible timeout=Xs` | Chờ element xuất hiện |
| `Browser.Wait For Elements State selector state=hidden timeout=Xs` | Chờ element biến mất |
| `Browser.Wait For Load State networkidle timeout=25s` | Chờ network idle sau action |
| `Wait for networkidle on NSP Page` | Sau khi nhập liệu + focus out |
| `Wait for loading table on NSP Page` | Đợi bảng data load xong |
| `Focus mouse out` | Click ra ngoài để đóng dropdown/combobox |

> **Chỉ dùng Sleep khi thật sự cần** (ví dụ: animation cố định không có sự kiện DOM).
> Nếu dùng Sleep phải ghi comment lý do.

---

## Quy Trình Tạo Module Mới (6 bước)

1. **Scan trang** — Xác định tất cả field, button, dropdown, table, modal trên trang
2. **Tạo LowLevel** — `UI_TenTrang.resource` — mỗi element 1 keyword action
3. **Tạo HighLevel** — `HighLevelKeywords_TenTrang.resource` — ghép Low thành luồng nghiệp vụ
4. **Tạo Verification** — `VerificationKeywords_TenTrang.resource` — các bước verify state
5. **Cập nhật General** — Thêm import HighLevel + Verification vào `{ProjectName}General.resource`
6. **Tạo Test Case** — `test_TenModule.robot` import General, viết TC dùng HighLevel + Verification

---

## Tài liệu tham chiếu

- RF Browser library docs: https://marketsquare.github.io/robotframework-browser/Browser.html
- Playwright locators: https://playwright.dev/docs/locators
- Playwright other locators: https://playwright.dev/docs/other-locators
