*** Settings ***
Documentation     Mô tả: Bộ test case cho trang Quản lý nhân viên
...               Trang: https://sales-platform-qc.masterisehomes.dev/sales-platform/user
...               Kiểm tra các chức năng: tìm kiếm theo nhiều điều kiện, tạo mới nhân viên, lọc trạng thái
...               Author: TuyenLe

Resource          ../../../KeywordLibraries/RealEstateOps/RealEstateOpsGeneral.resource

*** Variables ***
${USERNAME}                 tuyen.le@onemount.com
${PASSWORD}                 123456789


*** Test Cases ***


TC02: [Positive] Tạo mới nhân viên thành công (Thông tin bắt buộc)
    [Documentation]    Kiểm tra quy trình tạo mới nhân viên với các trường bắt buộc:
    ...                Họ và tên, Email, Số điện thoại, Trạng thái
    [Tags]    quanlynhanvien    smoke    positive    create    basic

    OPEN BROWSER AND DELETE COOKIES    url=${URL_REAL_ESTATE_OPS}
    Login with username and password on Login Real Estate Ops Page    ${USERNAME}    ${PASSWORD}
    Verify Login success on Login Real Estate Ops Page
    Go To Quan Ly Nhan Vien Page

    ${rnd}    Get Random String
    ${ho_va_ten}    Set Variable    AutoUI ${rnd}
    ${email}    Set Variable    AutoUI${rnd}@yopmail.com
    Click Button Tao Moi on Quan Ly Nhan Vien Page
    Fill Form Tao Moi Nhan Vien on Tao Moi Nhan Vien Page    ho_va_ten=${ho_va_ten}    email=${email}
    Check Message Toast on NSP Page    message=Tạo mới Nhân viên thành công
    Verify Trang Thai on Chi Tiet Nhan Vien Page    trang_thai=Hoạt động
    Verify Ho Va Ten on Chi Tiet Nhan Vien Page    ho_va_ten=${ho_va_ten}
    Verify Email on Chi Tiet Nhan Vien Page    email=${email}

NSP-TC-485 - NSP-53 - Mh Quản lý Nhân viên: Kiểm tra filter theo Họ & Tên
    [Documentation]    Kiểm tra quy trình tạo mới nhân viên với các trường bắt buộc:
    ...                Họ và tên, Email, Số điện thoại, Trạng thái
    [Tags]    quanlynhanvien

    OPEN BROWSER AND DELETE COOKIES    url=${URL_REAL_ESTATE_OPS}
    Login with username and password on Login Real Estate Ops Page    ${USERNAME}    ${PASSWORD}
    Verify Login success on Login Real Estate Ops Page
    Go To Quan Ly Nhan Vien Page
    FIll form search with condition    ho_va_ten=AutoUI
    Verify table is not empty on Quan Ly Nhan Vien Page

NSP-TC-486 - NSP-53 - Mh Quản lý Nhân viên: Kiểm tra Filter theo Số ĐT
    [Documentation]    Kiểm tra quy trình tạo mới nhân viên với các trường bắt buộc:
    ...                Họ và tên, Email, Số điện thoại, Trạng thái
    [Tags]    quanlynhanvien

    OPEN BROWSER AND DELETE COOKIES    url=${URL_REAL_ESTATE_OPS}
    Login with username and password on Login Real Estate Ops Page    ${USERNAME}    ${PASSWORD}
    Verify Login success on Login Real Estate Ops Page
    Go To Quan Ly Nhan Vien Page
    FIll form search with condition    so_dien_thoai=0123456789
    Verify table is not empty on Quan Ly Nhan Vien Page

NSP-TC-487 - NSP-53 - Mh Quản lý Nhân viên: Kiểm tra Filter theo Email
    [Documentation]    Kiểm tra quy trình tạo mới nhân viên với các trường bắt buộc:
    ...                Họ và tên, Email, Số điện thoại, Trạng thái
    [Tags]    quanlynhanvien

    OPEN BROWSER AND DELETE COOKIES    url=${URL_REAL_ESTATE_OPS}
    Login with username and password on Login Real Estate Ops Page    ${USERNAME}    ${PASSWORD}
    Verify Login success on Login Real Estate Ops Page
    Go To Quan Ly Nhan Vien Page
    FIll form search with condition    email=thuynt261@onemount.com
    Verify table is not empty on Quan Ly Nhan Vien Page

