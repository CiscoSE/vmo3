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


def auto_reply(tkn, email_addr):

    mailbox_url = "https://graph.microsoft.com/v1.0/users/" + email_addr + str(
        "/mailboxSettings/automaticRepliesSetting")

    payload = ""
    headers = {
        'Authorization': "Bearer " + str(tkn),
        'cache-control': "no-cache"
    }

    try:
        response = requests.get(mailbox_url, data=payload, headers=headers)
        resp_json = response.json()
        # odata = resp_json['@odata.context']
        # int_msg = resp_json['internalReplyMessage']
        ext_msg = resp_json['externalReplyMessage']
        status = resp_json['status']

    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return status, ext_msg
