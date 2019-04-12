#!/usr/bin/env python3

"""
Exchange Monitor - Main
Author: Clint Mann

Description: A Flask application that will create a RESTFul API
service that listens for an HTTP POST from a Mediator server.

The Mediator server determines which Azure Active Directory users will
have their Out of Office status monitored.

This application will parse the POST request from the external Mediator
server for a user email address and a monitor status. Users with at
monitor status of TRUE will be checked against Active Directory.
If the user exists in Active Directory, their email Automatic Replies,
or Out of Office status will be checked. If the Out of Office status changes
a POST will be made to the Mediator application, which will trigger the users
Alternative greeting, or voicemail, to be enabled in Cisco Unity.

"""

import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify
from datetime import datetime
from get_token import auth_token
from check_MSgraph import check_activedir_users, check_auto_reply
from mediator_sync import mediator_status, sync_mediator
from mediator_post import post_mediator

tenant = os.environ['TENANT']
client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
mediator_ip = os.environ['MEDIATOR_IP']
mediator_port = os.environ['MEDIATOR_PORT']

resource = "https://graph.microsoft.com"
grant_type = "client_credentials"

auth_base_url = "https://login.microsoftonline.com/"
oauth_url_v1 = auth_base_url + tenant + str("/oauth2/token")
graph_users_url = "https://graph.microsoft.com/v1.0/users/"
mediator_base_url = "http://" + mediator_ip + ":" + mediator_port
mediator_url = "http://" + mediator_ip + ":" + mediator_port + "/api/setstatus"
mediator_sync_url = "http://" + mediator_ip + ":" + mediator_port + \
                    "/api/setup"

app = Flask(__name__)
VMOusers = []
post_status = "False"


@app.before_first_request
def sync_schedule():
    global token

    # check MEDIATOR status
    resp = mediator_status(mediator_base_url)
    print(resp)

    if resp == 200:  # mediator server is active

        msg = 'Mediator Server REACHABLE.'
        print(msg)

        #  --- SCHEDULER ----
        scheduler = BackgroundScheduler(daemon=True)

        # schedule authentication token refresh - expires every 3600 seconds
        scheduler.add_job(auth_token, 'interval', seconds=3500,
                          args=[client_id, client_secret, resource, grant_type,
                                oauth_url_v1])

        token = auth_token(client_id, client_secret, resource, grant_type,
                           oauth_url_v1)

        # schedule user status check
        scheduler.add_job(process_users, 'interval', seconds=2)
        process_users()

        # start scheduler
        scheduler.start()

    else:  # mediator server is not active
        msg = 'Mediator Server UNREACHABLE.'
        print(msg)


@app.route("/")
def main():
    print(str(datetime.now())+": Processing /main functionality")

    #  sync with MEDIATOR
    sync_resp = sync_mediator(mediator_sync_url)
    response = sync_resp['result']
    print("response", response)

    if response == 'True':
        result = 'Mediator Server sync SUCCESSFUL.'
    else:
        result = 'Unable to sync with Mediator Server.'

    message = "EXCHANGE OOO MAIN PAGE : {}".format(result)
    print(message)

    return message


