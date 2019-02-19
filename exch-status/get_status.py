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
from post_api import mediator_post


def usr_status(token, med_url ):


    email_status = {}

    # print(db)
    # print(len(db))
    # using dict.items()
    count = 0
    for key, value in db.items():
        if isinstance(value, list):  # count the num of dict in list 'usrs'
            count += len(value)

    if count > 0:  # there are users in the list
        for key, value in db.items():
            for i in value:  # this will print the email addresses
                email_address = i['email']
                monitor = i['monitor']

                if monitor is True:
                    print(email_address, monitor)
                    # print(monitor)
                    user_status = auto_reply(token, email_address)
                    if user_status != 'disabled':
                        user_status = "True"
                        # print(usr_status)
                        print("User {0} has the following OoO status {1}"
                              .format(email_address, user_status))
                        if email_address in email_status:
                            print('email address in db')
                            if user_status in email_status:
                                print('status is a match')
                            else:
                                email_status['status'] = user_status
                        else:
                            email_status['email'] = email_address
                            email_status['status'] = user_status
                    else:
                        print("User {0} does not have an active Out of Office alert"
                              .format(email_address))

                else:
                    print("This User {0} is not in the monitor state"
                          .format(email_address))
    else:
        print("There are currently no users in database")

    # check db data for email address and if monitor is true -
    # if so add to list to check
    # pass this list to mailbox function this will be variable email_addrs
    # mailboxsettings(token, email_addr_list)

    # POST TO API
    print('email status ', email_status)

    mediator_post(med_url, email_status)




