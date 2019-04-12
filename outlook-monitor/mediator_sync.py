#!/usr/bin/env python3

"""
VMO3 - Mediator Sync
Author: Clint Mann

Description:
These functions interact with the Mediator server.

The function - mediator_status - will make a GET request to check if the
Mediator server is operational.

The function - sync_mediator - will make a REST API call and POST a
'hello' message with the Mediator server to synchronize.
"""

import requests
import datetime


def mediator_status(base_url):
    print('Checking MEDIATOR status...')

    resp = requests.get(base_url)
    response = resp.status_code

    return response


def sync_mediator(sync_url):
    print('In Mediator Sync...')
    start = datetime.datetime.now()
    print('START sync', start)

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(sync_url, headers=headers, timeout=35)

    end = datetime.datetime.now()
    print('END sync', end)

    resp = response.json()

    return resp
