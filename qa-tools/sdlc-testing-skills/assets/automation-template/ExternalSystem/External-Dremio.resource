*** Settings ***
Library           ../Libs/dremio_api.py
Library           JSONLibrary

*** Keywords ***
Connect Mongo and Get Info
    [Arguments]    ${operation}    ${shipment}
    ${query_sql}    Set Variable    SELECT * FROM integrationLog where orderNumber='${shipment}' and operationName='${operation}'
    log    ${query_sql}
    ${kq}    Get results any database    hybris    ${query_sql}
    log    ${kq}
    ${kq1}    Get Value From Json    ${kq}    $..rows
    ${info_in_mongo}    Set Variable    ${kq1}[0][0]
    log    ${kq1}[0][0]
    RETURN    ${info_in_mongo}
