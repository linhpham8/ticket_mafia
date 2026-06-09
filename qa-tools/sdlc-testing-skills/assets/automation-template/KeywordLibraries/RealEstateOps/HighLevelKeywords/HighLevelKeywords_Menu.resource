*** Settings ***
Resource    ../../RealEstateOps/LowLevelKeywords/UI_Menu.resource

*** Keywords ***
Toggle Sidebar Menu If Needed
    [Documentation]    Đóng hoặc mở menu sidebar tùy theo tham số truyền vào
    [Arguments]    ${action}=CLOSE
    
    # Kiểm tra trạng thái hiện tại của menu
    ${is_opened}    Get Status Sidebar Menu

    # Xử lý theo tham số truyền vào
    IF    '${action}' == 'OPEN'
        IF    ${is_opened} == 0    Toggle Sidebar Menu on Real Estate Ops Page
    ELSE IF    '${action}' == 'CLOSE'
        IF    ${is_opened} > 0    Toggle Sidebar Menu on Real Estate Ops Page
    ELSE
        Log    Action không hợp lệ. Chỉ chấp nhận OPEN hoặc CLOSE    level=WARN
    END

Go To Menu on NSP Page
    [Documentation]    Truy cập vào menu của
    ...    
    ...    Ví dụ : Go To Menu on NSP Page    menu_name=Master data    sub_menu_name=QL Nhân viên
    ...    
    ...    menu_name=${EMPTY}: Nếu không truyền tham số này thì sẽ không click menu
    ...    sub_menu_name: Nếu không truyền tham số này thì sẽ không click sub menu
    ...    

    [Arguments]    ${menu_name}    ${sub_menu_name}
    
    IF    "${menu_name}" != "${EMPTY}"
        ${status}    Get Status Menu Expanded on NSP Page    ${menu_name}
        IF    "${status}" == "false"
            Click Menu on NSP Page    ${menu_name}
        END
    END
    Click Sub Menu on NSP Page    ${sub_menu_name}
