*** Settings ***
Documentation     Mô tả : Các keyword thao tác trên menu
...    
...    Author: TuyenLe
Resource          ../../CommonKeyword/BrowserCore.resource

*** Keywords ***
Toggle Sidebar Menu on Real Estate Ops Page
    [Documentation]    Click icon toggle để mở hoặc đóng menu sidebar (hỗ trợ cả menu ẩn và menu hiện)
    Browser.Click    css=.c-layout-icon-toggle mat-icon

Click Menu name on menu Real Estate Ops
    [Documentation]    Click menu name on menu Real Estate Ops
    ...    
    [Arguments]    ${menu_name}
    Browser.Click    //div[text()='${menu_name}']
    Browser.Wait For Load State    networkidle   timeout=60s

Get Status Sidebar Menu
    [Documentation]    Lấy trạng thái hiện tại của menu sidebar
    ${is_opened}=    Browser.Get Element Count    css=mat-sidenav.mat-drawer-opened
    RETURN    ${is_opened}

Click Menu on NSP Page
    [Documentation]    Click Menu on NSP Page
    ...    
    [Arguments]    ${menu_name}
    Browser.Click    div.c-menu-node:has-text("${menu_name}")

Click Sub Menu on NSP Page
    [Documentation]    Click Sub Menu on NSP Page
    ...    
    [Arguments]    ${sub_menu_name}
    Browser.Click    li.c-menu-node:has-text("${sub_menu_name}")

Get Status Menu Expanded on NSP Page
    [Documentation]    Lấy trạng thái xem menu đang mở hay không

    [Arguments]    ${menu_name}
    ${is_expanded}=    Browser.Get Attribute    mat-nested-tree-node:has-text("${menu_name}")    aria-expanded
    RETURN    ${is_expanded}
    