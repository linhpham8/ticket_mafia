from os import environ
from urllib import response
import requests
import json
import re
from robot.api.deco import keyword, not_keyword

token  = environ.get("QMETRY_TOKEN")
API_URL = 'https://qtmcloud.qmetry.com'

#testCycleTestCaseMapId
@not_keyword
def testCycleTestCaseMapId(testcycles, key):
    headers = {'apiKey': token,'Content-Type': 'application/json'}
    data = "{\"filter\":{\"key\":\""+ key +"\"}}"
    response_data = requests.post(API_URL+'/rest/api/latest/testcycles/'+ testcycles +'/testcases/search/', data=data, headers=headers)
    json_data = json.loads(response_data.content)

    try:
        return json_data['data'][0]['testCycleTestCaseMapId']
    except Exception as e:
        print(json.loads(response_data.content))
        print(e)
        return('null')
    # print("===================testCycleTestCaseMapId===============")

#POST Start New Execution
@not_keyword
def start_New_Execution(testcycles, key, testcyclesId):
    # testcyclesId =  testCycleTestCaseMapId(testcycles, str(key))
    headers = {'apiKey': token,'Content-Type': 'application/json'}
    data = "{\"filter\":{\"key\":\""+ key +"\"}}"

    response_data = requests.post(API_URL+'/rest/api/latest/testcycles/'+ str(testcycles) +'/testcases/'+ str(testcyclesId) +'/executions', data=data, headers=headers)
    assert response_data.status_code == 204

#Get linked Test Cases of Test Cycle
@not_keyword
def get_linked_Test_Cases_of_Test_Cycle(testcycles, key):
    headers = {'apiKey': token,'Content-Type': 'application/json'}
    data = "{\"filter\":{\"key\":\""+ key +"\"}}"
 
    response_data = requests.post(API_URL+"/rest/api/latest/testcycles/"+ testcycles +"/testcases/search/", data=data, headers=headers)
    json_data = json.loads(response_data.content)
    print("====== Get_linked_Test_Cases_of_Test_Cycle=========")
    # print(json_data)
    print(json_data['data'][0]['testCaseExecutionId'])
    return  json_data['data'][0]['testCaseExecutionId']

#Update/Delete Test Case Execution
@not_keyword
def update_Test_Case_Execution(testcycles, key, executionResultId):

    #executionId = Trạng thái của Pass/Fail
    #environmentId =  Mỗi trường chạy  Android, IOS, WEB
    #testcycles = TestCycleDetail = wgguNVjfJwGO trong URL của Test Qmetry

    executionId = get_linked_Test_Cases_of_Test_Cycle(testcycles, key)

    headers = {'apiKey': token,'Content-Type': 'application/json'}
    # data = "{\"executionResultId\":"+ str(executionResultId) +",\"environmentId\": "+ str(environmentId) +"}"
    data = "{\"executionResultId\":"+ str(executionResultId) +"}"


    print("==Update_Test_Case_Execution==")
    response_data = requests.put(API_URL+"/rest/api/latest/testcycles/"+ testcycles +"/testcase-executions/"+ str(executionId), data=data, headers=headers)
    print(response_data.text)
    print("=========Update/Delete Test Case Execution==========")
    assert response_data.status_code == 204

