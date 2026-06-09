*** Settings ***
Documentation     Mô tả : Các keyword high level cho trang Quản lý nhân viên
...
...    Author: TuyenLe
...
Resource    ../../RealEstateOps/LowLevelKeywords/UI_QuanLyNhanVien.resource
Resource    ../LowLevelKeywords/NSP_UI_Utils.resource

*** Keywords ***
# ===== TÌM KIẾM / LỌC =====

Search Nhan Vien by Ho va ten on Quan Ly Nhan Vien Page
    [Documentation]    Tìm kiếm nhân viên theo họ và tên, sau đó chờ bảng cập nhật
    ...
    ...    Arguments:
    ...        ${ho_va_ten}    Họ và tên cần tìm kiếm
    ...
    [Arguments]    ${ho_va_ten}
    Enter Ho va ten on Quan Ly Nhan Vien Page    ${ho_va_ten}
    Focus mouse out
    Wait for networkidle on NSP Page

Search Nhan Vien by Email on Quan Ly Nhan Vien Page
    [Documentation]    Tìm kiếm nhân viên theo email, sau đó chờ bảng cập nhật
    ...
    ...    Arguments:
    ...        ${email}    Email cần tìm kiếm
    ...
    [Arguments]    ${email}
    Enter Email on Quan Ly Nhan Vien Page    ${email}
    Focus mouse out
    Wait for networkidle on NSP Page

Search Nhan Vien by So dien thoai on Quan Ly Nhan Vien Page
    [Documentation]    Tìm kiếm nhân viên theo số điện thoại, sau đó chờ bảng cập nhật
    ...
    ...    Arguments:
    ...        ${so_dien_thoai}    Số điện thoại cần tìm kiếm
    ...
    [Arguments]    ${so_dien_thoai}
    Enter So dien thoai on Quan Ly Nhan Vien Page    ${so_dien_thoai}
    Focus mouse out
    Wait for networkidle on NSP Page

Select Trang Thai on Quan Ly Nhan Vien Page
    [Documentation]    Chọn một hoặc nhiều trạng thái lọc trên trang quản lý nhân viên.
    ...    Nhiều giá trị phân cách bằng dấu phẩy (,)
    ...
    ...    Arguments:
    ...        ${trang_thai}    Trạng thái cần lọc (vd: Hoạt động hoặc Hoạt động,Ngừng hoạt động)
    ...
    [Arguments]    ${trang_thai}
    Click Trang Thai on Quan Ly Nhan Vien Page
    ${values}    Split String    ${trang_thai}    ,
    FOR    ${item}    IN    @{values}
        ${item_trimmed}    Strip String    ${item}
        Click Trang Thai on Trang Thai dropdown on Quan Ly Nhan Vien Page    ${item_trimmed}
    END
    Focus mouse out
    Wait for networkidle on NSP Page

Select Ngay Tao on Quan Ly Nhan Vien Page
    [Documentation]    Nhập khoảng ngày tạo vào bộ lọc. Bỏ qua nếu không truyền tham số.
    ...
    ...    Arguments:
    ...        ${ngay_tao_tu}    Ngày tạo từ (vd: 01/03/2026)
    ...        ${ngay_tao_den}   Ngày tạo đến (vd: 31/03/2026)
    ...
    [Arguments]    ${ngay_tao_tu}=${EMPTY}    ${ngay_tao_den}=${EMPTY}
    IF    '${ngay_tao_tu}' != '${EMPTY}'
        Enter Ngay Tao Tu on Quan Ly Nhan Vien Page    ${ngay_tao_tu}
    END
    IF    '${ngay_tao_den}' != '${EMPTY}'
        Enter Ngay Tao Den on Quan Ly Nhan Vien Page    ${ngay_tao_den}
    END

Select Ngay Cap Nhat on Quan Ly Nhan Vien Page
    [Documentation]    Nhập khoảng ngày cập nhật vào bộ lọc. Bỏ qua nếu không truyền tham số.
    ...
    ...    Arguments:
    ...        ${ngay_cap_nhat_tu}    Ngày cập nhật từ (vd: 01/03/2026)
    ...        ${ngay_cap_nhat_den}   Ngày cập nhật đến (vd: 31/03/2026)
    ...
    [Arguments]    ${ngay_cap_nhat_tu}=${EMPTY}    ${ngay_cap_nhat_den}=${EMPTY}
    IF    '${ngay_cap_nhat_tu}' != '${EMPTY}'
        Enter Ngay Cap Nhat Tu on Quan Ly Nhan Vien Page    ${ngay_cap_nhat_tu}
    END
    IF    '${ngay_cap_nhat_den}' != '${EMPTY}'
        Enter Ngay Cap Nhat Den on Quan Ly Nhan Vien Page    ${ngay_cap_nhat_den}
    END

Tai Lai Danh Sach on Quan Ly Nhan Vien Page
    [Documentation]    Click nút Tải lại và chờ danh sách nhân viên được làm mới
    ...
    Click Tai Lai on Quan Ly Nhan Vien Page
    Wait for loading table on NSP Page

# ===== TẠO MỚI NHÂN VIÊN =====

Fill Form Tao Moi Nhan Vien on Tao Moi Nhan Vien Page
    [Documentation]    Luồng tạo mới nhân viên: click Tạo mới → nhập thông tin → Lưu
    ...
    ...    Arguments:
    ...        ${ho_va_ten}        Họ và tên nhân viên
    ...    
    ...        ${email}            Email nhân viên
    ...    
    ...        ${so_dien_thoai}    Số điện thoại
    ...    
    ...        ${trang_thai}       Trạng thái: Hoạt động / Ngừng hoạt động
    ...
    [Arguments]    ${ho_va_ten}    ${email}    ${so_dien_thoai}=${EMPTY}    ${trang_thai}=Hoạt động
    Enter Ho va ten on Tao Moi Nhan Vien Page    ${ho_va_ten}
    Enter Email on Ton Tao Moi Nhan Vien Page    ${email}
    Select Trang Thai value on Tao Moi Nhan Vien Page    ${trang_thai}
    IF    '${so_dien_thoai}' != '${EMPTY}'
    Enter So Dien Thoai on Tao Moi Nhan Vien Page    ${so_dien_thoai}
    END
    Click Button Luu on Tao Moi Nhan Vien Page
