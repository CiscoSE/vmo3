#!/usr/bin/env python3

"""
VMO3 - MEDIATOR LISTEN Microservice
Author: Clint Mann

Description:
This is the MEDIATOR LISTEN API microservice, it will
 + wait for a REST API POST that contains user email address
 and monitor status. It will then pass that information to
 get_status.py to check the automaticRepliesSetting
 for the user mailbox
"""

from flask import Flask, request
from flask_restplus import Api, Resource
import jsonify
import json


app = Flask(__name__)
#api = Api(app) # version='1.0',title='VMO3 REGISTER USE API', default='VMO3',default_label='VMO3 namespace', description='VMO3 API to register users')


USER = {}

print('mediator listen - started')


@app.route('/', methods=['GET'])
def home():
    return ('<h1>VMO3 API to monitor Exchange Out of Office status</h1> \n'
            '<p>This API is used to register a user to be monitored by VMO3.</p> \n')


@app.route('/users', methods=['GET'])
def getusers():
    global USER
    data = json.dumps(USER)
    return data


@app.route('/monitor', methods=['POST'])
def monitorusers():
    global USER
    if not request.is_json:
        return jsonify({"result": "Not JSON"}), 400

    req_data = request.get_json(force=True, silent=True)

    try:
        email = req_data['email']
        # print(email)
        status = req_data['status']
        # status = request.args.get('status')
        # print(status)
        USER['email'] = email
        USER['status'] = status
        print('users', USER)
        data = json.dumps(USER)

        return '''<h1>You would like to monitor user {} {}</h1>'''.format(email, status)

    except(KeyError, TypeError, ValueError):
        return jsonify({"result":"Invalid JSON"}), 400


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
