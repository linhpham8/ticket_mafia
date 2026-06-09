*** Settings ***
Documentation     Mô tả : Các keyword thao tác trên trang Quản lý nhân viên
...
...    Author: TuyenLe
...
Resource          ../../CommonKeyword/BrowserCore.resource

*** Keywords ***
# ===== BỘ LỌC / FILTER =====

Enter Ho va ten on Quan Ly Nhan Vien Page
    [Documentation]    Nhập họ và tên vào ô lọc họ và tên trên trang quản lý nhân viên
    ...
    [Arguments]    ${ho_va_ten}
    Browser.Fill Text    [data-autoid='forms-input-table-sales_platform_user-inline-fullName']    ${ho_va_ten}

Enter So dien thoai on Quan Ly Nhan Vien Page
    [Documentation]    Nhập số điện thoại vào ô lọc số điện thoại trên trang quản lý nhân viên
    ...
    [Arguments]    ${so_dien_thoai}
    Browser.Fill Text    [data-autoid='forms-input-table-sales_platform_user-inline-phoneNumber']    ${so_dien_thoai}

Enter Email on Quan Ly Nhan Vien Page
    [Documentation]    Nhập email vào ô lọc email trên trang quản lý nhân viên
    ...
    [Arguments]    ${email}
    Browser.Fill Text    [data-autoid='forms-input-table-sales_platform_user-inline-email']    ${email}

Click Trang Thai on Quan Ly Nhan Vien Page
    [Documentation]    Click dropdown Trạng thái lọc trên trang quản lý nhân viên
    ...
    Browser.Click    [data-autoid='forms-select-table-sales_platform_user-inline-status']

Click Trang Thai on Trang Thai dropdown on Quan Ly Nhan Vien Page
    [Documentation]    Chọn một giá trị trong dropdown trạng thái lọc trên trang quản lý nhân viên
    ...
    [Arguments]    ${trang_thai}
    Browser.Click    //div[@role="listbox"]//div[contains(text(),'${trang_thai}')]

Enter Nguoi Tao on Quan Ly Nhan Vien Page
    [Documentation]    Nhập người tạo vào ô lọc người tạo trên trang quản lý nhân viên
    ...
    [Arguments]    ${nguoi_tao}
    Browser.Fill Text    [data-autoid='forms-input-table-sales_platform_user-inline-createdBy']    ${nguoi_tao}

Enter Nguoi Cap Nhat on Quan Ly Nhan Vien Page
    [Documentation]    Nhập người cập nhật vào ô lọc người cập nhật trên trang quản lý nhân viên
    ...
    [Arguments]    ${nguoi_cap_nhat}
    Browser.Fill Text    [data-autoid='forms-input-table-sales_platform_user-inline-modifiedBy']    ${nguoi_cap_nhat}

Enter Ngay Tao Tu on Quan Ly Nhan Vien Page
    [Documentation]    Nhập ngày tạo từ vào bộ lọc ngày tạo trên trang quản lý nhân viên
    ...
    [Arguments]    ${ngay_tao_tu}
    Browser.Fill Text    th.mat-column-createdAt sd-date-range >> input[placeholder="Từ"]    ${ngay_tao_tu}

Enter Ngay Tao Den on Quan Ly Nhan Vien Page
    [Documentation]    Nhập ngày tạo đến vào bộ lọc ngày tạo trên trang quản lý nhân viên
    ...
    [Arguments]    ${ngay_tao_den}
    Browser.Fill Text    th.mat-column-createdAt sd-date-range >> input[placeholder="đến"]    ${ngay_tao_den}

Enter Ngay Cap Nhat Tu on Quan Ly Nhan Vien Page
    [Documentation]    Nhập ngày cập nhật từ vào bộ lọc ngày cập nhật trên trang quản lý nhân viên
    ...
    [Arguments]    ${ngay_cap_nhat_tu}
    Browser.Fill Text    th.mat-column-modifiedAt sd-date-range >> input[placeholder="Từ"]    ${ngay_cap_nhat_tu}

Enter Ngay Cap Nhat Den on Quan Ly Nhan Vien Page
    [Documentation]    Nhập ngày cập nhật đến vào bộ lọc ngày cập nhật trên trang quản lý nhân viên
    ...
    [Arguments]    ${ngay_cap_nhat_den}
    Browser.Fill Text    th.mat-column-modifiedAt sd-date-range >> input[placeholder="đến"]    ${ngay_cap_nhat_den}

