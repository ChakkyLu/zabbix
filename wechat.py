#!/usr/bin/env python3
 #-*- coding: utf-8 -*-
 #date: 2018-04-20
 #comment: zabbix接入微信报警脚本

import requests
import sys
import os
import json
import logging

#logging.basicConfig(level = logging.DEBUG, format = '%(asctime)s, %(filename)s, %(levelname)s, %(message)s',datefmt = '%a, %d %b %Y %H:%M:%S',filename = os.path.join('/home/ec2-user/zabbix','weixin.log'),filemode = 'a')
appsecret = 'TaSWQvWpazt5auRuU6LMRyEb5WwjiWWX44o_rALG8nM'
agentid = 1000103
token_url='https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + appsecret
req = requests.get(token_url)
accesstoken = req.json()['access_token']

# send message
send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + accesstoken
user = sys.argv[1]
subject = sys.argv[2]
message = sys.argv[3]

params = {
    'tosuer' : user,
    'msgtype': "text",
    'agentid': agentid,
    'text': {
        'content': message
    },
    'safe': 0
}
req = requests.post(send_url, data=json.dumps(params))
logging.info('send to:' + user + ';;subject:' + subject + ';;message:' + message)