@app.route("/monitor", methods=['POST'])
def monitor_users():
    print(str(datetime.now())+": Processing /monitor functionality")

    if not request.is_json:
        return jsonify({"result": "Not JSON"}), 400

    else:
        # 1 - check API for POST from MEDIATOR
        req_data = request.get_json(force=True, silent=True)
        data = int(len(req_data))

        try:
            # 2 - check if there was anything POSTED from MEDIATOR
            if data > 0:  # MEDIATOR posted users to be monitored
                email_address = req_data['email']
                monitor_status = req_data['status']
                print('Monitor status', monitor_status)
                print('VMOusers - start', VMOusers)
                # 3 - there is a user - query MS Active Directory
                print('CHECK ACTIVE DIRECTORY FOR EMAIL: ', email_address)
                activedir_check = check_activedir_users(token, graph_users_url)
                print("activedir check", activedir_check)
                all_users = activedir_check['value']

                # 4 - check MS Graph response - does the user exist
                all_users_str = str(all_users)
                if email_address in all_users_str:  # user has email account
                    print("USER {0} FOUND in MS AD".format(email_address))

                    # 5 - should this user be monitored
                    if monitor_status == "True":  # user to be monitored
                        print(email_address, monitor_status)

                        # 6 - Query MS GRAPH for user OoO status
                        ooo_status, message = check_auto_reply(
                            token, email_address, graph_users_url)

                        # 7 - check OoO status - normalize
                        if ooo_status != "disabled":  # autoReply (OoO) enabled
                            ooo_status = "True"  # normalize status
                        else:  # OoO autoReply is disabled
                            ooo_status = "False"
                            print("User {0} : does not have active Out of "
                                  "Office alert".format(email_address))

                        profile = {
                            "email": email_address,
                            "ooo": ooo_status,
                            "message": message
                        }

                        # 8 - add user to local storage
                        if not VMOusers:  # list empty - add user
                            VMOusers.append(profile)
                        else:  # user not already in list of dictionaries
                            if not any(u.get('email', None) == email_address
                                       for u in VMOusers):
                                VMOusers.append(profile)  # add user
                            # will POST in process_user function
                    else:
                        # monitor is FALSE delete user from VMOusers
                        print("This User {0} is not in the monitor state"
                              .format(email_address))
                        print('VMOusers', VMOusers)

                        for u in range(len(VMOusers)):
                            if VMOusers[u]['email'] == email_address:
                                del VMOusers[u]
                                print('Deleted user...')
                                break
                    return '''<h1>You would like to monitor user {} {}</h1>'''\
                        .format(email_address, monitor_status)

                else:  # no users from MEDIATOR GET REQUEST - check local list
                    print('NO users to monitor from MEDIATOR')
                    return '''<h1>User {} not in Active Directory</h1>'''\
                        .format(email_address)

        except(KeyError, TypeError, ValueError):
            return jsonify({"result": "Invalid JSON"}), 400


def process_users():
    # 1 - check if there are users in vmo_enabled_users list
            if len(VMOusers) > 0:  # there are users in list
                print('length vmo users', len(VMOusers))
                print('USER FOUND IN VMO USERS')

                # 2 - parse through list checking ooo status
                for u in VMOusers:
                    print('user - for', u)
                    last_ooo_status = u['ooo']
                    email_address = u['email']
                    # monitor_status = u['monitor']

                    # 3 - user in list - check OoO status
                    ooo_status, message = check_auto_reply(
                        token, email_address, graph_users_url)
                    print('ooo status', ooo_status)

                    # 4 - compare last ooo status to current ooo status
                    if last_ooo_status == ooo_status:
                        print('user', u)
                        print('last ooo', last_ooo_status)
                        print('ooo status', ooo_status)
                        print('no change in OOO status')

                    else:
                        # 5 - change detected generate payload for MEDIATOR
                        print('user', u)
                        print('last ooo', last_ooo_status)
                        print('ooo status', ooo_status)
                        print('OOO status has changed...')

                        # update email_address in vmousers with new ooo
                        u['ooo'] = ooo_status
                        u['message'] = ""

                        if ooo_status != "disabled":  # autoReply (OoO) enabled
                            ooo_profile_status = "True"  # normalize status
                        else:  # normalize OoO status for MEDIATOR
                            ooo_profile_status = "False"

                        profile_payload = {
                            "email": email_address,
                            "status": ooo_profile_status,
                            "message": message
                        }

                        # 6 - POST ooo status change to MEDIATOR
                        print('POST OoO Status to Mediator '
                              'Server...(process_users)')
                        post_mediator(mediator_url, profile_payload)
                        print('POST complete from vmo enabled '
                              'list...(process_users)')
                        print('VMO USERS', VMOusers)
            else:  # there are no users in list
                print('NO USER FOUND IN VMO USERS', len(VMOusers))


if __name__ == '__main__':

    # Start Flask
    app.run(debug=True, host='0.0.0.0')

