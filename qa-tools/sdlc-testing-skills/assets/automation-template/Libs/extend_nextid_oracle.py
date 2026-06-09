import oracledb
import json
from datetime import datetime
from typing import Dict, Any
import os
import logging
from robot.api.deco import keyword, library, not_keyword
from robot.libraries.BuiltIn import BuiltIn
import decimal
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CRED_PATH = os.getenv("GOOGLESPACE")

# Shared instance list
_instances = []
@library
class ExtendNextIDOracle:
    """Library for querying Oracle databases in NextID environment (DEV, UAT, QC)"""
    ROBOT_LIBRARY_SCOPE = "TEST CASE"
    
    HOST = "10.254.136.30"
    PORT = 1521
    SERVICE_NAME = "pssnp"

    def __init__(self) -> None:
        logger.debug("Initializing ExtendPssOracle")
        self.instances = _instances
        try:
            with open(os.path.join(CRED_PATH, 'oracle_credentials.json'), 'r', encoding='utf-8') as f:
                creds = json.load(f)
                self.nid_mst_creds = creds.get("nid_mst_creds", {})
                self.nid_cus_creds = creds.get("nid_cus_creds", {})
                self.nid_core_creds = creds.get("nid_core_creds", {})
                self.nid_txn_creds = creds.get("nid_txn_creds", {})
                self.nid_log_creds = creds.get("nid_log_creds", {})
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load oracle_credentials.json: {e}")
            raise ValueError(f"File {CRED_PATH} không đúng định dạng JSON")
        except Exception as e:
            logger.error(f"Unexpected error in __init__: {e}")
            raise

    @not_keyword
    def _custom_converter(self, obj: Any):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
        if isinstance(obj, oracledb.LOB):
            try:
                data = obj.read()
                if isinstance(data, bytes):
                    try:
                        return data.decode('utf-8')
                    except UnicodeDecodeError:
                        import base64
                        return base64.b64encode(data).decode('ascii')
                return data
            except Exception as e:
                logger.error(f"Lỗi khi đọc LOB: {e}")
                return str(obj)
        raise TypeError(f"Đối tượng kiểu {type(obj)} không thể serialize thành JSON")
    
    @not_keyword
    def _get_db_config(self, db_type: str, env: str) -> Dict[str, Any]:
        env = env.lower()
        creds = {
			"mst": self.nid_mst_creds,
            "cus": self.nid_cus_creds,
            "core": self.nid_core_creds,
            "txn" : self.nid_txn_creds,
            "log" : self.nid_log_creds
        }[db_type]
        return {
            'user': f'nid_{db_type}_{env}',
            'password': creds.get(f'nid_{db_type}_{env}', ''),
            'dsn': f"{self.HOST}:{self.PORT}/{self.SERVICE_NAME}"
        }
    
    @not_keyword
    def _execute_query(self, sql_query: str, db_config: Dict[str, Any]) -> Any:
        BuiltIn().log(f"Connecting to Oracle database: {db_config['user']}", level="INFO")
        logger.debug(f"Database config: {db_config}")
        logger.debug(f"Executing query: {sql_query}")
        print(f"*HTML* <b style=\"background-color:Violet;\">Executing query:</b> {sql_query}")
        sql_query = sql_query.strip(";")
        try:
            with oracledb.connect(**db_config) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    columns = [col[0].lower() for col in cursor.description] if cursor.description else []
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    connection.commit()
                    logger.debug(f"*HTML* <b><red>Query results<red></b>: {results}")
                    json_result = json.dumps(results, default=self._custom_converter, ensure_ascii=False) if results else "[]"
                    if json.loads(json_result) == []:
                        print('*WARN* Câu query trả về dữ liệu rỗng, vui lòng kiểm tra lại câu query hoặc cấu hình sleep phù hợp')
                    else:
                        print(f"Số dòng trả về: {len(json.loads(json_result))}")
                    
                    logger.debug(f"JSON result before instance creation: {json_result}")
                    # print(f"JSON result: {json_result}")
                    result_data = json.loads(json_result)
                    instance = {
                        "type": "nextid",               # thêm type để phân biệt
                        "response": {"body": result_data},
                        "ts": time.time()
                    }
                    self.instances.append(instance)
                    logger.debug(f"Instance created and appended: {instance}")
                    logger.debug(f"Current instances: {self.instances}")
                    return result_data
        except oracledb.Error as err:
            error_msg = f"Database Error: {err}"
            BuiltIn().log(error_msg, level="ERROR")
            logger.error(error_msg)
            json_error = json.dumps({"error": {"message": str(err)}})
            result_data = json.loads(json_error)
            instance = {
                "type": "nextid",               # thêm type để phân biệt
                "response": {"body": result_data},
                "ts": time.time()
            }
            self.instances.append(instance)
            logger.debug(f"Error instance created and appended: {instance}")
            logger.debug(f"Current instances: {self.instances}")
            return result_data
        except Exception as e:
            error_msg = f"Unexpected error in _execute_query: {e}"
            BuiltIn().log(error_msg, level="ERROR")
            logger.error(error_msg)
            json_error = json.dumps({"error": {"message": str(e)}})
            result_data = json.loads(json_error)
            instance = {
                "type": "nextid",               # thêm type để phân biệt
                "response": {"body": result_data},
                "ts": time.time()
            }
            self.instances.append(instance)
            logger.debug(f"Error instance created and appended: {instance}")
            logger.debug(f"Current instances: {self.instances}")
            return result_data


    @keyword('Nid Oracle Query Master')
    def nid_oracle_query_master(self, sql_query: str) -> str:
        """
        Truy vấn cơ sở dữ liệu NID_MST trong Oracle.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

        Yêu cầu:
            - Thư viện oracledb (`pip install oracledb`)
            - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
        """
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        # env = "uat"
        db_config = self._get_db_config("mst", env)
        return self._execute_query(sql_query, db_config)
    
    ###############################

    @keyword('Nid Oracle Query Customer')
    def nid_oracle_query_customer(self, sql_query: str) -> str:
        """
        Truy vấn cơ sở dữ liệu NID_CUS trong Oracle.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

        Yêu cầu:
            - Thư viện oracledb (`pip install oracledb`)
            - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
        """
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        # env = "dev"
        db_config = self._get_db_config("cus", env)
        return self._execute_query(sql_query, db_config)
    
    ##################

    @keyword('Nid Oracle Query Transaction')
    def nid_oracle_query_transaction(self, sql_query: str) -> str:
        """
        Truy vấn cơ sở dữ liệu NID_TNX trong Oracle.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

        Yêu cầu:
            - Thư viện oracledb (`pip install oracledb`)
            - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
        """
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        # env = "dev"
        db_config = self._get_db_config("txn", env)
        return self._execute_query(sql_query, db_config)
    
    ###############

    @keyword('Nid Oracle Query Log')
    def nid_oracle_query_log(self, sql_query: str) -> str:
        """
        Truy vấn cơ sở dữ liệu NID_LOG trong Oracle.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

        Yêu cầu:
            - Thư viện oracledb (`pip install oracledb`)
            - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
        """
        # env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        env = "qc"
        db_config = self._get_db_config("log", env)
        return self._execute_query(sql_query, db_config)

    @keyword('Nid Oracle Query Core')
    def nid_oracle_query_core(self, sql_query: str) -> str:
        """
        Truy vấn cơ sở dữ liệu NID_CORE trong Oracle.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

        Yêu cầu:
            - Thư viện oracledb (`pip install oracledb`)
            - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
        """
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        # env = "dev"
        db_config = self._get_db_config("core", env)
        return self._execute_query(sql_query, db_config)    


# if __name__ == "__main__":
#     tt = ExtendNextIDOracle()
#     sql_query = "SELECT * FROM LOG_AUDIT where id=39;"
#     # sql_query = "SELECT * FROM log_transaction WHERE transaction_code LIKE '%TXN-20250609151133259314' FETCH FIRST 1 ROWS ONLY"
#     ca = tt.nid_oracle_query_log(sql_query)
#     print("========================")
#     print(ca)
