*** Settings ***
Documentation     - Chủ yếu được dùng ở tầng UIKeyword, và VerificationKeyword,
...               - Có thể được dùng ở tầng HighLevelKeyword nhưng nên hạn chế
...    
Resource          WebBrowserLibraries.resource
Resource          Utils.resource

*** Keywords ***
Open Browser Reusing Existing Browser
    [Documentation]    Dùng để debug trên chính màn hình của mình, không cần phải mở thêm 1 trình duyệt mới
    ...
    ...    Chạy cái này trước run lệnh này trong CMD
    ...    
    ...    Câu lệnh CMD trong Windows:
    ...    
    ...    "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=6969 --user-data-dir="C:\temp\gdata"
    ...    
    ...    Câu lệnh Terminal trong MacOS:
    ...    
    ...    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=6969 --user-data-dir="/tmp/gdata"
    ...    
    ...    Chạy cái này trước run lệnh này trong CMD
    ...    
    ...    Author: Tuyền Lê
    ...
    Browser.Connect To Browser    wsEndpoint=http://127.0.0.1:6969/    use_cdp=${True}    timeout=5s
    ${all_pages}    Browser.Get Page Ids    ALL
    Log    Tất cả pages sau connect: ${all_pages}
    FOR    ${page_id}    IN    @{all_pages}
        Browser.Switch Page    ${page_id}
        ${url}    Browser.Get Url
        Log    Kiểm tra page ${page_id} → ${url}
        IF    'chrome://newtab-footer/' not in '${url}'
            BREAK
        END
    END


OPEN BROWSER AND DELETE COOKIES
    [Documentation]    Mở trình duyệt mới và xóa cookies, dùng để test các trường hợp liên quan đến cookies
    ...
    ...    Args: ${RUN_BROWSER} = chrome, msedge, firefox
    ...    
    ...    Author: Tuyền Lê
    ... 
    [Arguments]    ${url}=${URL}    ${testBrowser}=${RUN_BROWSER}    ${ALIAS}=a1   
    ${now}    Get Time    epoch
    ${download directory}    Join Path    ${OUTPUT DIR}    downloads_${now}
    Set Test Variable    ${download directory}
    Create Directory    ${download directory}
    Browser.New browser    channel=${testBrowser}    headless=${False}
    ...    downloadsPath=${download directory}    args=["--start-maximized"]    timeout=120s
    Browser.New context   viewport=${None}    acceptDownloads=${True}    locale=vi-VN
    Browser.New page    url=${url}    