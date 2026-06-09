*** Settings ***
Library           ../../Libs/extend_keycloak.py

*** Keywords ***
Api get token from Sales Platform
    [Arguments]    ${username}    ${password}
    [Documentation]    Mô tả : Lấy token của Member Portal từ KeyCloak
	...    
	...    Author: TuyenLe
	...
	...    Date created: 19:03 15/10/2025
	...    
	...	    Arguments: ${username} : Tên đăng nhập | ${password} : Mật khẩu
	...		    
	...	    Return: ${nsp_token} : Token của Member Portal
	...	
    ${nsp_token}    Get Token From Keycloak    estate-operation    ${username}    ${password}
	Set Test Variable    ${nsp_token}