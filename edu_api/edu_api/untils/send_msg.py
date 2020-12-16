import random

import requests

from edu_api.settings import constants


class Message(object):
    def __init__(self,api_key):
        self.api_key = api_key
        self.single_send_url = constants.SINGLE_SEND_URL

    def send_message(self,phone,code):
        params = {
            "apikey":self.api_key,
            "mobile":phone,
            "text":f"【毛信宇test】您的验证码是{code}。如非本人操作，请忽略本短信"
        }
        req = requests.post(self.single_send_url,params)
        print(req)


if __name__ == '__main__':
    message = Message(constants.API_KEY)
    message.send_message('17698891321',random.randint(100000,999999))