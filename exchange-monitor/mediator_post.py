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


def post_mediator(mediator_url, status_payload):
    print('Status payload', status_payload)

    payload = status_payload

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(mediator_url, data=payload,
                             headers=headers)

    # print('Mediator POST', response.text)
    data = response.json()
    print(response.text)
    print('POST REQUEST - Mediator data to send', payload)
    print('POST REQUEST - Mediator response', str(data))



