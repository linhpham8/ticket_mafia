from os import environ
import requests
import json
from robot.api.deco import keyword, not_keyword

class RobotReportQmetry:
    API_URL = 'https://qtmcloud.qmetry.com'
    
    def __init__(self):
        self.headers = {'apiKey': environ.get("QMETRY_TOKEN"),'Content-Type': 'application/json'}

    @staticmethod
    def construct_data(key):
        return json.dumps({"filter": {"key": key}})
    
    @not_keyword
    def testCycleTestCaseMapId(self, testcycles, key):
        data = self.construct_data(key)
        response = requests.post(f'{self.API_URL}/rest/api/latest/testcycles/{testcycles}/testcases/search/', 
                                 data=data, headers=self.headers)
        
        try:
            response.raise_for_status()
            json_data = response.json()
            return json_data['data'][0]['testCycleTestCaseMapId']
        except (KeyError, IndexError, requests.RequestException) as e:
            print(response.text)
            print(e)
            return 'null'

    @not_keyword
    def start_New_Execution(self, testcycles, key, testcyclesId):
        data = self.construct_data(key)
        response = requests.post(f'{self.API_URL}/rest/api/latest/testcycles/{testcycles}/testcases/{testcyclesId}/executions', 
                                 data=data, headers=self.headers)
        response.raise_for_status()

    @not_keyword
    def get_linked_Test_Cases_of_Test_Cycle(self, testcycles, key):
        data = self.construct_data(key)
        response = requests.post(f'{self.API_URL}/rest/api/latest/testcycles/{testcycles}/testcases/search/', 
                                 data=data, headers=self.headers)
        response.raise_for_status()
        json_data = response.json()
        print("====== Get_linked_Test_Cases_of_Test_Cycle ========")
        print(json_data['data'][0]['testCaseExecutionId'])
        return json_data['data'][0]['testCaseExecutionId']

    @not_keyword
    def update_Test_Case_Execution(self, testcycles, key, executionResultId):
        executionId = self.get_linked_Test_Cases_of_Test_Cycle(testcycles, key)
        data = json.dumps({"executionResultId": executionResultId})
        response = requests.put(f'{self.API_URL}/rest/api/latest/testcycles/{testcycles}/testcase-executions/{executionId}', 
                                data=data, headers=self.headers)
        response.raise_for_status()
        print("=========Update/Delete Test Case Execution==========")
        print(response.text)

    @keyword
    def qmetry_Update_Status_Testcase(self, testcycles, key, executionResultId, environmentId):

        """Update Test Case to Qmetry
        Arguments:
        - ``testcycles``: WMSOLUTION-TC-3252
        - ``key``: Test Case ID, ex : VINE-TC-163
        - ``executionResultId``: ${TEST_STATUS} Trang thai Pass Fail cua testcase
        - ``environmentId``: Môi Trường Android, IOS, WEB...
        """
        project_mappings = {
            "WMS-TC": {"env": {"Android": 22951, "IOS": 22951, "No Environment": 19886, "WEB": 22951, "UAT": 22949, "QC": 22950}, 
                       "result": {"PASS": 98871, "FAIL": 98868}},
            "SATOS-TC": {"env": {"Android": 22951, "IOS": 22951, "No Environment": 19886, "WEB": 22951, "UAT": 22949, "QC": 22950}, 
                         "result": {"PASS": 77687, "FAIL": 77684}},
            "TM1D-TC": {"env": {"Android": 22951, "IOS": 22951, "No Environment": 19886, "WEB": 22951, "UAT": 22949, "QC": 22950}, 
                        "result": {"PASS": 87297, "FAIL": 87294}},
            "PM-TC": {"env": {"Android": 22951, "IOS": 22951, "No Environment": 19886, "WEB": 22951, "UAT": 22949, "QC": 22950}, 
                      "result": {"PASS": 75530, "FAIL": 75527}},
            "B2B1D-TC": {"env": {"Android": 22951, "IOS": 22951, "No Environment": 19886, "WEB": 22951, "UAT": 22949, "QC": 22950}, 
                         "result": {"PASS": 80674, "FAIL": 80671}},
            "CORE-TC": {"env": {"Android": 22951, "IOS": 22951, "No Environment": 19886, "WEB": 22951, "UAT": 22949, "QC": 22950}, 
                        "result": {"PASS": 114680, "FAIL": 114677}},
            "WMSOLUTION-": {"env": {"Android": 22951, "IOS": 22951, "No Environment": 24107, "WEB": 22951, "UAT": 22949, "QC": 32770}, 
                            "result": {"PASS": 94073, "FAIL": 94070}},
        }

        for project, mapping in project_mappings.items():
            if project in key:
                dict_env = mapping['env']
                dict_ResultId = mapping['result']
                break
        else:
            print("Lỗi Testcase id vui lòng kiểm tra lại")
            return

        testcyclesId = self.testCycleTestCaseMapId(testcycles, key)
        if testcyclesId != "null":
            self.start_New_Execution(testcycles, key, testcyclesId)
            self.update_Test_Case_Execution(testcycles, key, dict_ResultId[executionResultId.upper()])
            print("Update TC success")
        else:
            print("Error update testcase, Check TestcaseId Or Testcycle")

# if __name__ == "__main__":
#     cc = RobotReportQmetry()
#     cc.qmetry_Update_Status_Testcase("811UL36hvwM4", "B2B1D-TC-20817", "PASS","QC")