NSP-TC-488 - NSP-53 - Mh Quản lý Nhân viên: Kiểm tra Filter theo Trạng thái
    [Documentation]    Kiểm tra quy trình tạo mới nhân viên với các trường bắt buộc:
    ...                Họ và tên, Email, Số điện thoại, Trạng thái
    [Tags]    quanlynhanvien

    OPEN BROWSER AND DELETE COOKIES    url=${URL_REAL_ESTATE_OPS}
    Login with username and password on Login Real Estate Ops Page    ${USERNAME}    ${PASSWORD}
    Verify Login success on Login Real Estate Ops Page
    Go To Quan Ly Nhan Vien Page
    FIll form search with condition    trang_thai=Ngừng hoạt động
    Verify table is not empty on Quan Ly Nhan Vien Page

NSP-TC-489 - NSP-53 - Mh Quản lý Nhân viên: Kiểm tra Filter theo Ngày tạo
    [Documentation]    Kiểm tra quy trình tạo mới nhân viên với các trường bắt buộc:
    ...                Họ và tên, Email, Số điện thoại, Trạng thái
    [Tags]    quanlynhanvien

    OPEN BROWSER AND DELETE COOKIES    url=${URL_REAL_ESTATE_OPS}
    Login with username and password on Login Real Estate Ops Page    ${USERNAME}    ${PASSWORD}
    Verify Login success on Login Real Estate Ops Page
    Go To Quan Ly Nhan Vien Page
    FIll form search with condition    ngay_tao_tu=10/04/2026    ngay_tao_den=23/04/2026
    Verify table is not empty on Quan Ly Nhan Vien Page

NSP-TC-490 - [NSP-53] - Mh Quản lý Nhân viên: Kiểm tra Filter theo Người tạo
    [Documentation]    Kiểm tra quy trình tạo mới nhân viên với các trường bắt buộc:
    ...                Họ và tên, Email, Số điện thoại, Trạng thái
    [Tags]    quanlynhanvien

    OPEN BROWSER AND DELETE COOKIES    url=${URL_REAL_ESTATE_OPS}
    Login with username and password on Login Real Estate Ops Page    ${USERNAME}    ${PASSWORD}
    Verify Login success on Login Real Estate Ops Page
    Go To Quan Ly Nhan Vien Page
    FIll form search with condition    nguoi_tao=tuyen.le@onemount.com
    Verify table is not empty on Quan Ly Nhan Vien Page

NSP-TC-491 - [NSP-53] - Mh Quản lý Nhân viên: Kiểm tra Filter theo Ngày cập nhật
    [Documentation]    Kiểm tra quy trình tạo mới nhân viên với các trường bắt buộc:
    ...                Họ và tên, Email, Số điện thoại, Trạng thái
    [Tags]    quanlynhanvien

    OPEN BROWSER AND DELETE COOKIES    url=${URL_REAL_ESTATE_OPS}
    Login with username and password on Login Real Estate Ops Page    ${USERNAME}    ${PASSWORD}
    Verify Login success on Login Real Estate Ops Page
    Go To Quan Ly Nhan Vien Page
    FIll form search with condition    ngay_cap_nhat_tu=10/04/2026    ngay_cap_nhat_den=23/04/2026
    Verify table is not empty on Quan Ly Nhan Vien Page

NSP-TC-492 - [NSP-53] - Mh Quản lý Nhân viên: Kiểm tra Filter theo Người cập nhật
    [Documentation]    Kiểm tra quy trình tạo mới nhân viên với các trường bắt buộc:
    ...                Họ và tên, Email, Số điện thoại, Trạng thái
    [Tags]    quanlynhanvien

    OPEN BROWSER AND DELETE COOKIES    url=${URL_REAL_ESTATE_OPS}
    Login with username and password on Login Real Estate Ops Page    ${USERNAME}    ${PASSWORD}
    Verify Login success on Login Real Estate Ops Page
    Go To Quan Ly Nhan Vien Page
    FIll form search with condition    nguoi_cap_nhat=tuyen.le@onemount.com
    Verify table is not empty on Quan Ly Nhan Vien Page

