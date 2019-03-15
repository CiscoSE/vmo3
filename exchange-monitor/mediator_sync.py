#!/usr/bin/env python3

"""
VMO3 - MEDIATOR SYNC
Author: Clint Mann

Description:
This is the Mediator Sync, it will
 make a REST API call and POST a 'hello' message
 with the Mediator to synchronize
"""

import requests


def sync_mediator(sync_url):
    print('In Mediator Sync...')

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(sync_url, headers=headers)

    resp = response.json()

    return resp