# Update TC1
@keyword
def qmetry_Update_Status_Testcase(testcycles, key, executionResultId, environmentId):

    """Update Test Case to Qmetry

	Arguments:
	- ``testcycles``: WMSOLUTION-TC-3252 https://imgur.com/a/9eb7Ruw
	- ``key``: Test Case ID , ex : VINE-TC-163
	- ``executionResultId``: ${TEST_STATUS} Trang thai Pass Fail cua testcase
    - ``environmentId: Môi Trường Android, IOS, WEB...
    - ``Refer : https://qmetryforjiracloud40.docs.apiary.io/#reference/test-cycle-execution/updatedelete-test-case-execution/update-comment?console=1
	"""
   
    dict_env = {}
    dict_ResultId = {}


    # WMS-TC-2815
    if "WMS-TC" in key:

        print(" ==== WMS-TC ====")

        dict_env = {
        "Android": 22951,
        "IOS" : 22951,
        "No Environment" : 19886,
        "WEB" : 22951,
        "UAT" : 22949,
        "QC" : 22950

        }
        #set Test Status

        dict_ResultId = {
            "PASS" : 98871,
            "FAIL" : 98868
        }
    
    # 1Seal
    elif "SATOS-TC" in key:

        print(" ==== 1Seal ====")

        dict_env = {
        "Android": 22951,
        "IOS" : 22951,
        "No Environment" : 19886,
        "WEB" : 22951,
        "UAT" : 22949,
        "QC" : 22950

        }
        #set Test Status

        dict_ResultId = {
            "PASS" : 77687,
            "FAIL" : 77684
        }
    #  TM1D-TR-97  B2B
    elif "TM1D-TC" in key:

        print(" ==== TMS ====")

        dict_env = {
        "Android": 22951,
        "IOS" : 22951,
        "No Environment" : 19886,
        "WEB" : 22951,
        "UAT" : 22949,
        "QC" : 22950

        }
        #set Test Status

        dict_ResultId = {
            "PASS" : 87297,
            "FAIL" : 87294
        }

  #  VInshop
    elif "PM-TC" in key:

        print(" ==== VinShop ====")

        dict_env = {
        "Android": 22951,
        "IOS" : 22951,
        "No Environment" : 19886,
        "WEB" : 22951,
        "UAT" : 22949,
        "QC" : 22950

        }
        #set Test Status

        dict_ResultId = {
            "PASS" : 75530,
            "FAIL" : 75527
        }

    #  B2B
    elif "B2B1D-TC" in key:

        print(" ==== B2B1D-TC ====")


        dict_env = {
        "Android": 22951,
        "IOS" : 22951,
        "No Environment" : 19886,
        "WEB" : 22951,
        "UAT" : 22949,
        "QC" : 22950

        }
        #set Test Status

        dict_ResultId = {
            "PASS" : 80674,
            "FAIL" : 80671
        }
    # CORE    
    elif "CORE-TC" in key:

        print(" ==== CORE-TC ====")


        dict_env = {
        "Android": 22951,
        "IOS" : 22951,
        "No Environment" : 19886,
        "WEB" : 22951,
        "UAT" : 22949,
        "QC" : 22950

        }
        #set Test Status

        dict_ResultId = {
            "PASS" : 114680,
            "FAIL" : 114677
        }
    # WMSOLUTION
    elif "WMSOLUTION-" in key:

        print(" ==== WMSOLUTION-TC ====")


        dict_env = {
        "Android": 22951,
        "IOS" : 22951,
        "No Environment" : 24107,
        "WEB" : 22951,
        "UAT" : 22949,
        "QC" : 32770

        }
        #set Test Status

        dict_ResultId = {
            "PASS" : 94073,
            "FAIL" : 94070
        }
    else:
        print("Lỗi Testcase id vui lòng kiểm tra lại")

    # print(dict_ResultId)
    
    testcyclesId = testCycleTestCaseMapId(testcycles, key)
    
    if testcyclesId != "null":
        start_New_Execution(testcycles, str(key), testcyclesId)
        
        # Chỉ update kết quả pass fail vì do nhiều project trên qmetry không cấu hình môi trường QC, uAT, android....
        update_Test_Case_Execution(testcycles, key, dict_ResultId[str(executionResultId).upper()])
        
        print("Update TC success")
    else:
        print("Error update testcase, Pls check TestcaseId and Testcycle")
    
if __name__ == "__main__":
    #Start_New_Execution() 
    #executionId = Get_linked_Test_Cases_of_Test_Cycle()
    #print(executionId)
    #Update_Test_Case_Execution(str(executionId),str(18462))
    #testCycleTestCaseMapId("wgguNVjfJwGO", "VINE-TC-163")
    #Start_New_Execution("wgguNVjfJwGO", "VINE-TC-163")
    #a = Get_linked_Test_Cases_of_Test_Cycle("wgguNVjfJwGO", "VINE-TC-163")
    #print(a)
    # qmetry_Update_Status_Testcase("dvvtqp5T7GYa", "WMSOLUTION-TC-2515", "pass", "qc")
    # st = qmetry_Update_Status_Testcase("PVVhEDau4qyY", "TM1D-TR-955", "pass", "QC")
    qmetry_Update_Status_Testcase("WMSOLUTION-TR-73", "WMSOLUTION-TC-3251", "PASS","qc")

    #print(st)
    # Update_Status_Testcase("wgguNVjfJwGO", "VINE-TC-1083", "PASS", "IOS")
    