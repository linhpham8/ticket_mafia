import os
from typing import List, Pattern
import glob
import time
import json
import re
import json

import requests
from typing import List, Pattern

# class read_google_space():
#     def get_data_json(self, google_space):
#         with open('Libs\\google_space.json', 'r') as file :
#             data = json.load(file)
#             GOOGLE_CHAT_SPACE = data[google_space]

#             #     file = open(filename, encoding="utf8")
#             #  data = json.load(file)
        
#         print(GOOGLE_CHAT_SPACE['key'])
            
class extend_google_chat():

    def __init__(self, google_space):
        with open('{0}google_space.json'.format(os.environ.get("GOOGLESPACE")), 'r') as file :
            data = json.load(file)
            self.GOOGLE_CHAT_API = "https://chat.googleapis.com/v1/spaces"
            self.GOOGLE_CHAT_SPACE = google_space
            self.GOOGLE_CHAT_KEY = data[google_space]['key']
            self.GOOGLE_CHAT_TOKEN = data[google_space]['token']

    def get_mentions(self, mentions): 
        '''
        Laays
        '''

        # list_mentions = ''
        # item = mentions.split(';')
        # mention_length = len(item)


        # for i in range(mention_length):

        #     list_mentions += ' <users/{0}> '.format(item[i])      
        # return list_mentions
    
        return ' '.join(['<users/{0}>'.format(item) for item in mentions.split(';')])
    
    def get_pipeline(self, url_pipeline):

        pipeline_code = url_pipeline.rsplit('/', 1)[-1]
        return "<"+ url_pipeline +"|#"+ pipeline_code +">"
    
    def set_color_info(self, messages):

        if re.findall("\s0 failed", messages):
            color_info = {"msg" : "<font color=\"#1BE942\">{0}</font>".format(messages), "image":"https://i.imgur.com/eXS34BE.png"}
        else:
            color_info = {"msg" : "<font color=\"#FF0042\">{0}</font>".format(messages), "image":"https://i.imgur.com/EM0CFoZ.png"}
        return color_info

    def google_send_text(self, list_mention, link_jenkins):
        """Google Chat incoming webhook quickstart."""

        mention = self.get_mentions(list_mention)

        url = "{0}/{1}/messages?key={2}&token={3}".format(self.GOOGLE_CHAT_API, self.GOOGLE_CHAT_SPACE, self.GOOGLE_CHAT_KEY, self.GOOGLE_CHAT_TOKEN)
        payload = {"text": "Xin mời {0} kiểm tra kết quả\nLink report : <{1}robot/report/report.html#totals|{1}robot/report/report.html#totals>".format(mention, link_jenkins)}
        
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
  

    def google_send_card(self, suitename, messages, env, url_pipeline="1234"):
     
        if url_pipeline == "1234":
            pipeCode = "\n"
        elif "http" in url_pipeline:
            pipeCode = self.get_pipeline(url_pipeline)
        else:
            pipeCode = url_pipeline
        color_info = self.set_color_info(messages)

        payload = {"cardsV2":[{"cardId":"unique-card-id",
                               "card":{"sections":[{"header":" ","collapsible":False,"uncollapsibleWidgetsCount":1,
                                                    "widgets":[{"columns":{"columnItems":[{"horizontalSizeStyle":"FILL_MINIMUM_SPACE",
                                                                                           "horizontalAlignment":"START","verticalAlignment":"TOP",
                                                                                           "widgets":[{"textParagraph":{"text":"<B>TEST SUITE</B><br> {0}".format(suitename)}},
                                                                                                      {"textParagraph":{"text":"<B>ENVIRONMENT</B> <br> {0}".format(env).upper()}}]},
                                                                                                      {"widgets":[{"textParagraph":{"text":"<B>PIPELINE</B> <br> {0}".format(pipeCode)}},
                                                                                                                  {"textParagraph":{"text":"<B>TEST RESULT</B> <br> {0}".format(color_info['msg'])}}]}]}},
                                                                                                                  {"image":{"imageUrl":"{0}".format(color_info['image'])}}]}]}}]}

        headers = {"Content-Type": "application/json; charset=UTF-8"}
        url = "{0}/{1}/messages?key={2}&token={3}".format(self.GOOGLE_CHAT_API, self.GOOGLE_CHAT_SPACE, self.GOOGLE_CHAT_KEY, self.GOOGLE_CHAT_TOKEN)

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))


    def google_send_messages(self, list_mention, link_jenkins, suitename, messages, env, url_pipeline):
        self.google_send_text(list_mention, link_jenkins)
        self.google_send_card(suitename, messages, env, url_pipeline)
        print("Send report to google chat")

# run = google_chat().google_send_text("105505664806900222583;105505664806900222583","http://10.124.60.233:8080/job/MERCHANDISE/job/MERCHANDISE-VINSHOP-PLP/1682/")
# run1 = google_chat().google_send_card(suitename="PLP Vinshop", messages="23 tests, 1 passed, 0 failed", env="qc", url_pipeline="1234")
# [END hangouts_python_webhook]
# https://chat.google.com/room/AAAAYE-xHqo?cls=1
# run = read_google_space().get_data_json('AAAAvHU-7i0')