#!/usr/bin/env python3

"""
VMO3 - Mediator Post
Author: Clint Mann

Description:
This is the Mediator Post function, it will make a REST API call and POST
the automaticRepliesSetting for the user mailbox to the Mediator server.
"""

import requests


def post_mediator(mediator_url, status_payload):
    print('Status payload', status_payload)
    # print(type(status_payload))

    # payload = status_payload

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(mediator_url, json=status_payload,
                             headers=headers)

    # print('Mediator POST', response.text)
    data = response.json()
    # print(response.text)
    print('POST REQUEST - Mediator data to send', status_payload)
    print('POST REQUEST - Mediator response', str(data))




