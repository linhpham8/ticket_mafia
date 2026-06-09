*** Settings ***
Resource          ../../CommonKeyword/BrowserCore.resource

*** Keywords ***

Wait for loading table on NSP Page
    [Documentation]    Mô tả : Đợi cho hiển thị bảng danh sách trong lần đầu tiên vào menu - đợi hiện thị bảng
    ...
    ...    @tuyenle
    ...    Date created: 28/03/2026
    ...
    Browser.Wait For Elements State    div.c-loading    state=attached    timeout=120s
    Browser.Wait For Elements State    div.c-loading    state=detached    timeout=120s

Wait for networkidle on NSP Page
    [Documentation]    Mô tả : Khi thực hiện tìm kiếm nhập vào 1 trường và focus ra bên ngoài sẽ có 1 request gửi lên server
    ...    để lấy dữ liệu về, keyword này sẽ đợi request đó hoàn thành
    ...    @tuyenle
    ...    Date created: 30/03/2026
    ...
    Browser.Wait For Load State    networkidle   timeout=30s

Focus mouse out
    [Documentation]    Mô tả : di chuột, tắt các pop trong cá trường select, search...ra ngoài để tương tác với các trường khác
    ...
    ...    Author: TuyenLe
    ...
    ...    Có thể đặt ở trước keyword click nút tìm kiếm hoặc thoát trường nào đó có combobox
    ...
    ...    Date created: 28/03/2026
    ...
    Browser.Click With Options    //mat-sidenav-container    position_x=0    position_y=0    force=True

Press Key Enter
    [Documentation]    Ấn phím enter trên phím bằng cách focus vào ô input đầu tiên trong bảng filter (cho NSP)
    Browser.Focus    table[role="table"] input >> nth=0
    Browser.Press Keys    table[role="table"] input >> nth=0    Enter
    # sleep   1s

# Verify Message Toast On Nsp Page
#     [Documentation]    Mô tả : Check message toast
#     ...
#     ...    @tuyenle
#     ...    Date created: 16/04/2026
#     ...
#     [Arguments]    ${message}
#     Browser.Wait For Elements State    strong.sd-toast__title:has-text("${message}")    state=visible
#     Browser.Wait For Elements State    strong.sd-toast__title:has-text("${message}")    state=hidden

Wait For Api Search Changes on NSP Page
    [Documentation]    Mô tả : Khi thực hiện tìm kiếm nhập vào 1 trường và focus ra bên ngoài sẽ có 1 request gửi lên server
    ...    để lấy dữ liệu về, keyword này sẽ đợi request đó hoàn thành
    ...    @tuyenle
    ...    Date created: 30/03/2026
    ...
    # Browser.Wait For Request    /.*/api/v1/.*/search/
    Browser.Wait For Response    /.*/api/v1/.*/search/    timeout=180s

Check Message Toast on NSP Page
    [Documentation]    Kiểm tra thông báo "nội dung" xuất hiện
    [Arguments]    ${message}
    Browser.Wait For Elements State    div.sd-toast__body    state=visible
    Browser.Get Text    div.sd-toast__body    ==    ${message}
    # Browser.Wait For Elements State    div.sd-toast__body    state=hidden

Get total row in table on NPS Page
    [Documentation]    Trả về số dòng trong table
    ...    Author: TuyenLe
    ...    Date created: 28/03/2026
    ...    
    ${rows_count : int}    Browser.Get Element Count    tbody.mdc-data-table__content tr.c-row
    RETURN    ${rows_count}

Get str text paginator on NSP Page
    [Documentation]    Trả về chuỗi text hiển thị số dòng trong paginator
    ...    Author: TuyenLe
    ...    Date created: 28/03/2026
    ...    
    ${txt}    Browser.Get Text    div.mat-mdc-paginator-outer-container
    RETURN    ${txt}