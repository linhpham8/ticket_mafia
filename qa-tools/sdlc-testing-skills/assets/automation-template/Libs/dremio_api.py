from time import sleep
import requests
from os import environ, times
from robot.api.deco import keyword, not_keyword, library
from robot.api import logger
import json
from robot.libraries.BuiltIn import BuiltIn



TOKEN_DREMIO = "Bearer " + environ.get("TOKEN_DREMIO") # type: ignore
URL_DREMIO = "https://dremio.int.onemount.dev/"

headers = {
        'Authorization': '{0}'.format(TOKEN_DREMIO),
        'Content-Type': 'application/json'
        }

class dremio_api(object):
    ROBOT_AUTO_KEYWORDS = False

    @not_keyword
    def config_db_dremio(self, env, db_name):
        context_dremio = {
            f"hybris":f"b2b-{env}-mongodb-non-prod.hybris",
            f"hybris_oracle":f"b2b-hybris-{env}.HYBRIS",
            f"tms_oracle":f"tms_non_prod_{env}.BYTM_CRP",
            f"onedriver_{env}":f"mysql_dev_172_31_0_16.onedriver_{env}",
            f"merchant_service_{env}":f"mysql_dev_172_31_0_16.merchant_service_{env}",
            f"truck_platform_{env}":f"mysql_dev_172_31_0_16.truck_platform_{env}",
            f"wes_{env}_fm":f"mysql_dev_172_31_0_16.wes_{env}_fm",
            f"wes_{env}_tbs":f"mysql_dev_172_31_0_16.wes_{env}_tbs",
            f"wes_{env}_t26":f"mysql_dev_172_31_0_16.wes_{env}_t26",
            f"sales_tools_{env}":f"mysql_dev_172_31_0_16.sales_tools_{env}",
            f"omd_wms_{env}":f"mysql_dev_172_31_0_16.omd_wms_{env}",
            f"b2b_ofs_{env}":f"mysql_dev_172_31_0_16.b2b_ofs_{env}",
            f"vinshop_tracking": f"dp.omd.semantic.event_tracking",
            f"me_dev": f"dp.omd.application.dbt_dremio.me"
            }
       
        return context_dremio["{}".format(db_name)]

    @not_keyword
    def get_job_id(self, sql_cmd, context_dremio):
        url = URL_DREMIO + "/api/v3/sql"
        # print((["{0}".format(db_path).format(db_name)]))
        payload = json.dumps({
            "sql": f"{sql_cmd}",
            "context": [f"{context_dremio}"]
            })
        response = requests.request("POST", url, headers=headers, data=payload)
        BuiltIn().log(message="Dremio job id : " + response.json()['id'])
        return(response.json()['id'])

    @not_keyword
    def get_job_status(self, job_id):

        url = URL_DREMIO + "api/v3/job/{0}".format(job_id)
        payload={}
        response = requests.request("GET", url, headers=headers, data=payload)
        return(response.json()['jobState'])

    @not_keyword
    def get_job_details(self, job_id):

        url = URL_DREMIO + "apiv2/jobs-listing/v1.0/{0}/jobDetails?detailLevel=1&attempt=1".format(job_id)
        payload={}
       
        response = requests.request("GET", url, headers=headers, data=payload)
        return response.json()['failureInfo']
        
    @not_keyword
    def Get_results(self, job_id):
           
        url = URL_DREMIO + "api/v3/job/{0}/results".format(job_id)
        payload={}
       
        response = requests.request("GET", url, headers=headers, data=payload)
        jsonData = response.json()
        del jsonData['schema']
    
        return jsonData

    @not_keyword
    def _for_status(self, job_id):
        try:
    
            for i in range(20):
                print("Retry in " + str(i))
                sleep(6)
                job_state = self.get_job_status(job_id)
                if job_state in ("FAILED", "COMPLETED"):
                    break         
            # return job_state
        except Exception as er:
            print(er) 

        finally:
            return job_state

    @keyword(name="Get results any database")
    def Get_results_any_database(self, db_name, sql_cmd):

        """Get results any database

        Arguments:
        - ``DOC``: https://vinid-team.atlassian.net/wiki/spaces/1DCQC/pages/1736934132/Query+database+s+d+ng+api+dremio
        - ``env``: lấy trong file variable lúc chạy auto
        - ``db_name``: Với các db mysql thì truyền đúng tên db, với mongo hybris thì để hybris or hoặc oracle của tier để BYTM_CRP
        - Mysql : ${data} | Get results any database | wes_qc_fm | Select *
        - ex : Với Mysql trường hợp một câu query cho cả 2 db ở 2 môi trường QC và UAT có thể làm theo ví dụ này : ${data} | Get results any database | wes_${env}_fm | Select *      
        - ex : hybris mongodb : ${data} | Get results any database | hybris | Select *
        - ex : hybris oracle : ${data} | Get results any database | hybris_oracle | Select *
        - ex : Tms oracle : ${data} | Get results any database | tms_oracle | Select *
        - ``sql_cmd``: SELECT * FROM opsSapMappingProductData where productName = 'Tã quần Merries L44+6'
        - ``Return JSON data ``
        - ``Trường hợp thêm DB mới trong dremio vui long liên hệ tuyen.le để thêm trong script ``
        """

        env = BuiltIn().get_variable_value("${env}")

        context_dremio = self.config_db_dremio(env, db_name)
        job_id = self.get_job_id(sql_cmd, context_dremio)
        # print("DREMIO JOB ID : " + job_id)
        # BuiltIn().log(message="Dremio job id : " + job_id)
        job_status = self._for_status(job_id)
  
        if job_status == "COMPLETED":
            data = self.Get_results(job_id)
            return data

        elif job_status == "FAILED":
            failureInfo = self.get_job_details(job_id)
            return failureInfo

        else:
            return job_status
