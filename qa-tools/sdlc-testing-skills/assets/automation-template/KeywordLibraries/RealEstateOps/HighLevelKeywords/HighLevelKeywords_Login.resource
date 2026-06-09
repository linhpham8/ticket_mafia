*** Settings ***
Resource    ../../RealEstateOps/LowLevelKeywords/UI_Login.resource

*** Keywords ***
Login with username and password on Login Real Estate Ops Page
    [Documentation]    Đăng nhập vào trang đăng nhập Real Estate Ops với tên đăng nhập và mật khẩu
    ...    
    [Arguments]    ${username}    ${password}
    Enter Ten Dang Nhap on Login Real Estate Ops Page    ${username}
    Enter Mat Khau on Login Real Estate Ops Page    ${password}
    Click Button Login on Login Real Estate Ops Page    
