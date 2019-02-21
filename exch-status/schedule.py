#!/usr/bin/env python3

"""
VMO3 - Scheduler Microservice
Author: Clint Mann

Description:
This is the scheduler microservice, it will
 + schedule token.py to run in the background inside the application
 + schedule status.py to run in the background inside teh application
"""

import time
import os

from apscheduler.schedulers.background import BackgroundScheduler
from get_token import auth_token
from get_status import usr_status
from mediator_hello import  mediator_sync


tenant = os.environ['TENANT']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
mediator_ip = os.environ['MEDIATOR_IP']
mediator_port = os.environ['MEDIATOR_PORT']
listener_ip = os.environ['LISTENER_IP']
listener_port = os.environ['LISTENER_PORT']

resource = "https://graph.microsoft.com"
grant_type = "client_credentials"

auth_base_url = "https://login.microsoftonline.com/"
oauth_url_v1 = auth_base_url + tenant + str("/oauth2/token")
mailbox_base_url = "https://graph.microsoft.com/v1.0/users/"
mediator_url = "http://" + mediator_ip + ":" + mediator_port + "/api/setstatus"
mediator_sync_url = "http://" + mediator_ip + ":" + mediator_port + "/api/setup"
listener_url = "https://" + listener_ip + "/users"
listener_mon_url = "https://" + listener_ip + "/monitor"

if __name__ == '__main__':

    sync_resp = mediator_sync(mediator_sync_url)
    resp = sync_resp['result']

    if resp == 'True':
        print('Mediator Server sync SUCCESSFUL.')

        scheduler = BackgroundScheduler()

        # Schedule Get Authentication Token - expires every 3600 seconds
        scheduler.add_job(auth_token, 'interval', seconds=3500,
                          args=[client_id, client_secret, resource,
                                grant_type, oauth_url_v1])
        tkn = auth_token(client_id, client_secret, resource,
                         grant_type, oauth_url_v1)

        # Schedule User Status Check
        scheduler.add_job(usr_status, 'interval', seconds=5,
                          args=[tkn, mediator_url, listener_url, listener_mon_url])
        usr_status(tkn, mediator_url, listener_url, listener_mon_url)

        # Start Scheduler
        scheduler.start()

        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
    else:
        print('Was unable to sync with Mediator Server')