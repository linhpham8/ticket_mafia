import oracledb
import json
from datetime import datetime
from typing import Dict, Any, Union
import os
import logging
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn
import decimal
import requests
import urllib.parse
import binascii
import base64
from datetime import datetime, time
logging.basicConfig(level=logging.DEBUG)

CRED_PATH = os.getenv("GOOGLESPACE")

@library
class TemporalClient:
    
    TEMPORAL_URL = "https://pss-temporal-02.ops.nexa.mobi"

    # def __init__(self)-> None:
    #     logging.info("worrk")

    @keyword("Get Workflow Info")
    def get_workflow_info(self, query_type="WorkflowId", operator="Equals", value=None,  namespace="pss-transaction-01"):
        """
        Gửi GET request để lấy thông tin workflow từ Temporal API.

        Args:
            namespace (str): Namespace (VD: "pss-qc" - mặc định là pss)
            workflow_id (str): Workflow ID (VD: "pss_qc:HLBBVNVX:A2A:...")
        Ví dụ:
            ${data}    Get Workflow Info    query_type=WorkflowId    operator=Equals    value=EBVIVNVX:A2A:TRFACCDOM:TXN-29a57d3e47b74693a9150c431ac

        Returns:
            dict: JSON response từ server
        """
        # encoded_id = urllib.parse.quote(workflow_id, safe='')
        # query = f"`WorkflowId` STARTS_WITH \"{encoded_id}\""
        # query_encoded = urllib.parse.quote(query, safe='')
        # query_type = WorkflowId | RunId
        # operator = StartsWith | Equals to |Not Equals to | Contains |Is null | Is not null

        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        # env = "qc"
        namespace = f"{namespace}-{env}"
        # query_type = query_type
        # operator = StartsWith | Equals to |Not Equals to | Contains |Is null | Is not null

        if operator == "Equals":
            query = f'`{query_type}`="{value}"'
        else:
            logging.debug(f"Operator không hợp lệ: {operator}. Chỉ hỗ trợ 'Equals'. Vui lòng đợi người viết code cập nhật...ahihi")
        

        url = f"{self.TEMPORAL_URL}/api/v1/namespaces/{namespace}/workflows?query={query}"
        print(url)
        headers = {}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # raise nếu lỗi HTTP
        print(response.json())
        return response.json()
    
    def get_list_schedule_temporal(self, schedules="GenerateSessionScheduleWorkflowImpl", namespace="pss-transaction-01"):
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        # env = "qc"
        namespace = f"{namespace}-{env}"
        url = f"{self.TEMPORAL_URL}/api/v1/namespaces/{namespace}/schedules/{schedules}"
        headers = {}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Ném lỗi nếu HTTP status không phải 2xx
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Không thể lấy schedule từ Temporal: {e}")
        
    def find_time_slot(self, current_time, time_slots):
        try:
            current = datetime.strptime(current_time, "%H:%M:%S").time()
            for i, slot in enumerate(time_slots):
                start = datetime.strptime(slot, "%H:%M:%S").time()
                # Nếu là mốc cuối, khung giờ kéo dài đến 21:59:59 (hoặc điều chỉnh theo yêu cầu)
                if i == len(time_slots) - 1:
                    end = datetime.strptime("23:59:59", "%H:%M:%S").time()  # Có thể sửa thành "21:59:59"
                    if current >= start:
                        return slot
                else:
                    end = datetime.strptime(time_slots[i + 1], "%H:%M:%S").time()
                    if start <= current < end:
                        return slot
            return None  # Không thuộc khung giờ nào
        except ValueError as e:
            raise Exception(f"Lỗi định dạng thời gian: {e}")

    @keyword("Get Settlement Schedules")
    def get_settlement_schedules(self, schedules="GenerateSessionScheduleWorkflowImpl"):
        try:
            jsondata = self.get_list_schedule_temporal(schedules, 'pss')
            stlmt_schedules = base64.b64decode(jsondata['schedule']['action']['startWorkflow']['input']['payloads'][0]['data'])
            data_dict = json.loads(stlmt_schedules.decode('utf-8'))
            return data_dict['settlementSessionTriggerTimeOfDay']
        except Exception as e:
            raise Exception(f"Lỗi xử lý dữ liệu schedule: {e}")

    @keyword("Check Current Time In Settlement Schedule")
    def check_current_time_in_settlement_schedule(self, db_time="2025-06-17 17:01:00", schedules="GenerateSessionScheduleWorkflowImpl"):
        # Lấy khung giờ cấu hình từ Temporal
        try:
            time_slots = self.get_settlement_schedules(schedules)
        except Exception as e:
            raise Exception(f"Lỗi khi lấy settlementSessionTriggerTimeOfDay: {e}")
        
        # Giờ hiện tại
        current_time = datetime.now().strftime("%H:%M:%S")  # Ví dụ: "17:17:56"
        
        # Hàm tìm khung giờ
        def find_time_slot(time_str, slots):
            try:
                time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                for i, slot in enumerate(slots):
                    start = datetime.strptime(slot, "%H:%M:%S").time()
                    if i == len(slots) - 1:
                        end = datetime.strptime("21:59:59", "%H:%M:%S").time()
                        if time_obj >= start and time_obj <= end:
                            return slot
                    else:
                        end = datetime.strptime(slots[i + 1], "%H:%M:%S").time()
                        if start <= time_obj < end:
                            return slot
                return None
            except ValueError as e:
                raise Exception(f"Lỗi định dạng thời gian: {e}")
        
        # Tìm khung giờ cho giờ hiện tại
        current_slot = find_time_slot(current_time, time_slots)
        
        # Tìm khung giờ cho db_time
        try:
            db_time_obj = datetime.strptime(db_time, "%Y-%m-%d %H:%M:%S")
            db_time_str = db_time_obj.strftime("%H:%M:%S")  # Lấy phần giờ: "17:01:00"
            db_slot = find_time_slot(db_time_str, time_slots)
        except ValueError as e:
            raise Exception(f"Lỗi định dạng thời gian database: {e}")
        
        # Kết quả
        if current_slot:
            print(f"Giờ hiện tại {current_time} thuộc khung giờ {current_slot}")
        else:
            print(f"Giờ hiện tại {current_time} không thuộc khung giờ nào trong cấu hình")
        
        if db_slot:
            print(f"Giờ database {db_time_str} thuộc khung giờ {db_slot}")
        else:
            print(f"Giờ database {db_time_str} không thuộc khung giờ nào trong cấu hình")
        
        # So sánh khung giờ
        if current_slot == db_slot and current_slot is not None:
            # print(f"Khung giờ hiện tại ({current_slot}) GIỐNG với khung giờ từ database ({db_slot})")
            # return {"current_slot": current_slot, "db_slot": db_slot, "is_match": True}
            assert True, f"Khung giờ hiện tại ({current_slot}) GIỐNG với khung giờ từ database ({db_slot})"
        else:
            # print(f"Khung giờ hiện tại ({current_slot}) KHÁC với khung giờ từ database ({db_slot})")
            # return {"current_slot": current_slot, "db_slot": db_slot, "is_match": False}
            # return False
            assert False, f"Khung giờ hiện tại ({current_slot}) KHÁC với khung giờ từ database ({db_slot})"
# if __name__ == "__main__":
#     tt = TemporalClient()
#     ca = tt.check_current_time_in_settlement_schedule(db_time="2025-06-17 18:01:00", schedules="GenerateSessionScheduleWorkflowImpl")
#     print(ca)