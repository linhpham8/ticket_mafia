*** Settings ***
Resource	../../CommonKeyword/ApiCore.resource

*** Keywords ***
Api POST v1 users search
    [Arguments]    ${body}
    [Documentation]    APi cho chức năng tìm kiếm danh sách Nhân Viên
    ...    Arguments: ${body}
    ...    
    METHOD POST    ${API_SALES_FLATFORM_OPS}/api/v1/users/search    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}
    ...    SET_BODY=${body}

Api POST v1 users
    [Arguments]    ${body}
    [Documentation]    APi cho chức năng tạo mới nhân viên
    ...    Arguments: ${body} => Body của request để tạo mới nhân viên
    ...    
    METHOD POST    ${API_SALES_FLATFORM_OPS}/api/v1/users    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}
    ...    SET_BODY=${body}

Api PUT v1 users user-id
    [Arguments]    ${user_id}    ${body}
    [Documentation]    APi cho chức năng cập nhật nhân viên
    ...    Arguments: ${user_id} => ID của nhân viên cần cập nhật
    ...    ${body} => Body của request để cập nhật nhân viên
    ...    
    METHOD PUT    ${API_SALES_FLATFORM_OPS}/api/v1/users/${user_id}    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}
    ...    SET_BODY=${body}

Api GET v1 users user-id
    [Arguments]    ${user_id}
    [Documentation]    APi cho chức năng lấy thông tin chi tiết của nhân viên
    ...    Arguments: ${user_id} => ID của nhân viên cần lấy thông tin chi tiết
    ...    
    METHOD GET    ${API_SALES_FLATFORM_OPS}/api/v1/users/${user_id}    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}