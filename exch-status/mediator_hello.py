#!/usr/bin/env python3

"""
VMO3 - MEDIATOR HELLO Microservice
Author: Clint Mann

Description:
This is the Mediator Hello API microservice, it will
 + make a REST API call and POST a 'hello' message
 with teh Mediator to synchronize
"""

import requests
import json


def mediator_sync(sync_url, sync_payload):
    print(sync_payload)

    payload = sync_payload

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(sync_url, data=json.dumps(payload),
                             headers=headers)

    print(response.text)
    # data = response.json()
    # print(str(data))
