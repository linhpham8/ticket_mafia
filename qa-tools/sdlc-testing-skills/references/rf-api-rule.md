---
name: rf-api-rule
description: >
  Quy tắc bắt buộc khi sinh Robot Framework keyword cho API testing từ Swagger/OpenAPI.
  Sử dụng thư viện RESTinstance (Library REST). Áp dụng cho mọi project API testing.
  Đọc file này trước khi sinh bất kỳ keyword API nào.
---

# Robot Framework — Quy Tắc Chi Tiết Keyword API (RESTinstance từ Swagger)

> Bắt buộc đọc khi sinh API keyword với thư viện `REST` (RESTinstance).
> Áp dụng cho project dùng Swagger/OpenAPI làm nguồn sinh keyword.

---

## Kiến Trúc 4 Layer

```
LowLevelKeywords/Api_TenModule.resource         ← wrapper 1 API endpoint
HighLevelKeywords/Api_TenModule_High.resource   ← Payload Builder + Flow
VerificationKeywords/Verify_Api_TenModule.resource ← assert response
{ProjectName}General-API.resource               ← hub import
```

---

## Layer 1 — LowLevel API (`Api_TenModule.resource`)

### File name
`Api_TenModule.resource` — ví dụ: `Api_QuanLyNhanVien.resource`, `Api_DuAn.resource`

### Naming convention
`Api {METHOD} {path-segments}`

Chuyển path `/api/v1/users/{user_id}` thành keyword name: `Api PUT v1 users user-id`

| Ví dụ path | Keyword name |
|---|---|
| `POST /api/v1/users/search` | `Api POST v1 users search` |
| `POST /api/v1/users` | `Api POST v1 users` |
| `GET /api/v1/users/{id}` | `Api GET v1 users user-id` |
| `PUT /api/v1/users/{id}` | `Api PUT v1 users user-id` |
| `DELETE /api/v1/users/{id}` | `Api DELETE v1 users user-id` |

### Header bắt buộc
```robot
*** Settings ***
Resource    ../../CommonKeyword/ApiCore.resource
```

### Quy tắc bắt buộc

**Authorization header — hardcode trực tiếp, KHÔNG dùng `${headers}` argument:**
```robot
# ĐÚNG:
METHOD POST    ${BASE_URL}/api/v1/users    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}

# SAI — không được truyền ${headers} làm argument:
Api POST v1 users
    [Arguments]    ${body}    ${headers}
    METHOD POST    ${BASE_URL}/api/v1/users    SET_HEADERS=${headers}    SET_BODY=${body}
```

**Body — luôn nhận qua argument `${body}`:**
```robot
Api POST v1 users
    [Arguments]    ${body}
    METHOD POST    ${BASE_URL}/api/v1/users    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}
    ...    SET_BODY=${body}
```

**Path param — nhận qua argument riêng:**
```robot
Api GET v1 users user-id
    [Arguments]    ${user_id}
    METHOD GET    ${BASE_URL}/api/v1/users/${user_id}    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}
```

### Ví dụ đầy đủ
```robot
*** Settings ***
Resource    ../../CommonKeyword/ApiCore.resource

*** Keywords ***
Api POST v1 users search
    [Arguments]    ${body}
    [Documentation]    API tìm kiếm danh sách người dùng — POST /api/v1/users/search
    ...    Arguments: ${body} — body filter
    ...
    METHOD POST    ${API_BASE_URL}/api/v1/users/search    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}
    ...    SET_BODY=${body}

Api POST v1 users
    [Arguments]    ${body}
    [Documentation]    API tạo mới người dùng — POST /api/v1/users
    ...    Arguments: ${body} — body tạo mới người dùng
    ...
    METHOD POST    ${API_BASE_URL}/api/v1/users    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}
    ...    SET_BODY=${body}

Api GET v1 users user-id
    [Arguments]    ${user_id}
    [Documentation]    API lấy thông tin chi tiết người dùng — GET /api/v1/users/{user_id}
    ...    Arguments: ${user_id} — ID người dùng
    ...
    METHOD GET    ${API_BASE_URL}/api/v1/users/${user_id}    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}

Api PUT v1 users user-id
    [Arguments]    ${user_id}    ${body}
    [Documentation]    API cập nhật người dùng — PUT /api/v1/users/{user_id}
    ...    Arguments: ${user_id} — ID người dùng
    ...    ${body} — body cập nhật
    ...
    METHOD PUT    ${API_BASE_URL}/api/v1/users/${user_id}    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}
    ...    SET_BODY=${body}

Api DELETE v1 users user-id
    [Arguments]    ${user_id}
    [Documentation]    API xóa người dùng — DELETE /api/v1/users/{user_id}
    ...    Arguments: ${user_id} — ID người dùng
    ...
    METHOD DELETE    ${API_BASE_URL}/api/v1/users/${user_id}    SET_HEADERS={"authorization":"Bearer ${nsp_token}"}
```

