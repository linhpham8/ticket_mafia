import mysql.connector
import json
from datetime import datetime
import os
from robot.api.deco import keyword, not_keyword, library
from robot.libraries.BuiltIn import BuiltIn

@library
class extend_ods:

    def __init__(self) -> None:
        self.ods_pwd = os.getenv('ODS_PWD')
        if not self.ods_pwd:
            raise EnvironmentError("Biến ODS_PWD chưa được set trong environment")

    @not_keyword
    def datetime_converter(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
    
    @keyword('ods query database')
    def ods_query_database(self, db_name: str, sql_query: str):
        """ODS query database

        Arguments:
        - Cài đặt thư viện trước : pip install mysql-connector-python -U
        - Keyword truy vấn vào database của ODS, return ra json và dùng jsonpath lấy data 
        - ``env``: lấy trong file variable lúc chạy auto
        - ``db_name``: db trong "omd_vinid_app_common_dev_main_mysql_8_omd_b2b_custom_user_qc" truyền "omd_b2b_custom_user", ko cần môi trường mà sẽ tự lấy trong lúc khởi chạy biên ENV trong robot
        - ``sql_query``: SELECT * FROM Address;
        - ``Return JSON data ``
        """
        env = BuiltIn().get_variable_value('${env}')
        
        db_config = {
            'user': 'omd_metrics_platform',
            'password': self.ods_pwd,
            'host': 'tidb.int.onemount.dev',
            'port': 4000,
            'database': f'omd_vinid_app_common_dev_main_mysql_8_{db_name}_{env}'
        }

        BuiltIn().log(message=f"Database connect name: {db_config['database']}")
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)  # Trả về dữ liệu dạng dictionary

            # Thực hiện truy vấn
            cursor.execute(sql_query)
            results = cursor.fetchall()  # Lấy tất cả dữ liệu
            # Chuyển đổi dữ liệu thành JSON
            json_data = json.loads(json.dumps(results, default=self.datetime_converter, ensure_ascii=False))
            
            return json_data

        except mysql.connector.Error as err:

            BuiltIn().log(message=f"Database Error: {err}")
            return json.loads(json.dumps({"error": {"code": err.errno, "message": err.msg}}))

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# if __name__ == "__main__":
#     tt = ExtendODS()
#     cc = tt.ods_query_database()