Enter and select value in dropdown on Quan Ly Nhan Vien Page
    [Documentation]    Keyword viết riêng sẽ xử lý cho trường hợp nhập tên trong trường input và click vào danh sách
    [Arguments]    ${value}
    # Browser.Fill Text    css=input.c-search-input    ${value}
    Browser.Click    role=option[name="${value}"]

Click Button Tao Moi on Quan Ly Nhan Vien Page
    [Documentation]    Click nút Tạo mới trên trang danh sách quản lý nhân viên
    ...    
    Browser.Click    sd-button[title="Tạo mới"]

# ===== ACTION BUTTONS TRANG DANH SÁCH =====


Click Tai Lai on Quan Ly Nhan Vien Page
    [Documentation]    Click nút Tải lại để refresh danh sách nhân viên
    ...
    Browser.Click    //button[span[contains(text(),'Tải lại')]]

Click Thiet Lap on Quan Ly Nhan Vien Page
    [Documentation]    Click nút Thiết lập để cấu hình hiển thị bảng
    ...
    Browser.Click    //button[span[contains(text(),'Thiết lập')]]

# ===== CLICK VÀO DÒNG TRONG BẢNG =====

Click Nhan Vien by name on Quan Ly Nhan Vien Page
    [Documentation]    Click vào tên nhân viên trong bảng danh sách để mở chi tiết/chỉnh sửa
    ...
    [Arguments]    ${ten_nhan_vien}
    Browser.Click    //td//a[contains(text(),'${ten_nhan_vien}')]

# ===== FORM TẠO MỚI NHÂN VIÊN =====

Enter Ho va ten on Tao Moi Nhan Vien Page
    [Documentation]    Nhập họ và tên vào ô Họ và tên trên trang tạo mới nhân viên
    ...
    [Arguments]    ${ho_va_ten}
    Browser.Fill Text    input[placeholder="Họ và tên"]    ${ho_va_ten}

Enter Email on Ton Tao Moi Nhan Vien Page
    [Documentation]    Nhập email vào ô Email trên trang tạo mới nhân viên
    ...
    [Arguments]    ${email}
    Browser.Fill Text    input[placeholder="Email"]    ${email}

Enter So Dien Thoai on Tao Moi Nhan Vien Page
    [Documentation]    Nhập số điện thoại vào ô Số điện thoại trên trang tạo mới nhân viên
    ...
    [Arguments]    ${so_dien_thoai}
    Browser.Fill Text    input[placeholder="Số điện thoại"]    ${so_dien_thoai}

Select Trang Thai value on Tao Moi Nhan Vien Page
    [Documentation]    Click và chọn giá trị trạng thái trong dropdown trên trang tạo mới nhân viên
    ...
    [Arguments]    ${trang_thai}
    Browser.Click    [data-autoid="forms-select-sales_platform_user_status"]
    Browser.Click    role=option[name="${trang_thai}"]

Click Button Luu on Tao Moi Nhan Vien Page
    [Documentation]    Click nút Lưu trên form tạo mới nhân viên
    ...
    Browser.Click    [data-autoid="button-sales_platform_user_btn_save"]

Click Bo Qua on Tao Moi Nhan Vien Page
    [Documentation]    Click nút Bỏ qua (hủy) trên form tạo mới nhân viên
    ...
    Browser.Click    sd-button[title="Bỏ qua"]

# ===== PAGINATION =====

Click Trang Sau on Quan Ly Nhan Vien Page
    [Documentation]    Click nút trang sau trên trang quản lý nhân viên
    ...
    Browser.Click    button[aria-label='Trang sau']
Click Trang Truoc on Quan Ly Nhan Vien Page
    [Documentation]    Click nút trang trước trên trang quản lý nhân viên
    ...
    Browser.Click    button[aria-label='Trang trước']

Click Trang Dau on Quan Ly Nhan Vien Page
    [Documentation]    Click nút về trang đầu trên trang quản lý nhân viên
    ...
    Browser.Click    button[aria-label='Trang đầu']

Click Trang Cuoi on Quan Ly Nhan Vien Page
    [Documentation]    Click nút về trang cuối trên trang quản lý nhân viên
    ...
    Browser.Click    button[aria-label='Trang cuối']
