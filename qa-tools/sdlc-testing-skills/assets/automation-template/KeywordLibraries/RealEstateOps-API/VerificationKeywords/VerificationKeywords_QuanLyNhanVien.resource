*** Settings ***
Resource	../../CommonKeyword/ApiCore.resource

*** Keywords ***
Verify username from response api users create
    [Documentation]    Bóc tách username từ response api /users/create và so sánh với email
    [Arguments]    ${email}
    ${username}    REST.Output    $.data.username
    Should Be Equal    ${username}    ${email}    ignore_case=${TRUE}    msg=Username trong response không đúng với email truyền vào
