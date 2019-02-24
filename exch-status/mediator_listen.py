#!/usr/bin/env python3

"""
VMO3 - MEDIATOR LISTEN Microservice
Author: Clint Mann

Description:
This is the MEDIATOR LISTEN API microservice, it will
 + wait for a REST API POST that contains user email address
 and monitor status. It will then be queried by get_status.py
  to check the automaticRepliesSetting
 for the user mailbox
"""

from flask import Flask, request
# from flask_restplus import Api, Resource
import jsonify
import json


app = Flask(__name__)


USER = {}


@app.route('/', methods=['GET'])
def home():
    return ('<h1>VMO3 API to monitor Exchange Out of Office status</h1> \n'
            '<p>This API is used to register a user to be monitored by VMO3.</p> \n')


@app.route('/users', methods=['GET'])
def getusers():
    print('get user', USER)
    data = json.dumps(USER)
    USER.clear()
    return data


@app.route('/monitor', methods=['POST'])
def monitorusers():

    if not request.is_json:
        return jsonify({"result": "Not JSON"}), 400

    req_data = request.get_json(force=True, silent=True)

    try:
        email = req_data['email']
        # print(email)
        status = req_data['status']
        # print(status)
        USER['email'] = email
        USER['status'] = status
        data = json.dumps(USER)

        return '''<h1>You would like to monitor user {} {}</h1>'''.format(email, status)

    except(KeyError, TypeError, ValueError):
        return jsonify({"result":"Invalid JSON"}), 400


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
