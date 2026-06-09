*** Settings ***
Documentation     - Chủ yếu được dùng ở tầng UIKeyword, và VerificationKeyword,
...               - Có thể được dùng ở tầng HighLevelKeyword nhưng nên hạn chế
Resource          WebBaseLibraries.resource
Resource          Utils.resource


*** Keywords ***
Scroll Page To Location
    [Arguments]    ${x_location}    ${y_location}
    Sleep    2s
    SeleniumLibrary.Execute JavaScript    window.scrollTo(${x_location},${y_location})
    Sleep    2s

WEB-Press Enter Key
    [Arguments]    ${locator}
    SeleniumLibrary.Wait Until Element Is Visible    ${locator}
    SeleniumLibrary.Press Keys    ${locator}    ENTER

WEB-Clear Field Of Characters
    [Arguments]    ${locator}    ${character_count}
    [Documentation]    This keyword pushes the delete key (ascii: \8) a specified number of times in a specified field.
    FOR    ${index}    IN RANGE    ${character_count}
        SeleniumLibrary.Press Key    ${locator}    \\8
    END

WEB-Press Tab Key
    [Arguments]    ${locator}
    [Documentation]    Refer ascii at: https://en.wikipedia.org/wiki/ASCII
    SeleniumLibrary.Press Key    ${locator}    \\09    #Tab

Press Enter Key
    [Arguments]    ${locator}=None
    [Documentation]    Refer ascii at: https://en.wikipedia.org/wiki/ASCII
    SeleniumLibrary.Press Keys    ${locator}    ENTER    #Tab

WEB-Get Number of Open Tabs
    [Documentation]    Get number of open tabs
    @{windows}    SeleniumLibrary.Get Window Handles
    ${number_of_tabs}=    Get Length    ${windows}
    RETURN    ${number_of_tabs}

Switch Browser Tab By Index
    [Arguments]    ${tab_index}=1
    [Documentation]    Lựa chọn tab trình duyệt theo chỉ số (bắt đầu từ 0 tức là tab màn hình hiện tại)
    @{windows}    SeleniumLibrary.Get Window Handles
    SeleniumLibrary.Switch window    ${windows}[${tab_index}]

Switch To New Browser Tab
    [Documentation]    Chọn tab mới mở ra
    SeleniumLibrary.Switch window    NEW

Switch To Browser Tab By Title
    [Arguments]    ${title}
    [Documentation]    Chọn tab mới mở ra theo tiêu đề
    SeleniumLibrary.Switch window    ${title}

WEB-Press Keys
    [Arguments]    ${locator}    ${keys}
    [Documentation]    Arguments:
    ...    [ locator=None | *keys ]
    SeleniumLibrary.Press Keys    ${locator}    ${keys}    #Tab

WEB-Get All Texts
    [Arguments]    ${locator}
    SeleniumLibrary.Wait Until Page Contains Element    ${locator}
    SeleniumLibrary.Scroll Element Into View    ${locator}
    SeleniumLibrary.Wait Until Element Is Visible    ${locator}
    ${text}    get all texts    ${locator}
    RETURN    ${text}

OPEN BROWSER AND DELETE COOKIES
    [Arguments]    ${url}=${URL}    ${testBrowser}=${RUN_BROWSER}    ${ALIAS}=a1
    log    ${TEMPDIR}
    SeleniumLibrary.Open Browser    ${url}    ${testBrowser}    alias=${ALIAS}    options=add_argument("--window-size=1920,1048");add_argument("--window-position=0,0");add_experimental_option("prefs", {"credentials_enable_service" : False, "profile.password_manager_enabled": False, "profile.password_manager_leak_detection": False });add_experimental_option("detach", True)     #remote_url=${REMOTE_URL}
    
OPEN BROWSER AND CONFIG DOWNLOAD FILE
    [Arguments]    ${url}=${URL}
    [Documentation]    Mô tả : Mở trình duyệt và download đường dẫn trong biến ${download_directory}, biến ${download_directory} được set test varibale => gọi ra là biết thư mục nằm ở đâu
    ...
    ...    Chrome only
    ...
    ...    Author: TuyenLe
    ...
    ...    Date created: 15:43 26/05/2023
    ${now}    Get Time    epoch
    ${download directory}    Join Path    ${OUTPUT DIR}    downloads_${now}
    Set Test Variable    ${download directory}
    Create Directory    ${download directory}
    ${chrome options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    ${disabled}    Create List    Chrome PDF Viewer
    Call Method    ${chrome options}    add_argument    --start-maximized
    ${prefs}    Create Dictionary    download.default_directory=${download directory}    plugins.plugins_disabled=${disabled}    credentials_enable_service=${False}   profile.password_manager_enabled=${False}    profile.password_manager_leak_detection=${False}
    Call Method    ${chrome options}    add_experimental_option    prefs    ${prefs}
    Call Method    ${chrome options}    add_experimental_option    detach    ${True}
    SeleniumLibrary.Open browser    url=${URL}    browser=Chrome    options=${chrome options}

Open browser reusing existing browser
    [Arguments]    ${testBrowser}=${RUN_BROWSER}
    [Documentation]    Vùi lòng cập nhật thư viện bằng lên bên dưới cho lần đầu tiên

    ...
    ...    Chạy cái này trước run lệnh này trong CMD
    ...
    ...    "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=6969 --user-data-dir="C:\temp\gdata"
    ...
    ...    Sửa biến trong trong ride hoặc VScode
    ...
    ...    ${webDebug} = true \ \ ==> sử dụng trình duyệt đang mở hiện tại
    ...
    ...    ${webDebug} = false ==> chạy auto như bình thường ở trình duyệt mở với lện CMDh ở trên
    ...    
    SeleniumLibrary.Open browser    ${EMPTY}    ${testBrowser}    options=add_experimental_option("debuggerAddress","127.0.0.1:6969")

OPEN BROWSER AND DELETE COOKIES AGENT
    [Arguments]    ${url}=${URL}    ${testBrowser}=${RUN_BROWSER}    ${arg_agent}=${None}
    log    ${TEMPDIR}
    SeleniumLibrary.Open Browser    ${url}    ${testBrowser}    options=add_argument("--user-agent=${arg_agent}");add_argument("--start-maximized");add_experimental_option("detach", True)    #remote_url=${REMOTE_URL}