---

## Layer 2 — HighLevel API (`Api_TenModule_High.resource`)

HighLevel chứa **2 nhóm keyword** trong cùng 1 file:
1. **Payload Builder** — tạo dynamic body bằng `Create Dictionary`, trả về `${body}` qua `RETURN`
2. **Flow** — gọi Payload Builder + LowLevel API để thực hiện luồng nghiệp vụ

### File name
`Api_TenModule_High.resource` — ví dụ: `Api_QuanLyNhanVien_High.resource`

### Header bắt buộc
```robot
*** Settings ***
Resource    ../../../KeywordLibraries/{ProjectName}-API/LowLevelKeywords/Api_TenModule.resource
```

### Quy tắc Payload Builder

**Naming:** `Create Payload {TenEndpoint} {LoaiPayload}`
- `Create Payload Users Create`
- `Create Payload Users Search`
- `Create Payload Project Update`

**Quy tắc bắt buộc:**
- Dùng `Create Dictionary` — **KHÔNG** dùng `Library Collections` riêng lẻ
- Tham số optional dùng `${EMPTY}` hoặc `${None}` làm default
- Field optional → dùng IF để chỉ Set khi có giá trị
- Kết thúc bằng `RETURN    ${body}` — **KHÔNG** assign vào `${RESPONSE}`
- **KHÔNG** gọi API endpoint trong Payload Builder

```robot
Create Payload Users Create
    [Documentation]    Tạo dynamic body cho POST /api/v1/users
    [Arguments]    ${fullName}    ${email}    ${status}=ACTIVE    ${phoneNumber}=${None}
    &{body}    Create Dictionary
    ...    fullName=${fullName}
    ...    email=${email}
    ...    status=${status}
    IF    '${phoneNumber}' != '${None}' and '${phoneNumber}' != ''
        Set To Dictionary    ${body}    phoneNumber=${phoneNumber}
    END
    RETURN    ${body}
```

### Quy tắc Flow keyword

**Naming:** `Api {action} {TenModule} by {actor}` hoặc `Api {action} {TenModule}`
- `Api create user by admin`
- `Api search users by filter`
- `Api get user detail`

**Quy tắc bắt buộc:**
- Gọi Payload Builder trước, lấy `${body}`
- Truyền `${body}` vào LowLevel API keyword
- **KHÔNG** assign response — response được SET_VARIABLE tự động trong `ApiCore.resource`

```robot
Api create user
    [Documentation]    Luồng tạo mới người dùng
    [Arguments]    ${fullName}    ${email}    ${status}=ACTIVE    ${phoneNumber}=${None}
    ${body}    Create Payload Users Create
    ...    fullName=${fullName}    email=${email}
    ...    status=${status}    phoneNumber=${phoneNumber}
    Api POST v1 users    ${body}
```

