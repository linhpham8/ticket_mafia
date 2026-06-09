*** Settings ***
Documentation     Mô tả : Các keyword verify trên trang Quản lý nhân viên
...
...    Author: TuyenLe
...
Resource          ../../CommonKeyword/BrowserCore.resource

*** Keywords ***
# ===== VERIFY TRANG DANH SÁCH =====

Verify Trang Quan Ly Nhan Vien hien thi
    [Documentation]    Kiểm tra trang Quản lý nhân viên đã load xong (bảng danh sách hiển thị)
    ...
    Browser.Wait For Elements State    //table    state=visible    timeout=${TIMEOUT}

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
    [Documentation]    Kiểm tra trạng thái của nhân viên trong bảng danh sách theo tên nhân viên
    ...
    [Arguments]    ${ten_nhan_vien}    ${trang_thai}
    Browser.Wait For Elements State    //td//a[contains(text(),'${ten_nhan_vien}')]/ancestor::tr//td[contains(text(),'${trang_thai}')]    state=visible    timeout=${TIMEOUT}

Verify Email Nhan Vien hien thi on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra email của nhân viên hiển thị trong bảng danh sách
    ...
    [Arguments]    ${email}
    Browser.Wait For Elements State    //td[contains(text(),'${email}')]    state=visible    timeout=${TIMEOUT}

Verify So Dien Thoai Nhan Vien hien thi on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra số điện thoại của nhân viên hiển thị trong bảng danh sách
    ...
    [Arguments]    ${so_dien_thoai}
    Browser.Wait For Elements State    //td[contains(text(),'${so_dien_thoai}')]    state=visible    timeout=${TIMEOUT}

Verify Table Nhan Vien is loaded on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra bảng danh sách nhân viên đã load xong (có ít nhất 1 dòng dữ liệu)
    ...
    Browser.Wait For Elements State    //table//tr[contains(@class,'row')]    state=visible    timeout=${TIMEOUT}

Verify Ket Qua Tim Kiem Empty on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra bảng danh sách trống (không có kết quả tìm kiếm)
    ...
    Browser.Wait For Elements State    //table//tr[contains(@class,'row')]    state=detached    timeout=${TIMEOUT}

# ===== VERIFY FORM TẠO MỚI =====


Verify Trang Thai on Chi Tiet Nhan Vien Page
    [Documentation]    Kiểm tra trạng thái hoạt động của nhân viên
    [Arguments]    ${trang_thai}
    Browser.Get Text    sd-select[autoid="sales_platform_user_status"] >> span.c-badge-title:has-text("${trang_thai}") >> nth=0    ==    ${trang_thai}

Verify Ho Va Ten on Chi Tiet Nhan Vien Page
    [Documentation]    Kiểm tra họ và tên của nhân viên
    [Arguments]    ${ho_va_ten}
    Browser.Wait For Elements State    sd-input[autoid="sales_platform_user_full_name"] div.T14M:has-text("${ho_va_ten}")    state=visible

Verify Email on Chi Tiet Nhan Vien Page
    [Documentation]    Kiểm tra email của nhân viên
    [Arguments]    ${email}
    Browser.Wait For Elements State    sd-input[autoid="sales_platform_user_email"] div.T14M:has-text("${email}")    state=visible

Verify table is empty on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra không có dữ liệu trong bảng danh sách
    Browser.Wait For Elements State    text=Không có kết quả phù hợp    state=visible

Verify table is not empty on Quan Ly Nhan Vien Page
    [Documentation]    Kiểm tra có dữ liệu trong bảng danh sách 
    Browser.Take Screenshot
    Browser.Wait For Elements State    text=Không có kết quả phù hợp    state=hidden    timeout=10s
    Browser.Take Screenshot
    Browser.Wait For Elements State    td.mat-column-fullName >> nth=0    state=visible    timeout=60s
    Browser.Take Screenshot
    ${txt}    Browser.Get Text    td.mat-column-fullName >> nth=0
    Should Be True    len("${txt}") > 0  
