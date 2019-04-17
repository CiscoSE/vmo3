#!/usr/bin/env python3


"""
Demonstrates how to use the background scheduler to schedule a job that executes on 3 second
intervals.
"""

import requests
import sys
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler


base_url = "https://api.ciscospark.com"
wxt_token = 'NTczYzc0MjctZTUwNi00ODljLTg3YTMtMjY1NzIyZjFlZmNjYjRjNWYwMjgtZDQx_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f'
usr_email = 'climann2@cisco.com'


def usrinfo(b_url, token, email):

    querystring = "/v1/people?email=" + str(email)
    url = b_url + querystring
    headers = {
        'Content-Type': "application/json",
        'Authorization': "Bearer " + token,
        'cache-control': "no-cache",
    }

    try:
        r = requests.get(url, headers=headers)
        output = r.json()
        print(output)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':

    scheduler = BackgroundScheduler()
    # Schedule Get Authentication Token - expires every 3600 seconds
    scheduler.add_job(getauthtoken, 'interval', seconds=20,
                      args=[client_id, client_secret, resource, grant_type, oauth_url_v1])
    token = getauthtoken(client_id, client_secret, resource, grant_type, oauth_url_v1)
    #scheduler.start()

    # Schedule Get Mailbox Settings
    scheduler.add_job(userinfo, 'interval', seconds=5,
                      args=[token, email_address])
    usr_status = mailboxsettings(token, email_address)

    scheduler.start()

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            # scheduler.add_job(mailboxsettings, 'interval', seconds=5,
            #                  args=[access_token, email_address])
            #usr_status = mailboxsettings(access_token, email_address)
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()