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

def connect():
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    return client

# US1T56XV3
# bot-auto-reports

def get_path_image(path):
    time.sleep(3)
    listFile = glob.glob(path + '/*.png')
    latestFile = max(listFile, key=os.path.getmtime)
    if latestFile is None:
        print("Cannot get the latest screenshot in this directory : " + path)
    else:
        return latestFile

def get_mentions(mentions: list): 

    list_mentions = ''
    for mention in mentions:
        list_mentions += '<@' + mention + '>' + ' '
    
    return list_mentions

def get_pipeline(url_pipeline):

    pipeline_code = url_pipeline.rsplit('/', 1)[-1]
    return "<"+ url_pipeline +"|#"+ pipeline_code +">"

def Slack_send_message(mention, channel, suitename, messages, link, env, url_pipeline="123"):
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

    if "." in suitename:
        # suitename = suitename.rsplit(".", 2)[1]
        # suitename = suitename[9:]
        suitename = suitename.replace('B2B-Autotest.','').replace('Projects.','')
        # suitename = suitename[suitename.index(".") + 1:]
    if url_pipeline == "123":
        pipeCode = ""
    elif "http" in url_pipeline:
        pipeCode = get_pipeline(url_pipeline)
    else:
        pipeCode = url_pipeline

    client = connect()
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
                    {"title": "TEST DETAIL", "value": "" + link + "", "short": False}
                ],
            "footer": "Automation Team",
            "footer_icon": "https://i.imgur.com/UBzfS6M.png",    
            }           

        ]
    )

    return response
    # print(str(response))

def Slack_send_file(channel, path):
    """Send report to slack

	Arguments:
	- ``channel``: US1T56XV3 or #bot-auto-reports 
	- ``path``: Path file
		"""
    pathIMG = get_path_image(path)
    client = connect()

    responseFile = client.files_upload(
        channels=channel,
        file=pathIMG)

    return responseFile

def Slack_File_and_Message(channel, testName, message, path, link):
    """Slack_File_and_Message
	Arguments:
	- ``channel``: US1T56XV3 or #bot-auto-reports
    - ``testName``: Testcase Name
	- ``message``: Pass Fail In robotframework 
	- ``msg``: message which we want to put in group chat
	- ``link``: link to log file
		"""
    
    #time.sleep(3)
    client = connect()

    pathIMG = get_path_image(path)
    print(pathIMG)
    responseFile = client.files_upload(
        channels=channel,
        initial_comment=testName,
        file=pathIMG
    )

    sendMesage = client.chat_postMessage(
        channel=channel,
        text=message)

    return responseFile

def Slack_File_Message_and_Mention(channel: str, testName: str, message: str, path: str, link: str, mentions: list):

    """Slack_File_and_Message
	Arguments:
	- ``channel``: US1T56XV3 or #bot-auto-reports
    - ``testName``: Testcase Name
	- ``message``: Pass Fail In robotframework 
	- ``msg``: message which we want to put in group chat
	- ``link``: link to log file
    - ``mentions : List mentions
		"""

    list_mention = get_mentions(mentions)
    pathIMG = get_path_image(path)

    client = connect()

    responseFile = client.files_upload(
        channels=channel,
        initial_comment='Xin mời các sếp ' + list_mention + ' kiểm tra kết quả ',
        file=pathIMG
    )

    return pathIMG

def Slack_result(msg, path):
    sendMesage = Slack_send_message(msg)
    sendFile = Slack_send_file(path)
    assert sendMesage["ok"]
    assert sendFile["ok"]

# def get_code_pipeline():

#     s1 = 'https://gitlab.id.vin/tms/tier1/tier1-bff-partner/-/pipelines/1373769'


#     st1 = s[s.index(".") - 1::]

#     index = s.rfind('/')
#     st2 = s[index+1:]
#     s = s.rsplit('/', 1)[-1]
#     print(st1)
#     print(st2)
#     print(s)

if __name__ == "__main__":

    # a = get_pipeline_code('https://gitlab.id.vin/tms/tier1/tier1-bff-partner/-/pipelines/1373769')
    # print(a[0])
    # pathIMG = Slack_File_and_Message("U01AZ78JECR", "TM1D-01 Smoke API Flow", "D:\\", "D:\\", "link")
    
    # _list = ['U01AZ78JECR']
    #get_mentions(_list)
    Slack_send_message("U01AZ78JECR", "C02CVHJ297E", "Projects.API.TMSPartnerPortal.Driver", "D:\\", "D:\\", "link", "1373769")
    #print(pathIMG)
