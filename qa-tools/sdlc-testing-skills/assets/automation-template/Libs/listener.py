import os.path
import tempfile
from datetime import datetime, timedelta
from time import time
# from SlackEx import SlackEx,
from extend_reports import robot_report_database, jenkins_job, save_suite_results_db
import extend_google_chat as gc

from extend_qmetry import RobotReportQmetry
import pytz
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn


class listener:
    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        # self.__slack = SlackEx()
        self.__robot_report_database = robot_report_database()
        self.__BUILD_URL = os.environ['BUILD_URL']
        self.__pipeline_code = None
        self.__BUILD_NUMBER = os.environ['BUILD_NUMBER']
        self.__env = ""
        self.__robot_qmetry = RobotReportQmetry()
        # self.__jenkins_job = jenkins_job()
        # self.__save_suite_results_db = save_suite_results_db()
        self.__channel = None
        self.__mention = None
        self.__platform = None
        self.__test_type = None
        self.__app_version = None
        self.suite_data = {}
        self.current_suite = None
        self.timestamp = None
        self.__team = ""

    def end_test(self, data, result):
        '''
            Phần này cho phần update qmetry
        '''
        list_test_id = BuiltIn().get_variable_value('${testcaseID}')
        
        if list_test_id is not None:
            list_test_id = list_test_id.split(";")
            __test_cycle = BuiltIn().get_variable_value('${TESTCYCLES}')
            for _test_id in list_test_id:
                self.__robot_qmetry.qmetry_Update_Status_Testcase(
                    __test_cycle, _test_id, result.status, self.__env)
        self.__channel = BuiltIn().get_variable_value('${channel}')
        self.__mention = BuiltIn().get_variable_value('${mention}')
        self.__platform = BuiltIn().get_variable_value('${platform}')
        self.__test_type = BuiltIn().get_variable_value('${test_type}')
        self.__app_version = BuiltIn().get_variable_value('${app_version}')
        self.__team = BuiltIn().get_variable_value('${team}').upper()
        """
        Được gọi khi một test case kết thúc.
        data: Đối tượng test case (TestData).
        result: Đối tượng kết quả test case (TestResult).
        """
        if self.current_suite:
            suite_info = self.suite_data[self.current_suite]
            suite_info['total_tests'] += 1
            if result.passed:
                suite_info['test_pass'] += 1
            else:
                suite_info['test_fail'] += 1
                suite_info['failed_cases'].append(data.name)
                
    def start_suite(self, data, result):
        '''
            PIPELINE_CODE cái nầy cấu hình trong lúc chạy job trên jenkins
        '''
        self.__pipeline_code = BuiltIn().get_variable_value('${PIPELINE_CODE}')
        self.__env = BuiltIn().get_variable_value('${env}').upper()

        """
        Được gọi khi một suite bắt đầu.
        data: Đối tượng suite (SuiteData).
        result: Đối tượng kết quả suite (SuiteResult).
        """
        suite_name = data.name
        self.current_suite = suite_name

        if suite_name not in self.suite_data:
            self.suite_data[suite_name] = {
                'total_tests': 0,
                'test_pass': 0,
                'test_fail': 0,
                'failed_cases': []
            }

        if not self.timestamp:
            timezone = pytz.timezone("Asia/Ho_Chi_Minh")
            start_time = result.start_time
            if start_time:
                start_time = timezone.localize(start_time)
                self.timestamp = int(start_time.timestamp() * 1000)
                

    def end_suite(self, data, result):
        
        # if data.parent and data.parent.parent is None:
        # if data.parent is None:
        if ".robot" in str(data.source):
            # print(self.__pipeline_code)
            # Thông báo kết quả chạy trên jenkins vào slack
            # try:
            #     self.__slack.Slack_send_message(mention=BuiltIn().get_variable_value('${mention}'),
            #                                     channel=BuiltIn().get_variable_value(
            #                                         '${channel}'),
            #                                     suitename=result.name,
            #                                     messages=result.full_message,
            #                                     link=self.__BUILD_URL,
            #                                     env=self.__env,
            #                                     url_pipeline=str(self.__pipeline_code))
            #     _send = gc.extend_google_chat(google_space=BuiltIn().get_variable_value('${channel}'))
            #     _send.google_send_messages(list_mention=BuiltIn().get_variable_value('${mention}'),
            #                                      link_jenkins=self.__BUILD_URL, suitename=result.name,
            #                                      messages=result.full_message,
            #                                      env=self.__env,
            #                                      url_pipeline=str(self.__pipeline_code))
            # except Exception as err:
            #     print(err)

            # Thông báo kết quả chạy trên google chat
            try:
                # _send = gc.extend_google_chat(google_space=BuiltIn().get_variable_value('${channel}'))
                # _send.google_send_messages(list_mention=BuiltIn().get_variable_value('${mention}'),
                #                                  link_jenkins=self.__BUILD_URL, suitename=result.name,
                #                                  messages=result.full_message,
                #                                  env=self.__env,
                #                                  url_pipeline=str(self.__pipeline_code))
                _send = gc.extend_google_chat(google_space=self.__channel)
                _send.google_send_messages(list_mention=self.__mention,
                                                 link_jenkins=self.__BUILD_URL, 
                                                 suitename=data.name,
                                                 messages=result.full_message,
                                                 env=self.__env,
                                                 url_pipeline=str(self.__pipeline_code))
            except Exception as err:
                print(err)
            # cho phần report kết quả chạy trên jenkins vào data base
            # try:
            #     self.__robot_report_database.report_database(suite_env=self.__env,
            #                                                  suite_team=BuiltIn().get_variable_value('${team}'),
            #                                                  suite_name=result.name,
            #                                                  suite_msg=result.full_message,
            #                                                  suite_status=result.status,
            #                                                  jenkins_link=self.__BUILD_URL + "robot/report/report.html#totals",
            #                                                  jenkins_build_id=self.__BUILD_NUMBER,
            #                                                  platform=self.__platform,
            #                                                  test_type=self.__test_type,
            #                                                  app_version=self.__app_version)
                
                
            # except Exception as err:
            #     print(err)

            # try:
            #     team = BuiltIn().get_variable_value('${team}')
            #     if not team:
            #         team = "N/A"
            #     self.__jenkins_job.insert_job_name(os.environ['JOB_URL'], team)
                
            # except Exception as err:
            #     print(err)
            
        # """
        # Được gọi khi một suite kết thúc.
        # data: Đối tượng suite (SuiteData).
        # result: Đối tượng kết quả suite (SuiteResult).
        # """         
        # suite_name = data.name
        # if ".robot" in str(data.source):
        #     suite_info = self.suite_data[suite_name]
        #     # Gửi dữ liệu đến API

        #     payload = {
        #         'job_url': self.__BUILD_URL + "robot/report/report.html#totals",
        #         'build_number': self.__BUILD_NUMBER,
        #         'suite_name': suite_name,
        #         'job_type': self.__test_type or "N/A",
        #         'team': self.__team or "N/A",
        #         'suite_info': suite_info,
        #         'timestamp': self.timestamp
        #     }
        # try:
        #     self.__save_suite_results_db.save_suite_results(payload)
        # except Exception as err:
        #     print(err)
            
        # # Reset current_suite sau khi suite kết thúc
        # self.current_suite = None

def close(self):
        """
        Được gọi khi toàn bộ quá trình chạy test kết thúc.
        Đảm bảo tất cả suite đã được lưu.
        """
        if self.suite_data:
            logger.info("All suites have been processed.")