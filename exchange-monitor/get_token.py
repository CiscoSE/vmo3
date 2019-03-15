#!/usr/bin/env python3

"""
VMO3 - Get Token
Author: Clint Mann

Description:
Get a token from Microsoft Graph API using Client Credentials
"""

import requests


def auth_token(c_id, c_secret, r_url, g_type, auth_url):

    payload = 'client_id={0}&client_secret={1}&resource={2}&grant_type={3}'\
        .format(c_id, c_secret, r_url, g_type)

    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
    }

    response = requests.post(auth_url, data=payload, headers=headers)
    resp_json = response.json()
    access_token = resp_json['access_token']
    print('Retrieved MS Graph Access Token - SUCCESSFUL')

    return access_token
