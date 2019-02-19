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
    # for loop here - loop through email_addr list - and make a GET request for each
    # If status is enabled - add to status list - this list will be sent back to the
    # Mediator APP

    mailbox_url = "https://graph.microsoft.com/v1.0/users/" + email_addr + str(
        "/mailboxSettings/automaticRepliesSetting")

    payload = ""
    headers = {
        'Authorization': "Bearer " + str(tkn),
        'cache-control': "no-cache"
    }

    try:
        # response = requests.request("GET", mailbox_url, data=payload, headers=headers)
        response = requests.get(mailbox_url, data=payload, headers=headers)
        resp_json = response.json()
        odata = resp_json['@odata.context']
        int_reply = resp_json['internalReplyMessage']
        ext_reply = resp_json['externalReplyMessage']
        status = resp_json['status']

        # print(odata)
        # print(status)  # will return scheduled or disabled or alwaysEnabled
        # print(int_reply)
        # print(ext_reply)

    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return status
