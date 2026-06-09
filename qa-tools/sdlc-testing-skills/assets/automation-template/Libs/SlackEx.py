import os
from typing import List, Pattern
from aiohttp import client
# import slack
import glob
import time
import json
import re

from slack_sdk import WebClient

# from slack_sdk.errors import SlackApiError
# channel ='US1T56XV3'
# https://github.com/slackapi/python-slack-sdk

class SlackEx:

    def __init__(self):
        self.conn = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
        # return client

    # US1T56XV3
    # bot-auto-reports

    def get_mentions(self, mentions: list): 

        list_mentions = ''
        for mention in mentions:
            list_mentions += '<@' + mention + '>' + ' '
        
        return list_mentions

    def get_pipeline(self, url_pipeline):

        pipeline_code = url_pipeline.rsplit('/', 1)[-1]
        return "<"+ url_pipeline +"|#"+ pipeline_code +">"

    def Slack_send_message(self, mention, channel, suitename, messages, link, env, url_pipeline="123"):
        """Send report to slack

        Arguments:
        - ``mention``: US1T56XV3;US1T56AA
        - ``channel``: US1T56XV3 or #bot-auto-reports 
        - ``message``: Pass Fail In robotframework 
        - ``groupID``: groupid of room chat or slack which we want to send msg
        - ``suitename``: ${SUITE_NAME} global variable of Robotframework
        - ``msg``: message which we want to put in group chat
        - ``link``: link to log file
        """
        list_mention = ''

        item = mention.split(';')
        mention_length = len(item)

        for i in range(mention_length):
            list_mention += '<@' + item[i] + '>' + ' '

        if re.findall("\s0 failed", messages):
            print("Pass")
            msg = f"{messages}"
            setColor = "#00D9C0"
        else:
            msg = f"`{messages}`"
            setColor = "#FF4365"

        # if "." in suitename:
        #     # suitename = suitename.rsplit(".", 2)[1]
        #     # suitename = suitename[9:]
        #     suitename = suitename.replace('B2B-Autotest.','').replace('Projects.','')
        #     # suitename = suitename[suitename.index(".") + 1:]
        if url_pipeline == "123":
            pipeCode = ""
        elif "http" in url_pipeline:
            pipeCode = self.get_pipeline(url_pipeline)
        else:
            pipeCode = url_pipeline

        client = self.conn
        response = client.chat_postMessage(
            channel=channel,
            # text='>Xin mời ' + list_mention + ' kiểm tra kết quả ' + ' \n ' + suitename + ' \n ' + sendMesage + ' \n ' + link
            text='Xin mời ' + list_mention + ' kiểm tra kết quả ',
            attachments=[
                {
                "color" : setColor,
                "fields":          
                    [
                        {"title": "TEST SUITE", "value": "" + suitename + "", "short": True},
                        {"title": "PIPELINE", "value": "" + pipeCode + "", "short": True},
                        {"title": "ENVIRONMENT", "value": "`" + str(env.upper()) + "`", "short": True},
                        {"title": "TEST RESULT", "value": "" + msg + "", "short": True},
                        {"title": "TEST DETAIL", "value": "" + link + "robot/report/report.html#totals", "short": False}
                    ],
                "footer": "Automation Team",
                "footer_icon": "https://i.imgur.com/UBzfS6M.png",    
                }           

            ]
        )

        return response
        # print(str(response))

# sl = SlackEx()
# sl.Slack_send_message("U01AZ78JECR", "C02CVHJ297E", "Projects.API.TMSPartnerPortal.Driver", "3 tests, 2 passed, 0 failed", "C:\\", "link", "1373769")

# def get_code_pipeline():

#     s1 = 'https://gitlab.id.vin/tms/tier1/tier1-bff-partner/-/pipelines/1373769'


#     st1 = s[s.index(".") - 1::]

#     index = s.rfind('/')
#     st2 = s[index+1:]
#     s = s.rsplit('/', 1)[-1]
#     print(st1)
#     print(st2)
#     print(s)

# if __name__ == "__main__":

    # a = get_pipeline_code('https://gitlab.id.vin/tms/tier1/tier1-bff-partner/-/pipelines/1373769')
    # print(a[0])
    # pathIMG = Slack_File_and_Message("U01AZ78JECR", "TM1D-01 Smoke API Flow", "D:\\", "D:\\", "link")

    # _list = ['U01AZ78JECR']
    #get_mentions(_list)
    # Slack_send_message("U01AZ78JECR", "C02CVHJ297E", "Projects.API.TMSPartnerPortal.Driver", "D:\\", "D:\\", "link", "1373769")
    #print(pathIMG)
