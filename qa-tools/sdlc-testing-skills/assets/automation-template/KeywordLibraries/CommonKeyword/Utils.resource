*** Settings ***
Resource          CommonVariable.resource
Library           DateTime
Library           JSONLibrary
Library           ../../Libs/MyLibrary.py
Library           ../../Libs/ConnectKafka.py
Library           ../../Libs/extend_nsp_postgresql.py
Library           ../../Libs/database_output.py
Library           OperatingSystem
Library           String
Library           Collections
Library           yaml
Library           XML
Library           Process
Library           CSVLibrary
Library           SSHLibrary
Library           ExcellentLibrary

*** Keywords ***
Get Random Quantity from 1 to 9
    ${randomNumber}    Get Random Number In Range    1    9
    RETURN    ${randomNumber}

Get random item in List
    [Arguments]    ${list}
    [Documentation]    Lấy ngẫu nhiên một item trong list
    ...
    ...    Argments : ${list}
    ...
    ...    Return ${item}
    ${item}    Evaluate    random.choice(${list})    random
    RETURN    ${item}

Get Random String
    [Arguments]    ${length}=8
    [Documentation]    Platform : ALL
    ...
    ...    Mô tả : Ngẫu nhiên 8 ký từ \ tự từ A-Z (mặc định là 8)
    ...
    ...    Return : ${str}
    ${str}    Generate Random String    ${length}    [LETTERS]
    #${str}    Set Variable    ${rnd}
    RETURN    ${str}

Get Random Number
    [Arguments]    ${length}=8
    [Documentation]    Platform : ALL
    ...
    ...    Mô tả : Ngẫu nhiên N ký từ 0123456789
    ...
    ...    Return : ${str}
    ${str}    Generate Random String    ${length}    123456789
    #${str}    Set Variable    ${rnd}
    RETURN    ${str}

Get Day after increase days
    [Arguments]    ${increase_day}=0
    [Documentation]    Tăng số lượng ngày tương ứng
    ${date} =    Get Current Date    result_format=datetime    exclude_millis=${TRUE}
    ${date} =    Add Time To Date    ${date}    ${increase_day} days    result_format=%d
    RETURN    ${date}

Get Month after increase days
    [Arguments]    ${increase_day}=0
    [Documentation]    Tăng số lượng ngày tương ứng rồi lấy ra tháng
    ${date} =    Get Current Date    result_format=datetime    exclude_millis=${TRUE}
    ${date} =    Add Time To Date    ${date}    ${increase_day} days    result_format=%m
    RETURN    ${date}

Get Year after increase days
    [Arguments]    ${increase_day}=0
    [Documentation]    Tăng số lượng ngày tương ứng rồi lấy ra năm
    ${date} =    Get Current Date    result_format=datetime    exclude_millis=${TRUE}
    ${date} =    Add Time To Date    ${date}    ${increase_day} days    result_format=%Y
    RETURN    ${date}


Get DateTime
    [Arguments]    ${date_format}=%Y-%m-%d %H:%M:%S
    ${dateTime}    Get Current Date    result_format=${date_format}
    RETURN    ${dateTime}

Get DateTime and Add day
    [Arguments]    ${day}    ${date_format}=%Y-%m-%d %H:%M:%S
    [Documentation]    ${day} | ${date_format}=%Y-%m-%d %H:%M:%S
    ${dt}    Get Current Date    result_format=%Y-%m-%d %H:%M:%S.%f
    ${addDay}    Add Time To Date    ${dt}    ${day} days
    ${dateTime}    Convert Date    ${addDay}    result_format=${date_format}
    RETURN    ${dateTime}


Get DateTime and Subtract day
    [Arguments]    ${day}    ${date_format}=%Y-%m-%d %H:%M:%S
    [Documentation]    ${day} | ${date_format}=%Y-%m-%d %H:%M:%S
    ${dt}    Get Current Date    result_format=%Y-%m-%d %H:%M:%S.%f
    ${subDay}    Subtract Time From Date    ${dt}    ${day} days
    ${dateTime}    Convert Date    ${subDay}    result_format=${date_format}
    RETURN    ${dateTime}

Catenate a string to each item in list
    [Arguments]    ${list}    ${string}
    ${newlist}    create list
    FOR    ${i}    IN ZIP    ${list}
        ${i}    Set variable    ${i}${string}
        Append to list    ${newlist}    ${i}
    END
    Log    ${newlist}
    Return from keyword    ${newlist}

Get list key or value from dictionary YAML
    [Arguments]    ${expression}    ${k_or_v}
    ${list}    Set variable    ${expression}
    ${list}    Evaluate    list(${expression}.${k_or_v}())
    Return from keyword    ${list}