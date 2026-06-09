import psycopg2
import psycopg2.extras
import json
from datetime import datetime
from typing import Dict, Any
import os
import logging
import decimal
import time
import base64
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CRED_PATH = os.getenv("GOOGLESPACE")

# Shared instance list
_instances = []

@library
class ExtendMagSalesPlatformPostgres:
    """Library for querying PostgreSQL database mag_sales_platform in PSS environment (DEV, UAT, QC)"""
    ROBOT_LIBRARY_SCOPE = "TEST CASE"
    
    DEFAULT_HOST = os.getenv("DB_HOST", "localhost")
    DEFAULT_PORT = int(os.getenv("DB_PORT", 5433))

    def __init__(self) -> None:
        logger.debug("Initializing ExtendMagSalesPlatformPostgres")
        self.instances = _instances
        try:
            if not CRED_PATH:
                raise ValueError("Biến môi trường GOOGLESPACE chưa được thiết lập")
                
            cred_file = os.path.join(CRED_PATH, 'postgresql_credentials.json')
            if not os.path.exists(cred_file):
                 raise FileNotFoundError(f"Không tìm thấy file credentials tại: {cred_file}")

            with open(cred_file, 'r', encoding='utf-8') as f:
                creds = json.load(f)
                self.mag_sales_platform_creds = creds.get("mag_sales_platform", {})
        except json.JSONDecodeError as e:
            logger.error(f"Failed to load postgresql_credentials.json: {e}")
            raise ValueError(f"File {cred_file} không đúng định dạng JSON")
        except Exception as e:
            logger.error(f"Unexpected error in __init__: {e}")
            raise

    def _custom_converter(self, obj: Any):
        """Converter JSON hỗ trợ Decimal, datetime, và binary data (bytea)"""
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
        if isinstance(obj, (bytes, bytearray, memoryview)):
            data = bytes(obj) if isinstance(obj, memoryview) else obj
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                return base64.b64encode(data).decode('ascii')
        raise TypeError(f"Đối tượng kiểu {type(obj)} không thể serialize thành JSON")

    def _get_db_config(self, env: str) -> Dict[str, Any]:
        """Lấy config theo cấu trúc postgresql_credentials.json và biến môi trường"""
        env = env.lower()
        db_user_key = f"mag_sales_platform_{env}"
        
        # Thử lấy Host/Port từ Robot variables trước, nếu không có thì dùng mặc định/env
        host = BuiltIn().get_variable_value('${DB_HOST}', self.DEFAULT_HOST)
        port = BuiltIn().get_variable_value('${DB_PORT}', self.DEFAULT_PORT)
        
        return {
            'host': host,
            'port': int(port),
            'dbname': db_user_key,
            'user': db_user_key,
            'password': self.mag_sales_platform_creds.get(db_user_key, ''),
        }

    def _execute_query(self, sql_query: str, db_config: Dict[str, Any]) -> Any:
        connection_info = f"{db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
        BuiltIn().log(f"Connecting to PostgreSQL database: {connection_info}", level="INFO")
        logger.debug(f"Executing query: {sql_query}")
        
        # Display query in Robot log with some styling
        print(f'*HTML* <span style="color: #2e7d32; font-weight: bold;">Executing query:</span> <code>{sql_query}</code>')
        print(f'*HTML* <span style="background: linear-gradient(to right, red, orange, yellow, green); color:black; font-weight:bold;">Executing query: {sql_query} </span>')
        sql_query = sql_query.strip().rstrip(";")
        
        try:
            with psycopg2.connect(**db_config) as connection:
                with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute(sql_query)
                    
                    # Kiểm tra xem có dữ liệu trả về không (cho các câu lệnh SELECT)
                    if cursor.description:
                        rows = cursor.fetchall()
                        results = [dict(row) for row in rows]
                    else:
                        connection.commit()
                        results = [{"message": "Query executed successfully, no rows returned"}]
                    
                    logger.debug(f"Query results count: {len(results) if isinstance(results, list) else 0}")
                    
                    json_result = json.dumps(results, default=self._custom_converter, ensure_ascii=False)
                    result_data = json.loads(json_result)
                    
                    if not result_data or result_data == []:
                        print('*WARN* Câu query trả về dữ liệu rỗng. Hãy kiểm tra lại điều kiện WHERE hoặc data.')
                    
                    self._record_instance(result_data)
                    return result_data
                    
        except psycopg2.Error as err:
            error_msg = f"PostgreSQL Error: {err}"
            return self._handle_error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in _execute_query: {e}"
            return self._handle_error(error_msg)

    def _record_instance(self, data: Any):
        """Lưu lại lịch sử response để debug hoặc dùng cho các keyword khác"""
        instance = {
            "type": "postgres",
            "response": {"body": data},
            "ts": time.time()
        }
        self.instances.append(instance)

    def _handle_error(self, error_msg: str) -> Dict[str, Any]:
        BuiltIn().log(error_msg, level="ERROR")
        logger.error(error_msg)
        result_data = {"error": {"message": error_msg}}
        self._record_instance(result_data)
        return result_data

    @keyword('Postgres Query Mag Sales Platform')
    def postgres_query_mag_sales_platform(self, sql_query: str):
        """
        Truy vấn cơ sở dữ liệu mag_sales_platform trong PostgreSQL.

        Args:
            sql_query: Chuỗi truy vấn SQL (ví dụ: SELECT * FROM table_name)

        Returns:
            List các dict hoặc dict lỗi
        """
        env = BuiltIn().get_variable_value('${env}', 'uat').lower()
        db_config = self._get_db_config(env)
        return self._execute_query(sql_query, db_config)
    
    @keyword('Check No Empty Values')
    def check_no_empty_values(self, json_result, columns=None) -> None:
        """
        Kiểm tra xem các cột trong kết quả có chứa giá trị empty (NULL, chuỗi rỗng, hoặc khoảng trắng) hay không.
        """
        if not json_result:
            BuiltIn().log("Không có dữ liệu để kiểm tra", level="INFO")
            return

        if isinstance(json_result, dict) and "error" in json_result:
            raise AssertionError(f"Lỗi truy vấn: {json_result['error']['message']}")

        # Nếu là kết quả của INSERT/UPDATE/DELETE không có row
        if isinstance(json_result, list) and len(json_result) == 1 and "message" in json_result[0]:
            return

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