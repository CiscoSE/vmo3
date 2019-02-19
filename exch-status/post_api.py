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


def mediator_post(mediator_url, status_payload):
    print(status_payload)

    payload = status_payload

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(mediator_url, data=json.dumps(payload),
                             headers=headers)

    print(response.text)
    # data = response.json()
    # print(str(data))


def listener_get(listener_url):

    headers = {
        'Content-Type': 'application/json'
    }

    # req_data = request.get_json(force=True, silent=True)
    response = requests.get(listener_url, headers=headers)
    print(response.text)

    print('DATA', response)

    return response
