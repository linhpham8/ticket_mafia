*** Settings ***
Documentation     Mô tả : Các keyword verify trên trang đăng nhập Real Estate Ops
...    
...    Author: TuyenLe
...    
Resource          ../../CommonKeyword/BrowserCore.resource

*** Keywords ***
Verify Login success on Login Real Estate Ops Page
    [Documentation]    Kiểm tra trang đăng nhập Real Estate Ops đã hiển thị chữ Sale Platform, có thể verify các thành phần khác
    ...    
    ...
    Browser.Wait For Elements State    //span[text()="Sales Platform"]    state=visible    timeout=60s
    