import oracledb
import json
from datetime import datetime
from typing import Dict, Any
import os
import logging
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn
import decimal
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CRED_PATH = os.getenv("GOOGLESPACE")

# Shared instance list
_instances = []
@library
class ExtendPssOracle:
    """Library for querying Oracle databases in PSS environment (DEV, UAT, QC)"""
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
                self.master_data_creds = creds.get("master_data_creds", {})
                self.settlement_creds = creds.get("settlement_creds", {})
                self.trans_creds = creds.get("trans_creds", {})
                self.pss_trans_log = creds.get("pss_trans_log", {})
                self.pss_mst_creds = creds.get("pss_mst_creds", {})
                self.pss_txn_creds = creds.get("pss_tnx_creds", {})
                self.pss_stlmt_creds = creds.get("pss_stlmt_creds", {})
                self.pss_aprv_creds = creds.get("pss_aprv_creds", {})
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load oracle_credentials.json: {e}")
            raise ValueError(f"File {CRED_PATH} không đúng định dạng JSON")
        except Exception as e:
            logger.error(f"Unexpected error in __init__: {e}")
            raise

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

    def _get_db_config(self, db_type: str, env: str) -> Dict[str, Any]:
        env = env.lower()
        creds = {
			"master_data": self.master_data_creds,
            "settlement": self.settlement_creds,
            "trans": self.trans_creds,
            "log": self.pss_trans_log,
            "mst" : self.pss_mst_creds,
            "txn" : self.pss_txn_creds,
            "stlmt" : self.pss_stlmt_creds,
            "aprv" : self.pss_aprv_creds
        }[db_type]
        return {
            'user': f'pss_{db_type}_{env}',
            'password': creds.get(f'pss_{db_type}_{env}', ''),
            'dsn': f"{self.HOST}:{self.PORT}/{self.SERVICE_NAME}"
        }

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
                        "type": "pss",
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
                "type": "pss",
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
                "type": "pss",
                "response": {"body": result_data},
                "ts": time.time()
            }
            self.instances.append(instance)
            logger.debug(f"Error instance created and appended: {instance}")
            logger.debug(f"Current instances: {self.instances}")
            return result_data

    # @keyword('Oracle Query Master Data v1')
    # def oracle_query_master_data_v1(self, sql_query: str) -> str:
    #     """
    #     Truy vấn cơ sở dữ liệu PSS_MASTER_DATA trong Oracle.

    #     Args:
    #         sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

    #     Returns:
    #         Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

    #     Yêu cầu:
    #         - Thư viện oracledb (`pip install oracledb`)
    #         - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
    #     """
    #     env = BuiltIn().get_variable_value('${env}', 'uat').lower()
    #     db_config = self._get_db_config("master_data", env)
    #     return self._execute_query(sql_query, db_config)
    
    @keyword('Oracle Query Master Data')
    def oracle_query_master_data(self, sql_query: str) -> str:
        """
        Truy vấn cơ sở dữ liệu PSS_MST_CREDS trong Oracle.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

        Yêu cầu:
            - Thư viện oracledb (`pip install oracledb`)
            - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
        """
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        db_config = self._get_db_config("mst", env)
        return self._execute_query(sql_query, db_config)
    
    ###############################

    # @keyword('Oracle Query Settlement v1')
    # def oracle_query_settlement_v1(self, sql_query: str) -> str:
    #     """
    #     Truy vấn cơ sở dữ liệu PSS_SETTLEMENT trong Oracle.

    #     Args:
    #         sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

    #     Returns:
    #         Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

    #     Yêu cầu:
    #         - Thư viện oracledb (`pip install oracledb`)
    #         - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
    #     """
    #     env = BuiltIn().get_variable_value('${env}', 'uat').lower()
    #     db_config = self._get_db_config("settlement", env)
    #     return self._execute_query(sql_query, db_config)
    
    @keyword('Oracle Query Settlement')
    def oracle_query_settlement(self, sql_query: str) -> str:
        """
        Truy vấn cơ sở dữ liệu PSS_STLMT_CREDS trong Oracle.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

        Yêu cầu:
            - Thư viện oracledb (`pip install oracledb`)
            - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
        """
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        db_config = self._get_db_config("stlmt", env)
        return self._execute_query(sql_query, db_config)
    
    ##################

    # @keyword('Oracle Query Transaction v1')
    # def oracle_query_trans_v1(self, sql_query: str) -> str:
    #     """
    #     Truy vấn cơ sở dữ liệu PSS_TRANS trong Oracle.

    #     Args:
    #         sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

    #     Returns:
    #         Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

    #     Yêu cầu:
    #         - Thư viện oracledb (`pip install oracledb`)
    #         - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
    #     """
    #     env = BuiltIn().get_variable_value('${env}', 'uat').lower()
    #     # env = "qc"
    #     db_config = self._get_db_config("trans", env)
    #     return self._execute_query(sql_query, db_config)


    @keyword('Oracle Query Transaction')
    def oracle_query_trans(self, sql_query: str) -> str:
        """
        Truy vấn cơ sở dữ liệu PSS_TNX_CREDS trong Oracle.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

        Yêu cầu:
            - Thư viện oracledb (`pip install oracledb`)
            - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
        """
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        # env = "qc"
        db_config = self._get_db_config("txn", env)
        return self._execute_query(sql_query, db_config)
    
    ###############

    @keyword('Oracle Query Log')
    def oracle_query_log(self, sql_query: str) -> str:
        """
        Truy vấn cơ sở dữ liệu PSS_LOG trong Oracle.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

        Yêu cầu:
            - Thư viện oracledb (`pip install oracledb`)
            - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
        """
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        # env = "qc"
        db_config = self._get_db_config("log", env)
        return self._execute_query(sql_query, db_config)

    @keyword('Oracle Query Aprv')
    def oracle_query_aprv(self, sql_query: str) -> str:
        """
        Truy vấn cơ sở dữ liệu PSS_APRV trong Oracle.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            Chuỗi JSON chứa kết quả truy vấn hoặc thông tin lỗi

        Yêu cầu:
            - Thư viện oracledb (`pip install oracledb`)
            - Biến môi trường ${env} được thiết lập trong Robot Framework (dev, uat, qc)
        """
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        # env = "qc"
        db_config = self._get_db_config("aprv", env)
        return self._execute_query(sql_query, db_config)
    
    @keyword('Check No Empty Values')
    def check_no_empty_values(self, json_result, columns) -> None:
        """
        Kiểm tra xem các cột trong kết quả có chứa giá trị empty (NULL, chuỗi rỗng, hoặc khoảng trắng) hay không.

        Args:
            json_result: List các dictionary chứa kết quả truy vấn
            columns: Danh sách các cột cần kiểm tra (nếu None, kiểm tra tất cả cột)

        Raises:
            AssertionError: Nếu tìm thấy giá trị empty trong bất kỳ cột nào
        """
        if not json_result:
            BuiltIn().log("Không có dữ liệu để kiểm tra", level="INFO")
            return

        if isinstance(json_result, list) and json_result and isinstance(json_result[0], dict) and "error" in json_result[0]:
            raise AssertionError(f"Lỗi truy vấn: {json_result[0]['error']['message']}")

        for row_idx, row in enumerate(json_result, 1):
            check_columns = columns if columns else row.keys()
            for col in check_columns:
                if col not in row:
                    raise AssertionError(f"Cột [{col}] không tồn tại trong hàng {row_idx}")
                value = row[col]
                if value is None:
                    raise AssertionError(f"Giá trị NULL được tìm thấy tại cột [{col}], hàng {row_idx}")
                if isinstance(value, str) and value.strip() == "":
                    raise AssertionError(f"Giá trị empty (chuỗi rỗng hoặc khoảng trắng) được tìm thấy tại cột [{col}], hàng {row_idx}")
        BuiltIn().log("Không tìm thấy giá trị empty trong các cột được kiểm tra", level="INFO")

# if __name__ == "__main__":
#     tt = ExtendPssOracle()
#     sql_query = "select * from TXN_TRANSACTION where sender_trans_code='TXN-20250613111155513367'"
#     # sql_query = "SELECT * FROM log_transaction WHERE transaction_code LIKE '%TXN-20250609151133259314' FETCH FIRST 1 ROWS ONLY"
#     ca = tt.oracle_query_trans(sql_query)
#     print("========================")
#     print(ca)
