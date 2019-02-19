# -*- coding: utf-8 -*-

'''
Work in progress....
'''

from flask import Flask, request
from flask_restplus import Api, Resource
import jsonify

app = Flask(__name__)
#api = Api(app) # version='1.0',title='VMO3 REGISTER USE API', default='VMO3',default_label='VMO3 namespace', description='VMO3 API to register users')


USER = {}


@app.route('/', methods=['GET'])
def home():
    return ('<h1>VMO3 API to monitor Exchange Out of Office status</h1> \n'
            '<p>This API is used to register a user to be monitored by VMO3.</p> \n')


@app.route('/users', methods=['GET'])
def getusers():
    req_data = request.get_json(force=True, silent=True)
    # email = request.args.get('email')
    email = req_data['email']
    print(email)
    status = req_data['status']
    # status = request.args.get('status')
    print(status)
    USER['email'] = email
    USER['status'] = status
    print('users', USER)
    return '''<h1>You would like to monitor user {} {}</h1>'''.format(email, status)


@app.route('/monitor', methods=['POST'])
def monitorusers():
    req_data = request.get_json(force=True, silent=True)
    # email = request.args.get('email')
    email = req_data['email']
    print(email)
    status = req_data['status']
    # status = request.args.get('status')
    print(status)
    USER['email'] = email
    USER['status'] = status
    print('users', USER)
    return '''<h1>You would like to monitor user {} {}</h1>'''.format(email, status)


if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)

