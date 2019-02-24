
#!/usr/bin/env python3

"""
VMO3 - User Status Microservice
Author: Clint Mann

Description:
This is the user status microservice, it will
 + reach out out to mailsetting.py to check the
 automaticRepliesSetting for the user mailbox
 + it will then send the results to VMO3 Hub microservice
"""

from mail_setting import auto_reply, graph_check_user
from api import mediator_post, listener_get
import json

vmo_enabled_usrs = []


def usr_status(token, med_url, listen_api_url, mailbox_base_url):

    # 1 - Check API for POST from MEDIATOR
    mon_user_resp = listener_get(listen_api_url)  # GET user to monitor
    print('GS - GET RESPONSE from Listener', mon_user_resp)  # should be
    # <Response [200]>

    monitor_user = mon_user_resp.json()
    print('GS - GET RESPONSE JSON', monitor_user)

    count = int(len(monitor_user))
    print(count)

    # 2 - check if there was anything POSTED from MEDIATOR
    if count > 0:  # MEDIATOR posted users to be monitored
        email_address = monitor_user['email']
        monitor_status = monitor_user['status']

        # 3 - there is a user - query MS Graph
        print('CHECK GRAPH FOR EMAIL: ', email_address)
        graph_check = graph_check_user(token, mailbox_base_url)
        all_users = graph_check['value']
        # print('value type', type(value))
        print('value', all_users)

        # 4 - check MS Graph response - does the user exist
        all_users_str = str(all_users)
        if email_address in all_users_str:  # user has email account
            print("USER {0} FOUND in MS AD".format(email_address))

            # 5 - should this user be monitored
            if monitor_status == "True":  # user supposed to be monitored
                print(email_address, monitor_status)

                # 6 - Query MS GRAPH for user OoO status
                ooo_status, message = auto_reply(
                    token, email_address, mailbox_base_url)

                # 7 - if OoO is enabled - POST to MEDIATOR
                if ooo_status != "disabled":  # autoReply (OoO) is enabled
                    ooo_status = "True"  # normalize status

                    # 8 - add this user to local storage
                    # add ooo_status to vmo_enabled_usrs

                    profile = {
                        "email": email_address,
                        "monitor": monitor_status,
                        "ooo": ooo_status,
                        "message": message
                    }

                    profile_payload = {
                        "email": email_address,
                        "status": ooo_status,
                        "message": message
                    }

                    profile_json = json.dumps(profile_payload)  # make JSON

                    print('POST OoO Status to Mediator Server...')
                    mediator_post(med_url, profile_json)
                    print('POST complete...')

                    if monitor_user not in vmo_enabled_usrs:  # usr not in list
                        vmo_enabled_usrs.append(profile)  # add user

                    else:
                        print('user in vmo_enabled_user')

                else:  # OoO autoReply is disabled

                    print("User {0} : does not have active Out of Office "
                          "alert".format(email_address))

                    # profile = dict()

                    # profile["email"] = email_address
                    # profile["monitor"] = monitor_status
                    # profile["ooo"] = ooo_status
                    # profile["message"] = message

                    profile = {
                        "email": email_address,
                        "monitor": monitor_status,
                        "ooo": ooo_status,
                        "message": message
                    }

                    json.dumps(profile)

                    if monitor_user not in vmo_enabled_usrs:  # usr not in list
                        vmo_enabled_usrs.append(profile)  # add user
                    else:
                        print('user in vmo_enabled_user')
            else:
                # check list if user in it remove them since mon is now false
                print("This User {0} is not in the monitor state"
                      .format(email_address))
        else:
            print("USER {0} NOT FOUND in MS GRAPH".format(email_address))

    else:  # NO USERS from MEDIATOR GET REQUEST - CHECK local list

        # 1 - check if there are users in vmo_enabled_users list
        if len(vmo_enabled_usrs) != 0:  # there are users in list
            print('USER FOUND IN local list')

            # 2 - parse through list checking ooo status
            for u in vmo_enabled_usrs:
                # print(u)
                last_ooo_status = u['ooo']
                email_address = u['email']
                monitor_status = u['monitor']

                # 3 - if monitor in list is true check OoO status
                if u['monitor'] == 'True':
                    print('check MS Graph for OOO status')
                    ooo_status, message = auto_reply(
                            token, email_address, mailbox_base_url)
                    print('ooo status', ooo_status)

                    # 4 - compare last ooo status to current ooo status
                    if last_ooo_status == ooo_status:
                        print('last ooo', last_ooo_status)
                        print('ooo status', ooo_status)
                        print('no change in OOO status')
                    else:
                        print('last ooo', last_ooo_status)
                        print('ooo status', ooo_status)
                        print('OOO status has changed...')

                        u['ooo'] = ooo_status
                        u['message'] = ""

                        profile = {
                            "email" : email_address,
                            "monitor" : monitor_status,
                            "ooo" : ooo_status,
                            "message" : message
                        }

                        profile_payload = {
                            "email": email_address,
                            "status": ooo_status,
                            "message": message
                        }
                        profile_json = json.dumps(profile_payload)

                        print('profile json', profile_json)
                        # 4 - if ooo status changed POST to MEDIATOR
                        print('POST OoO Status to Mediator Server...')
                        mediator_post(med_url, profile_json)
                        print('POST complete from vmo enabled list...')
                        # update vmo uses with new ooo
                        print('VMO USERS', vmo_enabled_usrs)

        else:  # there are no users in the list
            print("NO USERS FOUND in local user list")