### Ví dụ đầy đủ
```robot
*** Settings ***
Resource    ../../../KeywordLibraries/RealEstateOps-API/LowLevelKeywords/Api_QuanLyNhanVien.resource

*** Keywords ***
# ===== FLOW KEYWORDS =====

Api search users by filter
    [Documentation]    Luồng tìm kiếm người dùng theo filter
    [Arguments]    ${fullName}=${None}    ${email}=${None}    ${status}=${None}    ${page}=0    ${pageSize}=20
    ${body}    Create Payload Users Search
    ...    fullName=${fullName}    email=${email}    status=${status}
    ...    page=${page}    pageSize=${pageSize}
    Api POST v1 users search    ${body}

Api create user
    [Documentation]    Luồng tạo mới người dùng
    [Arguments]    ${fullName}    ${email}    ${status}=ACTIVE    ${phoneNumber}=${None}
    ${body}    Create Payload Users Create
    ...    fullName=${fullName}    email=${email}    status=${status}    phoneNumber=${phoneNumber}
    Api POST v1 users    ${body}

Api update user
    [Documentation]    Luồng cập nhật thông tin người dùng
    [Arguments]    ${user_id}    ${fullName}=${None}    ${status}=${None}
    ${body}    Create Payload Users Update    fullName=${fullName}    status=${status}
    Api PUT v1 users user-id    ${user_id}    ${body}

# ===== PAYLOAD BUILDER KEYWORDS =====

Create Payload Users Search
    [Documentation]    Tạo dynamic body cho POST /api/v1/users/search
    [Arguments]    ${fullName}=${None}    ${email}=${None}    ${status}=${None}
    ...    ${page}=0    ${pageSize}=20    ${sortField}=createdAt    ${sortDirection}=DESC
    ${filters}    Create List
    IF    '${fullName}' != '${None}' and '${fullName}' != ''
        ${f}    Create Dictionary    fieldName=fullName    condition=CONTAINS    data=${fullName}
        Append To List    ${filters}    ${f}
    END
    IF    '${email}' != '${None}' and '${email}' != ''
        ${f}    Create Dictionary    fieldName=email    condition=CONTAINS    data=${email}
        Append To List    ${filters}    ${f}
    END
    IF    '${status}' != '${None}' and '${status}' != ''
        ${f}    Create Dictionary    fieldName=status    condition=IN    data=['${status}']
        Append To List    ${filters}    ${f}
    END
    ${sorts}    Create List
    ${sort}    Create Dictionary    fieldName=${sortField}    direction=${sortDirection}
    Append To List    ${sorts}    ${sort}
    &{body}    Create Dictionary
    ...    filters=${filters}
    ...    sorts=${sorts}
    ...    page=${page}
    ...    pageSize=${pageSize}
    RETURN    ${body}

Create Payload Users Create
    [Documentation]    Tạo dynamic body cho POST /api/v1/users
    [Arguments]    ${fullName}    ${email}    ${status}=ACTIVE    ${phoneNumber}=${None}
    &{body}    Create Dictionary
    ...    fullName=${fullName}
    ...    email=${email}
    ...    status=${status}
    IF    '${phoneNumber}' != '${None}' and '${phoneNumber}' != ''
        Set To Dictionary    ${body}    phoneNumber=${phoneNumber}
    END
    RETURN    ${body}

Create Payload Users Update
    [Documentation]    Tạo dynamic body cho PUT /api/v1/users/{id}
    [Arguments]    ${fullName}=${None}    ${status}=${None}
    &{body}    Create Dictionary
    IF    '${fullName}' != '${None}' and '${fullName}' != ''
        Set To Dictionary    ${body}    fullName=${fullName}
    END
    IF    '${status}' != '${None}' and '${status}' != ''
        Set To Dictionary    ${body}    status=${status}
    END
    RETURN    ${body}
```

---

## Layer 3 — VerificationKeywords API (`Verify_Api_TenModule.resource`)

### File name
`VerificationKeywords_TenModule.resource` (giống UI) hoặc `Verify_Api_TenModule.resource`

### Header bắt buộc
```robot
*** Settings ***
Resource    ../../CommonKeyword/ApiCore.resource
```

### Quy tắc bắt buộc
- Dùng `REST.Output` với JSONPath để extract giá trị từ response
- Dùng `Should Be Equal` / `Should Contain` / `Should Be Equal As Integers` để assert
- Group các assertion liên quan vào 1 keyword theo context (không tách quá nhỏ)
- **KHÔNG** gọi API endpoint trong Verification keyword

### Các assertion pattern

**Verify HTTP status code:**
```robot
Output    response status
Integer    response status    200
# hoặc:
Integer    response status    201
```

**Verify field trong response body:**
```robot
${username}    REST.Output    $.data.username
Should Be Equal    ${username}    ${expected_email}    ignore_case=${TRUE}

${status}    REST.Output    $.data.status
Should Be Equal As Strings    ${status}    ACTIVE
```

**Verify array trong response:**
```robot
${count}    REST.Output    $.data.totalElements
Should Be True    ${count} > 0

${items}    REST.Output    $.data.content
Should Not Be Empty    ${items}
```

### Ví dụ đầy đủ
```robot
*** Settings ***
Resource    ../../CommonKeyword/ApiCore.resource

*** Keywords ***
Verify api create user response is success
    [Documentation]    Kiểm tra response tạo mới người dùng thành công: status 201, có username
    ...
    [Arguments]    ${email}
    Integer    response status    201
    ${username}    REST.Output    $.data.username
    Should Be Equal    ${username}    ${email}    ignore_case=${TRUE}
    ...    msg=Username trong response không khớp với email

Verify api search users has results
    [Documentation]    Kiểm tra response tìm kiếm trả về ít nhất 1 kết quả
    ...
    Integer    response status    200
    ${total}    REST.Output    $.data.totalElements
    Should Be True    ${total} > 0    msg=Tìm kiếm không trả về kết quả

Verify api get user detail
    [Documentation]    Kiểm tra response chi tiết người dùng đúng thông tin
    ...
    [Arguments]    ${expected_email}    ${expected_status}
    Integer    response status    200
    ${email}    REST.Output    $.data.email
    Should Be Equal As Strings    ${email}    ${expected_email}
    ${status}    REST.Output    $.data.status
    Should Be Equal As Strings    ${status}    ${expected_status}

Verify api response status
    [Documentation]    Kiểm tra HTTP status code của response
    ...
    [Arguments]    ${expected_status_code}
    Integer    response status    ${expected_status_code}

Verify api error message contains
    [Documentation]    Kiểm tra response error chứa thông điệp mong đợi
    ...
    [Arguments]    ${expected_message}
    ${message}    REST.Output    $.message
    Should Contain    ${message}    ${expected_message}
```

