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

from mail_setting import auto_reply
from post_api import mediator_post , listener_get


def usr_status(token, med_url, listen_api_url):

    mon_user = listener_get(listen_api_url)

    monitor_user = mon_user.json()

    count = int(len(monitor_user))

    if count > 0:  # there are users in the list
        email_address = monitor_user['email']
        monitor = monitor_user['status']
        if monitor == 'True':
            print(email_address, monitor)
            # print(monitor)
            user_status, message = auto_reply(token, email_address)
            if user_status != 'disabled':
                user_status = "True"
                # print(usr_status)
                print("User {0} has the following OoO status {1} {2}"
                        .format(email_address, user_status, message))
                if email_address in monitor_user:
                    print('email address in db')
                    if user_status in monitor_user:
                        print('status is a match')
                    else:
                        monitor_user['status'] = user_status
                else:
                    monitor_user['email'] = email_address
                    monitor_user['status'] = user_status
                    monitor_user['message'] = message

                    print('email status ', monitor_user)
                    print('message', message)
                    mediator_post(med_url, monitor_user)
            else:
                print("User {0} does not have an active Out of Office alert"
                        .format(email_address))

        else:
            print("This User {0} is not in the monitor state"
                    .format(email_address))

    else:
        print("There are currently no users in database")






