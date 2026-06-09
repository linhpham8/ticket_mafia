*** Settings ***
Resource	../../../KeywordLibraries/RealEstateOps-API/LowLevelKeywords/Api_QuanLyNhanVien.resource


*** Keywords ***

Api users search by user
    [Arguments]    ${body}
    [Documentation]    POST api/v1/users/search
    ...    Arguments: ${body} => Body của request có các filter điều kiện
    ...
    Api POST v1 users search    ${body}

Api create user by user
    [Documentation]    POST api/v1/users
    [Arguments]    ${fullName}    ${email}    ${status}=ACTIVE    ${phoneNumber}=${None}
    ${body}    Create Payload Api Users Create    fullName=${fullName}    email=${email}    phoneNumber=${phoneNumber}    status=${status}
    Api POST v1 users    ${body}


*** Keywords ***    
Create Payload Users Search
    [Documentation]    Tạo dynamic body cho api /users/search
    [Arguments]    ${fullName}=${None}      ${phoneNumber}=${None}      ${email}=${None}
    ...    ${status}=${None}
    ...    ${createdAtFrom}=${None}     ${createdAtTo}=${None}
    ...    ${createdBy}=${None}
    ...    ${modifiedAtFrom}=${None}    ${modifiedAtTo}=${None}
    ...    ${modifiedBy}=${None}
    ...    ${page}=0    ${pageSize}=20
    ...    ${sortField}=createdAt    ${sortDirection}=DESC
    
    ${filters}    Create List

    # ====================== FILTERS ======================
    IF    '${fullName}' != '${None}' and '${fullName}' != ''
        ${f}    Create Dictionary    fieldName=fullName    condition=CONTAINS    data=${fullName}
        Append To List    ${filters}    ${f}
    END

    IF    '${phoneNumber}' != '${None}' and '${phoneNumber}' != ''
        ${f}    Create Dictionary    fieldName=phoneNumber    condition=CONTAINS    data=${phoneNumber}
        Append To List    ${filters}    ${f}
    END

    IF    '${email}' != '${None}' and '${email}' != ''
        ${f}    Create Dictionary    fieldName=email    condition=CONTAINS    data=${email}
        Append To List    ${filters}    ${f}
    END

    # Status IN
    IF    '${status}' != '${None}' and '${status}' != ''
        ${f}    Create Dictionary    fieldName=status    condition=IN    data=['${status}']
        Append To List    ${filters}    ${f}
    END

    # CreatedAt BETWEEN
    IF    '${createdAtFrom}' != '${None}' and '${createdAtTo}' != '${None}'
        ${f}    Create Dictionary    fieldName=createdAt    condition=BETWEEN    data=['${createdAtFrom}', '${createdAtTo}']
        Append To List    ${filters}    ${f}
    END

    IF    '${createdBy}' != '${None}' and '${createdBy}' != ''
        ${f}    Create Dictionary    fieldName=createdBy    condition=CONTAINS    data=${createdBy}
        Append To List    ${filters}    ${f}
    END

    # ModifiedAt BETWEEN
    IF    '${modifiedAtFrom}' != '${None}' and '${modifiedAtTo}' != '${None}'
        ${f}    Create Dictionary    fieldName=modifiedAt    condition=BETWEEN    data=['${modifiedAtFrom}', '${modifiedAtTo}']
        Append To List    ${filters}    ${f}
    END

    IF    '${modifiedBy}' != '${None}' and '${modifiedBy}' != ''
        ${f}    Create Dictionary    fieldName=modifiedBy    condition=CONTAINS    data=${modifiedBy}
        Append To List    ${filters}    ${f}
    END

    # ====================== SORTS ======================
    ${sorts}    Create List
    ${sort}    Create Dictionary    fieldName=${sortField}    direction=${sortDirection}
    Append To List    ${sorts}    ${sort}

    # ====================== BODY ======================
    &{body}    Create Dictionary
    ...    filters=${filters}
    ...    orders=${{[]}}
    ...    sorts=${sorts}
    ...    page=${page}
    ...    pageSize=${pageSize}

    RETURN    ${body}

Create Payload Api Users Create 
    [Documentation]    Tạo dynamic body cho API tạo mới users POST api/v1/users 
    [Arguments]    ${fullName}=${None}    ${email}=${None}    ${status}=ACTIVE    ${phoneNumber}=${None}    

    &{body}    Create Dictionary
    ...    fullName=${fullName}
    ...    email=${email}
    ...    status=${status}

    # phoneNumber là optional → chỉ thêm vào body khi có giá trị

    IF    '${phoneNumber}' != '${None}' and '${phoneNumber}' != ''
        Set To Dictionary    ${body}    phoneNumber=${phoneNumber}
    END
    RETURN    ${body}
