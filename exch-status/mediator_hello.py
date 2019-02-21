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


def mediator_sync(sync_url):
    print('In Mediator Sync...')
    #print(sync_payload)

    #payload = sync_payload

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(sync_url, headers=headers)


    #print(response.text)
    resp = response.json()
    #print(str(resp))

    return resp
