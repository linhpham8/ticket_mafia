*** Settings ***
Documentation     Mô tả : Các keyword thao tác trên trang đăng nhập Real Estate Ops
...    
...    Author: TuyenLe
Resource          ../../CommonKeyword/BrowserCore.resource

*** Keywords ***
Enter Ten Dang Nhap on Login Real Estate Ops Page
    [Documentation]    Nhập tên đăng nhập vào ô username trên trang đăng nhập Real Estate Ops
    ...
    [Arguments]    ${username}
    Browser.Fill Text    id=username    ${username}

Enter Mat Khau on Login Real Estate Ops Page
    [Documentation]    Nhập mật khẩu vào ô password trên trang đăng nhập Real Estate Ops
    ...
    [Arguments]    ${password}
    Browser.Fill Text    id=password    ${password}

Click Button Login on Login Real Estate Ops Page
    [Documentation]    Click nút đăng nhập trên trang đăng nhập Real Estate Ops
    ...
    Browser.Click    id=kc-login


Click login Dang Nhap voi Google on Login Real Estate Ops Page
    [Documentation]    Click nút đăng nhập với Google trên trang đăng nhập Real Estate Ops
    ...
    Browser.Click    id=social-google

Click Dang Nhap voi SSO Microsoft on Login Real Estate Ops Page
    [Documentation]    Click nút đăng nhập với SSO Microsoft trên trang đăng nhập Real Estate Ops
    ...
    Browser.Click    id=social-microsoft