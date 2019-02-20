#!/usr/bin/env python3

"""
VMO3 - POST API Microservice
Author: Clint Mann

Description:
This is the Post API microservice, it will
 + make a REST API call and POST the automaticRepliesSetting
 for the user mailbox
"""

import requests
import json


def listener_get(listener_url):

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.get(listener_url, headers=headers)
    print('Response', response.text)

    print('GET REQUEST to Listener API', response)
    data = response.json()
    print('GET RESPONSE DATA', str(data))
    return response


def mediator_post(mediator_url, status_payload):
    print('Status payload', status_payload)

    payload = status_payload

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(mediator_url, data=json.dumps(payload),
                             headers=headers)

    # print('Mediator POST', response.text)
    data = response.json()
    print('POST REQUEST - Mediator response', str(data))



