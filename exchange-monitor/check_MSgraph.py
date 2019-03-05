#!/usr/bin/env python3

"""
VMO3 - AutoReply Microservice
Author: Clint Mann

Description:
This is the token microservice, it will
 + check the automaticRepliesSetting for the user mailbox
"""

import sys
import requests
import re


def check_activedir_user(tkn, graph_base_url):

    headers = {
        'Authorization': "Bearer " + str(tkn),
        'cache-control': "no-cache"
    }
    try:
        response = requests.get(graph_base_url, headers=headers)
        # print('Response', response.text)
        resp_json = response.json()
        # print('L - GET REQUEST to Graph check user', response)
        data = response.json()
        # print('L - GET RESPONSE GRAPH CHECK DATA', str(data))

    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return resp_json


def check_auto_reply(tkn, email_addr, graph_base_url):

    mailbox_url = graph_base_url + email_addr + str(
        "/mailboxSettings/automaticRepliesSetting")

    payload = ""
    headers = {
        'Authorization': "Bearer " + str(tkn),
        'cache-control': "no-cache"
    }

    try:
        # check if resource - the email address exists - if so continue - else error message
        response = requests.get(mailbox_url, data=payload, headers=headers)
        resp_json = response.json()
        print(response.text)
        # print(resp_json)
        status = resp_json['status']
        # odata = resp_json['@odata.context']
        # int_msg = resp_json['internalReplyMessage']
        e_msg = resp_json['externalReplyMessage']
        ext_rmsg = re.sub("\n", "", e_msg)  # remove carriage returns
        ext_msg = re.sub("<.*?>", "", ext_rmsg)  # remove html tags

    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return status, ext_msg
