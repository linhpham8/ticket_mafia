*** Settings ***
Resource    ../../KeywordLibraries/RealEstateOps/RealEstateOpsGeneral.resource
Resource    ../../KeywordLibraries/KeyCloak/Api_KeyCloak_Token.resource
Resource    ../../KeywordLibraries/CommonKeyword/ApiCore.resource

*** Variables ***
${username}    tuyen.le@onemount.com
${password}   123456789
# Mặc định lấy tháng 3/2026 như cũ nhưng chuyển thành biến để dễ quản lý
${START_DATE}    01/03/2026
${END_DATE}      30/03/2026

*** Test Cases ***
test_token_sale_flatform
    Api get token from Sales Platform    ${username}    ${password}
    METHOD POST    URL=https://sales-platform-qc.masterisehomes.dev/api/v1/units/search    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}    SET_BODY={"filters":[{"fieldName":"project.id","condition":"EQUALS","data":"019d42c4-5aaa-7d12-b85b-0c176286eece"}],"orders":[],"sorts":[{"fieldName":"createdAt","direction":"DESC"}],"page":0,"pageSize":20}

    
test_postgresql_query
    [Documentation]    Kiểm tra tính năng truy vấn PostgreSQL và kiểm tra dữ liệu kết quả
    [Tags]    Postgresql
    ${results}    Postgres Query Mag Sales Platform    sql_query=SELECT * FROM mst_import_file_detail LIMIT 10
    # Thêm bước kiểm chứng dữ liệu thay vì chỉ output
    Check No Empty Values    ${results}    columns=status,id
    Log Dictionary    ${results[0]}


test_menu
    [Documentation]    Kiểm tra tương tác với Sidebar Menu
    [Tags]    UI
    Open browser reusing existing browser
    # Toggle Sidebar Menu If Needed    OPEN
    # # Chờ element hiển thị thay vì sleep
    # Wait for networkidle on NSP Page
    Browser.Click    sd-button[title="Đóng"]