import mysql.connector
import pymysql
import json
from datetime import datetime
from typing import Dict, Any, Union
import os
import logging
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn
import decimal

logging.basicConfig(level=logging.DEBUG)

CRED_PATH = os.getenv("GOOGLESPACE") # fix tạm GOOGLESPACE

@library
class ExtendPssTiDB:
    """Library for querying TiDB v8.5.1 database in PSS environment"""

    HOST = "pss-tidb.int.nexa.mobi"
    PORT = 4000

    def __init__(self, use_pymysql: bool = False) -> None:
        self.use_pymysql = use_pymysql
        try:
            with open(os.path.join(CRED_PATH, 'tidb_credentials.json'), 'r', encoding='utf-8') as f:
                creds = json.load(f)
                self.transaction_log_creds = creds.get("transaction_log_creds", {})
                self.audit_log_creds = creds.get("audit_log_creds", {})
        except json.JSONDecodeError:
            raise ValueError(f"File {CRED_PATH} không đúng định dạng JSON")  
        # self.transaction_log_creds = {
        #     "pss_transaction_log_dev": os.getenv("PSS_TRANS_LOG_DEV_PWD", "PFahRGrpm2Cd3SQ9zeAV7N"),
        #     "pss_transaction_log_uat": os.getenv("PSS_TRANS_LOG_UAT_PWD", "V4CcatpNRBFTY7EuGxMAHv"),
        #     "pss_transaction_log_qc": os.getenv("PSS_TRANS_LOG_QC_PWD", "RQCZmPybDAjqYVLe39gUwv")
        # }
        # self.audit_log_creds = {
        #     "pss_audit_log_dev": os.getenv("PSS_AUDIT_LOG_DEV_PWD", "Dm7YUtKh6kRNJdAjeyLqpa"),
        #     "pss_audit_log_uat": os.getenv("PSS_AUDIT_LOG_UAT_PWD", "m9CSfyA6XGNuB2QWpvVjgc"),
        #     "pss_audit_log_qc": os.getenv("PSS_AUDIT_LOG_QC_PWD", "PeKNjEMDyWBbqTavUn3trG")
        # }

    def _custom_converter(self, obj: Any) -> Union[float, str]:
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def _get_db_config(self, log_type: str, env: str) -> Dict[str, Any]:
        env = env.lower()
        creds = self.transaction_log_creds if log_type == "transaction" else self.audit_log_creds
        config = {
            'user': f'pss_{log_type}_log_{env}',
            'password': creds[f'pss_{log_type}_log_{env}'],
            'host': self.HOST,
            'port': self.PORT,
            'database': f'pss_data_log_{env}',
            'collation': 'utf8mb4_general_ci',
            'charset': 'utf8mb4'
        }
        if not self.use_pymysql:
            config['use_pure'] = True  # Vô hiệu hóa C extension
        else:
            config['cursorclass'] = pymysql.cursors.DictCursor
        # Thêm SSL nếu cần
        # config['ssl_ca'] = '/path/to/ca-certificates.crt'
        # config['ssl_verify_cert'] = True
        return config

    def _execute_query(self, sql_query, db_config):
        """Thực thi truy vấn SQL và trả về kết quả dạng JSON"""
        BuiltIn().log(f"Connecting to database: {db_config['database']}", level="INFO")
        logging.debug(f"Database config: {db_config}")
        logging.debug(f"Executing query: {sql_query}")
        
        try:
            if self.use_pymysql:
                connector = pymysql
                error_class = pymysql.MySQLError
            else:
                connector = mysql.connector
                error_class = mysql.connector.Error
                
            with connector.connect(**db_config) as connection:
                with connection.cursor(dictionary=True) as cursor:
                    print(f"Executing SQL query: {sql_query}")
                    cursor.execute(sql_query)
                    results = cursor.fetchall()
                    connection.commit()  # Đảm bảo commit
                    logging.debug(f"Query results: {results}")
                    return json.loads(json.dumps(results, default=self._custom_converter, ensure_ascii=False)) if results else []
                    # return json.dumps(results, default=self._custom_converter, ensure_ascii=False) if results else "[]"
                    
        except error_class as err:
            error_msg = f"Database Error: {err}"
            BuiltIn().log(error_msg, level="ERROR")
            logging.error(error_msg)
            return json.dumps({"error": {"message": str(err)}})

    @keyword('TiDB Query Transaction Log')
    def tidb_query_transaction_log(self, sql_query):
        env = BuiltIn().get_variable_value('${env}', 'qc').lower()
        # env = "qc"
        db_config = self._get_db_config("transaction", env)
        return self._execute_query(sql_query, db_config)

    @keyword('TiDB Query Audit Log')
    def tidb_query_audit_log(self, sql_query):
        env = BuiltIn().get_variable_value('${env}', 'qc').lower()
        # env = "qc"
        db_config = self._get_db_config("audit", env)
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

if __name__ == "__main__":
    tt = ExtendPssTiDB()
    sql_query = "SELECT * FROM transaction_log WHERE trace_no='129d6c839646f83a2b93ddfe3b796784'"

    # sql_query = "with promotion_order_rate_cte as (select trans.gt_code customerId, count(distinct IF(promo.promotion_code is not null, promo.order_code, null)) / count(distinct trans.order_code) promotion_order_rate from omd_cdp_data_from_dp_qc.DP_STAT_TRANSACTION_DAILY trans left join omd_cdp_data_from_dp_qc.DP_PROMOTION_TRANSACTION promo on trans.order_code = promo.order_code where trans.order_created_date >= '2024-12-28' and trans.order_created_date <= '2025-03-28' and trans.final_status not in ('CANCELLED', 'RETURNED_TO_WAREHOUSE') and trans.order_is_fake = false and trans.order_is_test = false group by trans.gt_code) select customer.customer_code, promotion_order_rate_cte.promotion_order_rate from omd_cdp_data_from_dp_qc.DP_CUSTOMER_GT customer left join promotion_order_rate_cte on promotion_order_rate_cte.customerId = customer.customer_code where customer.customer_code = 'DOOPS24285LmD';	"
    # ca = tt.tidb_query_transaction_log(sql_query)
    # print("========================")
    # print(ca)

    cc = tt.tidb_query_audit_log(sql_query)
    print(cc)