---

## Layer 4 — General Resource API (`{ProjectName}General-API.resource`)

```robot
*** Settings ***
Resource    ../../KeywordLibraries/KeyCloak/Api_KeyCloak_Token.resource
Resource    ../../KeywordLibraries/{ProjectName}-API/HighLevelKeywords/Api_QuanLyNhanVien_High.resource
Resource    ../../KeywordLibraries/{ProjectName}-API/HighLevelKeywords/Api_DuAn_High.resource
Resource    ../../KeywordLibraries/{ProjectName}-API/VerificationKeywords/VerificationKeywords_QuanLyNhanVien.resource
Resource    ../../KeywordLibraries/{ProjectName}-API/VerificationKeywords/VerificationKeywords_DuAn.resource
```

**Test case API chỉ import 1 dòng:**
```robot
Resource    ../../KeywordLibraries/{ProjectName}/{ProjectName}General-API.resource
```

---

## Test Case API (`test_Api_TenModule.robot`)

### Gen từ Swagger — nguyên tắc tổ chức
- Mỗi file `.robot` tương ứng 1 **controller/tag** trong Swagger
- Mỗi `Test Case` tương ứng 1 kịch bản kiểm thử (happy path / error path)
- Chỉ import General-API resource — không import trực tiếp High/Low/Verify

### Ví dụ đầy đủ
```robot
*** Settings ***
Resource    ../../KeywordLibraries/RealEstateOps-API/RealEstateOpsGeneral-API.resource

*** Test Cases ***
API-TC-001 Tao moi nguoi dung thanh cong
    [Documentation]    POST /api/v1/users — tạo mới người dùng với đầy đủ thông tin hợp lệ
    [Tags]    smoke    api    users    happy-path
    Api create user
    ...    fullName=Test User Autotest
    ...    email=test.auto@company.com
    ...    status=ACTIVE
    Verify api create user response is success    test.auto@company.com
    [Teardown]    Api DELETE v1 users user-id    ${RESPONSE_USER_ID}

API-TC-002 Tim kiem nguoi dung theo ten
    [Documentation]    POST /api/v1/users/search — tìm kiếm theo fullName có kết quả
    [Tags]    regression    api    users
    Api search users by filter    fullName=Test User
    Verify api search users has results

API-TC-003 Tao nguoi dung thieu email tra ve loi 400
    [Documentation]    POST /api/v1/users — thiếu email bắt buộc → 400 Bad Request
    [Tags]    regression    api    users    negative
    Api POST v1 users    ${{{"fullName": "Missing Email User"}}}
    Verify api response status    400

API-TC-004 Lay chi tiet nguoi dung theo ID
    [Documentation]    GET /api/v1/users/{id} — lấy chi tiết người dùng đã tạo
    [Tags]    regression    api    users
    Api get user detail    ${EXISTING_USER_ID}
    Verify api get user detail    expected_email=existing@company.com    expected_status=ACTIVE
```

---

## Quy Trình Gen API Script Từ Swagger (5 bước)

1. **Đọc Swagger** — Xác định controller/tag, endpoints, request schema, response schema
2. **Tạo LowLevel** — 1 keyword/endpoint, hardcode authorization header, nhận `${body}` qua argument
3. **Tạo HighLevel** — Payload Builder cho mỗi endpoint phức tạp, Flow keyword cho mỗi kịch bản nghiệp vụ
4. **Tạo Verification** — Group assertions theo context của response
5. **Cập nhật General-API + Tạo Test Case** — Import đủ, 1 file .robot/controller

---

## Checklist Trước Khi Xuất

- [ ] LowLevel: authorization hardcode trong METHOD call, không dùng `${headers}` argument
- [ ] LowLevel: naming đúng `Api {METHOD} {path-segments}`
- [ ] Payload Builder: dùng `Create Dictionary` + `RETURN`, không assign response
- [ ] Payload Builder: field optional dùng IF + `Set To Dictionary`
- [ ] Flow keyword: gọi Payload Builder trước, không gọi METHOD trực tiếp
- [ ] Verification: dùng `REST.Output` + JSONPath, group assertions hợp lý
- [ ] General-API: đã import đủ HighLevel + Verification + KeyCloak
- [ ] Test Case: chỉ import General-API resource
- [ ] Không hardcode secret/token trong test case hay keyword — dùng `${nsp_token}` từ env

---

## Tài liệu tham chiếu

- RESTinstance library docs: https://asyrjasalo.github.io/RESTinstance/
- JSONPath syntax: https://goessner.net/articles/JsonPath/
- Swagger/OpenAPI: https://swagger.io/specification/
