*** Settings ***
Resource          ../CommonKeyword/Utils.resource
Library           REST

*** Keywords ***
METHOD GET
    [Arguments]    ${URL}    ${SET_HEADERS}=${EMPTY}    ${SET_QUERY}=${EMPTY}
    [Documentation]
    ...    Arguments:
    ...        
    ...    ${URL}: URL mà yêu cầu GET sẽ được gửi đến. 
    ...    
    ...    ${SET_HEADERS}: Các header tùy chọn cho yêu cầu, mặc định là rỗng. Type : Dictionary 
    ...    
    ...    ${SET_QUERY}: Các tham số truy vấn tùy chọn cho yêu cầu, mặc định là rỗng.
    ...
    ...    Chú ý : Không nên sinh thêm log của biến ${RESPONSE} => trong keyword đã có rồi.
    ...    
    ...    ${RESPONSE} => repsone body đã được set thành biến
    ...
    REST.GET    ${URL}    headers=${SET_HEADERS}    query=${SET_QUERY}
    Output    also_console=False
    ${RESPONSE}    Output    response body    also_console=False
    Set Test Variable    ${RESPONSE}
    RETURN    ${RESPONSE}

METHOD POST
    [Arguments]    ${URL}    ${SET_HEADERS}=${EMPTY}    ${SET_BODY}=${EMPTY}
    [Documentation]
    ...    Thực hiện yêu cầu POST đến URL được cung cấp.
    ...    
    ...    Arguments:
    ...    - ${URL}: URL mà yêu cầu POST sẽ được gửi đến.
    ...    - ${SET_HEADERS}: Các header tùy chọn cho yêu cầu, mặc định là rỗng. Type = Dictionary.
    ...    - ${SET_BODY}: Nội dung body cho yêu cầu, mặc định là rỗng. Type = Dictionary.
    ...
    ...    Các trường hợp lỗi tiềm năng:
    ...    - HTTP status code >= 400: Yêu cầu không thành công, có thể do URL không tồn tại, không có quyền truy cập, hoặc lỗi máy chủ.
    ...    - Headers không hợp lệ: Ví dụ, `Content-Type` không đúng, dẫn đến lỗi 400 hoặc 415.
    ...    - Body không hợp lệ: JSON hoặc dữ liệu gửi lên không đúng định dạng.
    ...    - Timeout: Thời gian chờ phản hồi quá lâu.
    ...    - Kết nối mạng hoặc lỗi DNS: Không thể kết nối tới máy chủ hoặc phân giải tên miền.
    ...
    ...    Cách xử lý lỗi:
    ...    - Kiểm tra mã trạng thái HTTP và đưa ra thông báo lỗi phù hợp.
    ...    - Đảm bảo headers và body hợp lệ và phù hợp với API.
    ...    - Thiết lập timeout hợp lý cho yêu cầu.
    ...    - Kiểm tra kết nối mạng trước khi thực hiện yêu cầu.
    ...
    ...    Chú ý: Không nên sinh thêm log của biến ${RESPONSE} vì nó đã được quản lý trong từ khóa.
    ...    
    ...    ${RESPONSE} => Nội dung phản hồi đã được lưu trữ thành biến.
    ...    Credit by chatGPT :V
    ...    
    REST.POST    ${URL}    body=${SET_BODY}    headers=${SET_HEADERS}
    Output    also_console=False
    ${RESPONSE}    Output    response body    also_console=False
    Set Test Variable    ${RESPONSE}
    RETURN    ${RESPONSE}

METHOD PUT
    [Arguments]    ${URL}    ${SET_HEADERS}=${EMPTY}    ${SET_BODY}=${EMPTY}
    [Documentation]
    ...    Thực hiện yêu cầu PUT đến URL được cung cấp.
    ...    
    ...    Arguments:
    ...    - ${URL}: URL mà yêu cầu PUT sẽ được gửi đến.
    ...    - ${SET_HEADERS}: Các header tùy chọn cho yêu cầu, mặc định là rỗng. Type = Dictionary.
    ...    - ${SET_BODY}: Nội dung body cho yêu cầu, mặc định là rỗng. Type = Dictionary.
    ...
    ...    Các trường hợp lỗi tiềm năng:
    ...    - HTTP status code >= 400: Yêu cầu không thành công, có thể do URL không tồn tại, không có quyền truy cập, hoặc lỗi máy chủ.
    ...    - Headers không hợp lệ: Ví dụ, `Content-Type` không đúng, dẫn đến lỗi 400 hoặc 415.
    ...    - Body không hợp lệ: JSON hoặc dữ liệu gửi lên không đúng định dạng.
    ...    - Timeout: Thời gian chờ phản hồi quá lâu.
    ...    - Kết nối mạng hoặc lỗi DNS: Không thể kết nối tới máy chủ hoặc phân giải tên miền.
    ...
    ...    Cách xử lý lỗi:
    ...    - Kiểm tra mã trạng thái HTTP và đưa ra thông báo lỗi phù hợp.
    ...    - Đảm bảo headers và body hợp lệ và phù hợp với API.
    ...    - Thiết lập timeout hợp lý cho yêu cầu.
    ...    - Kiểm tra kết nối mạng trước khi thực hiện yêu cầu.
    ...
    ...    Chú ý: Không nên sinh thêm log của biến ${RESPONSE} vì nó đã được quản lý trong từ khóa.
    ...    
    ...    ${RESPONSE} => Nội dung phản hồi đã được lưu trữ thành biến.
    ...
    REST.PUT    ${URL}    body=${SET_BODY}    headers=${SET_HEADERS}
    Output    also_console=False
    ${RESPONSE}    Output    response body    also_console=False
    Set Test Variable    ${RESPONSE}
    RETURN    ${RESPONSE}

