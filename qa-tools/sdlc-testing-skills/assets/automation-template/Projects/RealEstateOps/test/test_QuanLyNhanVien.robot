*** Settings ***


Resource    ../../../KeywordLibraries/RealEstateOps-API/RealEstateOpsGeneral-API.resource
*** Variables ***
${username}    tuyen.le@onemount.com
${password}   123456789

*** Test Cases ***
tc_01_get_user_success
    [Documentation]    Kiểm tra tính năng lấy danh sách nhân viên thành công
    Api get token from Sales Platform    ${username}    ${password}
    ${body}    Create Payload Users Search
    Api users search by user    ${body}

tc_02_create_user_success
    [Documentation]    Kiểm tra tính năng tạo mới nhân viên thành công
    Api get token from Sales Platform    ${username}    ${password}
    ${fullName}    Get Random String
    ${email}    Set Variable    ${fullName}@yopmail.com
    Api create user by user    fullName=${fullName}    email=${email}
    Verify username from response api users create    ${email}