NSP-TC-496 - [NSP-53] - Mh Quản lý Nhân viên: Kiểm tra chuyển trang (Paination)
    [Documentation]    Kiểm tra quy trình tạo mới nhân viên với các trường bắt buộc:
    ...                Họ và tên, Email, Số điện thoại, Trạng thái
    [Tags]    quanlynhanvien
    OPEN BROWSER AND DELETE COOKIES    url=${URL_REAL_ESTATE_OPS}
    Login with username and password on Login Real Estate Ops Page    ${USERNAME}    ${PASSWORD}
    Go To Quan Ly Nhan Vien Page
    #
    Wait for networkidle on NSP Page
    Check row in paginator on NSP Page



*** Keywords ***
Go To Quan Ly Nhan Vien Page
    Go To Menu on NSP Page    menu_name=${EMPTY}    sub_menu_name=QL Nhân viên
    Toggle Sidebar Menu If Needed



FIll form search with condition
    [Arguments]    ${ho_va_ten}=${EMPTY}    ${so_dien_thoai}=${EMPTY}    ${email}=${EMPTY}    ${trang_thai}=${EMPTY}    ${nguoi_cap_nhat}=${EMPTY}    ${nguoi_tao}=${EMPTY}    ${ngay_tao_tu}=${EMPTY}    ${ngay_tao_den}=${EMPTY}    ${ngay_cap_nhat_tu}=${EMPTY}    ${ngay_cap_nhat_den}=${EMPTY}
    IF    '${ho_va_ten}' != '${EMPTY}'
        Enter Ho va ten on Quan Ly Nhan Vien Page    ${ho_va_ten}
    END
    IF    '${so_dien_thoai}' != '${EMPTY}'
        Enter So dien thoai on Quan Ly Nhan Vien Page    ${so_dien_thoai}
    END
    IF    '${email}' != '${EMPTY}'
        Enter Email on Quan Ly Nhan Vien Page    ${email}
    END
    IF    '${trang_thai}' != '${EMPTY}'
        Select Trang Thai on Quan Ly Nhan Vien Page    ${trang_thai}
    END
    IF    '${nguoi_cap_nhat}' != '${EMPTY}'
        Enter Nguoi Cap Nhat on Quan Ly Nhan Vien Page    ${nguoi_cap_nhat}
    END
    IF    '${nguoi_tao}' != '${EMPTY}'
        Enter Nguoi Tao on Quan Ly Nhan Vien Page    ${nguoi_tao}
    END
    #
    IF    '${ngay_tao_tu}' != '${EMPTY}' or '${ngay_tao_den}' != '${EMPTY}'
        Select Ngay Tao on Quan Ly Nhan Vien Page    ${ngay_tao_tu}    ${ngay_tao_den}
    END
    IF    '${ngay_cap_nhat_tu}' != '${EMPTY}' or '${ngay_cap_nhat_den}' != '${EMPTY}'
        Select Ngay Cap Nhat on Quan Ly Nhan Vien Page    ${ngay_cap_nhat_tu}    ${ngay_cap_nhat_den}
    END
    Press Key Enter
    # Wait for loading table on NSP Page
    Wait For Api Search Changes on NSP Page
    # Wait for networkidle on NSP Page

Check row in paginator on NSP Page
    [Documentation]    Kiểm tra số dòng trong table và số trang
    ...    Author: TuyenLe
    ...    Date created: 28/03/2026
    ...
    ${txt}    Get str text paginator on NSP Page
    ${str}   Get Regexp Matches    ${txt}    (\\d+)
    ${total_row}    Set Variable    ${str}[3]

    ${display_row}    set Variable    ${str}[0]
    ${row_page}     set Variable    ${str}[1]
    ${row_on_page}  set Variable    ${str}[2]
    # Lấy số dòng hiển thị ở trang hiện tại
    ${rows}    Set Variable    ${0}
    ${rows_count}    Get total row in table on NPS Page
    ${rows}    Evaluate    ${rows} + ${rows_count}
    #
    FOR    ${page_index}    IN RANGE    (${total_row} - 1) // ${display_row}
        Click Trang Sau on Quan Ly Nhan Vien Page
        Wait for loading table on NSP Page
        ${rows_count}    Get total row in table on NPS Page
        ${rows}    Evaluate    ${rows} + ${rows_count}
    END
    #
    Should Be True    ${rows} == int(${total_row})