METHOD DELETE
    [Arguments]    ${URL}    ${SET_HEADERS}=${EMPTY}    ${SET_BODY}=${EMPTY}
    [Documentation]
    ...    Thực hiện yêu cầu DELETE đến URL được cung cấp.
    ...    
    ...    Arguments:
    ...    - ${URL}: URL mà yêu cầu DELETE sẽ được gửi đến.
    ...    - ${SET_HEADERS}: Các header tùy chọn cho yêu cầu, mặc định là rỗng. Type = Dictionary.
    ...    - ${SET_BODY}: Nội dung body cho yêu cầu, mặc định là rỗng. Type = Dictionary.
    ...
    ...    Các trường hợp lỗi tiềm năng:
    ...    - HTTP status code >= 400: Yêu cầu không thành công, có thể do URL không tồn tại, không có quyền truy cập, hoặc lỗi máy chủ.
    ...    - Headers không hợp lệ: Ví dụ, `Content-Type` không đúng, dẫn đến lỗi 400 hoặc 415.
    ...    - Body không hợp lệ: Nếu body không đúng định dạng hoặc không được phép, có thể dẫn đến lỗi 400 (Bad Request).
    ...    - Timeout: Thời gian chờ phản hồi quá lâu.
    ...    - Kết nối mạng hoặc lỗi DNS: Không thể kết nối tới máy chủ hoặc phân giải tên miền.
    ...
    ...    Cách xử lý lỗi:
    ...    - Kiểm tra mã trạng thái HTTP và đưa ra thông báo lỗi phù hợp.
    ...    - Đảm bảo headers và body hợp lệ và phù hợp với API.
    ...    - Thiết lập timeout hợp lý cho yêu cầu.
    ...    - Kiểm tra kết nối mạng trước khi thực hiện yêu cầu.
    ...
    ...    Chú ý: Không nên sinh thêm log của biến ${RESPONSE} vì nó đã được quản lý trong từ khóa.
    ...    
    ...    ${RESPONSE} => Nội dung phản hồi đã được lưu trữ thành biến.
    ...
    REST.Delete    ${URL}    body=${SET_BODY}    headers=${SET_HEADERS}
    Output    also_console=False
    ${RESPONSE}    Output    response body    also_console=False
    Set Test Variable    ${RESPONSE}
    RETURN    ${RESPONSE}

METHOD PATCH
    [Arguments]    ${URL}    ${SET_HEADERS}=${EMPTY}    ${SET_BODY}=${EMPTY}
    [Documentation]
    ...    Thực hiện yêu cầu PATCH đến URL được cung cấp.
    ...
    ...    Arguments:
    ...    - ${URL}: URL mà yêu cầu PATCH sẽ được gửi đến.
    ...    - ${SET_HEADERS}: Các header tùy chọn cho yêu cầu, mặc định là rỗng. Type = Dictionary.
    ...    - ${SET_BODY}: Nội dung body cho yêu cầu, mặc định là rỗng. Type = Dictionary.
    ...
    ...    Các trường hợp lỗi tiềm năng:
    ...    - HTTP status code >= 400: Yêu cầu không thành công, có thể do URL không tồn tại, không có quyền truy cập, hoặc lỗi máy chủ.
    ...    - Headers không hợp lệ: Ví dụ, `Content-Type` không đúng, dẫn đến lỗi 400 hoặc 415.
    ...    - Body không hợp lệ: JSON hoặc dữ liệu gửi lên không đúng định dạng hoặc không hợp lệ với API.
    ...    - Timeout: Thời gian chờ phản hồi quá lâu.
    ...    - Kết nối mạng hoặc lỗi DNS: Không thể kết nối tới máy chủ hoặc phân giải tên miền.
    ...
    ...    Cách xử lý lỗi:
    ...    - Kiểm tra mã trạng thái HTTP và đưa ra thông báo lỗi phù hợp.
    ...    - Đảm bảo headers và body hợp lệ và phù hợp với API.
    ...    - Thiết lập timeout hợp lý cho yêu cầu.
    ...    - Kiểm tra kết nối mạng trước khi thực hiện yêu cầu.
    ...
    ...    Chú ý: Không nên sinh thêm log của biến ${RESPONSE} vì nó đã được quản lý trong từ khóa.
    ...
    ...    ${RESPONSE} => Nội dung phản hồi đã được lưu trữ thành biến.
    ...
    REST.PATCH    ${URL}    body=${SET_BODY}    headers=${SET_HEADERS}
    Output    also_console=False
    ${RESPONSE}    Output    response body    also_console=False
    Set Test Variable    ${RESPONSE}
    RETURN    ${RESPONSE}

