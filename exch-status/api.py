
from flask import Flask, request
from flask_restplus import Api, Resource

# db_connect = create_engine('sqlite:///chris.db')
app = Flask(__name__)
api = Api(app, version='1.0', title='VMO3 REGISTER USE API', default='VMO3', default_label='VMO3 namespace', description='VMO3 API to register users')

USERS = {}


class Employees(Resource):
    def get(self):
        conn = db_connect.connect()  # connect to database
        query = conn.execute("select * from employees")  # This line performs query and returns json result
        return {'employees': [i[0] for i in query.cursor.fetchall()]}  # Fetches first column that is Employee ID


api.add_resource(Employees, 'api/employees')  # Route_1

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
