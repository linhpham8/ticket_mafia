import mysql.connector
import json
from datetime import datetime
import os
from robot.api.deco import keyword, not_keyword, library
from robot.libraries.BuiltIn import BuiltIn
import decimal


data = {

    "omd_cdp_ingest_workers_dev": "J4b09PxZdpOHzlGpQLaA",
    "omd_cdp_ingest_workers_qc": "RVlFbnogNFP7iApEaSry",
}


@library
class extend_cdp:

    # def __init__(self) -> None:
    #     self.cdp_pwd = os.getenv('cdp_PWD')
    #     if not self.cdp_pwd:
    #         raise EnvironmentError("Biến cdp_PWD chưa được set trong environment")

    @not_keyword
    def custom_converter(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
    
    @keyword('cdp query database')
    def cdp_query_database(self, db_name: str, sql_query: str) -> str:
        """cdp query database

        Arguments:
        - Cài đặt thư viện trước : pip install mysql-connector-python -U
        - Keyword truy vấn vào database của cdp, return ra json và dùng jsonpath lấy data 
        - ``env``: lấy trong file variable lúc chạy auto
        - ``db_name``: db trong "omd_cdp_ingest_workers_qc" truyền "omd_cdp_ingest_workers", ko cần môi trường mà sẽ tự lấy trong lúc khởi chạy biên ENV trong robot
        - ``sql_query``: SELECT * FROM Address;
        - ``Return JSON data ``
        """
        env = BuiltIn().get_variable_value('${env}')
        # env = "qc"

        db_config = {
            'user': f'omd_cdp_ingest_workers_{env}',
            'password': data[f'omd_cdp_ingest_workers_{env}'],
            'host': 'tidb.int.onemount.dev',
            'port': 4000,
            'database': f'{db_name}_{env}'
        }
        BuiltIn().log(message=f"Database connect name: {db_config['database']}")
        print(f"Database connect name: {db_config['database']}")
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)  # Trả về dữ liệu dạng dictionary

            # Thực hiện truy vấn
            cursor.execute(sql_query)
            results = cursor.fetchall()
            if results:
                return json.loads(json.dumps(results, default=self.custom_converter, ensure_ascii=False))

            return json.dumps([])  
            
        except mysql.connector.Error as err:

            BuiltIn().log(message=f"Database Error: {err}")
            print({"error": {"code": err.errno, "message": err.msg}})
            return json.dumps({"error": {"code": err.errno, "message": err.msg}})

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

# if __name__ == "__main__":
#     tt = extend_cdp()
#     sql_query = "with promotion_order_rate_cte as (select trans.gt_code customerId, count(distinct IF(promo.promotion_code is not null, promo.order_code, null)) / count(distinct trans.order_code) promotion_order_rate from omd_cdp_data_from_dp_qc.DP_STAT_TRANSACTION_DAILY trans left join omd_cdp_data_from_dp_qc.DP_PROMOTION_TRANSACTION promo on trans.order_code = promo.order_code where trans.order_created_date >= '2024-12-28' and trans.order_created_date <= '2025-03-28' and trans.final_status not in ('CANCELLED', 'RETURNED_TO_WAREHOUSE') and trans.order_is_fake = false and trans.order_is_test = false group by trans.gt_code) select customer.customer_code, promotion_order_rate_cte.promotion_order_rate from omd_cdp_data_from_dp_qc.DP_CUSTOMER_GT customer left join promotion_order_rate_cte on promotion_order_rate_cte.customerId = customer.customer_code where customer.customer_code = 'DOOPS24285LmD';	"

#     # sql_query = "with promotion_order_rate_cte as (select trans.gt_code customerId, count(distinct IF(promo.promotion_code is not null, promo.order_code, null)) / count(distinct trans.order_code) promotion_order_rate from omd_cdp_data_from_dp_qc.DP_STAT_TRANSACTION_DAILY trans left join omd_cdp_data_from_dp_qc.DP_PROMOTION_TRANSACTION promo on trans.order_code = promo.order_code where trans.order_created_date >= '2024-12-28' and trans.order_created_date <= '2025-03-28' and trans.final_status not in ('CANCELLED', 'RETURNED_TO_WAREHOUSE') and trans.order_is_fake = false and trans.order_is_test = false group by trans.gt_code) select customer.customer_code, promotion_order_rate_cte.promotion_order_rate from omd_cdp_data_from_dp_qc.DP_CUSTOMER_GT customer left join promotion_order_rate_cte on promotion_order_rate_cte.customerId = customer.customer_code where customer.customer_code = 'DOOPS24285LmD';	"
#     cc = tt.cdp_query_database("omd_cdp_orchestration", sql_query)
#     print(cc)

