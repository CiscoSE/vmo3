import configparser
import requests
import datetime
from utilities import print_details
from flask import Flask,jsonify,request,render_template,redirect,flash
import json
import db

print("VMO3 Mediator Starting...\n")

print("Configuration Options:")

app = Flask(__name__,static_url_path='/static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Open up the configuration file and get all application defaults

config = configparser.ConfigParser()

try:
    config.read('package_config.ini')
except configparser.Error:
    print("Error: Unable to open package_config.ini")
    exit(-1)


# This flag turns on debugging of the web messages hitting the flask server
try:
    debugmode = config.get("vmo-mediator","webdebug")
    if debugmode == 'True':
        WEBDEBUG = True
    else:
        WEBDEBUG = False
except configparser.NoOptionError:
    WEBDEBUG=False


try:
    vmip = config.get("vmo-mediator","vm-interface")
    mailip = config.get("vmo-mediator","mail-interface")
    listenip = config.get("vmo-mediator","listen-ip")
    listenport = config.get("vmo-mediator","listen-port")

except:
    print("Error: Required items are not present in the configuration file.")
    exit(-1)

print("listenip: "+listenip)
print("listenport: "+listenport)
print("VM-interface: "+vmip)
print("Mail-interface: "+mailip)

lastsynchronize = "Unknown"
#
# Initialize the connection to the database
#
dbname="vmo3.sqlite"
database = db.initialize_database(dbname)
if database == False:
    print("Error: Unable to initialize the database.")
    exit(-1)


def synchronize_dbs():
    # Make a call to the voice mail application to get all users
    apistring = vmip+"/ucxn/users"

    print ("API String: "+apistring)
    try:

        resp = requests.get(apistring)
        print (resp)
    except requests.exceptions.RequestException as e:
        flash("ERROR: Error when attempting to synchronize database: "+str(e))

        return

    if resp.status_code != 200:
        flash ("ERROR: Synchronization failed to ("+apistring+"): "+" Status Code ("+str(resp.status_code)+"): "+str(resp.reason))
        return

    print (resp)
    data=resp.json()
    print(str(data))

    # For each user in the data received, see if the record already exists in our database and if so synchronize the records
    for user in data:

        emailid = user['Alias']
        ret, msg = db.search_database(dbname, "users", "Alias", emailid)

        # If we found the user check the out of office greeting:

        updatestring = ""
        if ret:
            print ("Found existing record")
            if msg['Extension'] != user['Extension']:
                updatestring += "Extension='"+user['Extension']+"'"

            print ("vmo db AlternateGreetingEnabled = "+msg['AlternateGreetingEnabled'])
            print ("ucxn db AlternateGreetingEnabled = "+user['AlternateGreetingEnabled'])
            if msg['AlternateGreetingEnabled'] != user['AlternateGreetingEnabled']:
                if updatestring != "":
                    updatestring += " and "
                updatestring += "AlternateGreetingEnabled='" + user['AlternateGreetingEnabled']+"'"

            if updatestring != "":
                print ("Updating record: "+emailid)

                ret, msg = db.update_database(dbname, "users", updatestring, "Alias='" + emailid + "'")
                print ("Return = "+str(ret) + " "+str(msg))
        else:
            print ("Did not find existing record")
            ret, msg = db.insert_into_database(dbname, "users", ObjectId=user['ObjectId'], Alias=user['Alias'], Extension=user['Extension'],CallHandlerObjectID=user['CallHandlerObjectId'],AlternateGreetingEnabled=user['AlternateGreetingEnabled'],Active="True")

    return





#
# Main Program Logic
#


# Route Point for generic message when web server is hit.
@app.route('/')
@app.route('/home.html')
def home():

    data = db.search_db(dbname, "users")

    return render_template("list-users.html", rows=data, ipaddress=vmip, lastsynchronized=lastsynchronize)




# Route point for displaying the about message
@app.route('/about')
def about():
    if WEBDEBUG:
        print_details(request)
    return render_template('about.html')


# Route point that will clear all the tables and displays the result.
@app.route('/clear-tables')
def cleartables():
    """
    Clears all the database tables
    @return: html page to show status
    """

    ret,guestmsg = db.delete_database(dbname, "users", "")
    if ret:
        users="Deleted"

    return render_template("clear-tables.html", users=users)


# This route will display the user table
@app.route('/syncdbs')
def syncdbs():

    """
    Displays the user table
    @return: html page of the table
    """
    # Make a call to the voice mail application to get all users
    synchronize_dbs()

    global lastsynchronize

    now = datetime.datetime.now()
    lastsynchronize=now.strftime("%m-%d-%Y %H:%M")

    print (lastsynchronize)

    data = db.search_db(dbname, "users")

    #return render_template("list-users.html", rows=data, ipaddress=vmip)
    return redirect("/", code=302)


# This route will toggle the status of a user that is selected
@app.route("/toggle_status/<emailid>", methods=('GET', 'POST'))
def toggle_status(emailid):

    if WEBDEBUG:
        print_details(request)

    print ("Toggling VMO Status for: "+emailid)

    ret, msg = db.search_database(dbname, "users", "Alias", emailid)
    print("Current Value of VMO Status: "+msg['Active'])

    if ret:
        value = msg['Active']
        if value == "True":
            value = "False"
        else:
            value = "True"

    updatestring = "Active='" + value +"'"
    print (msg['CallHandlerObjectId'])
    ret, msg = db.update_database(dbname, "users", updatestring, "Alias='" + emailid + "'")

    #TODO: Make a call to the mail exchange server to register a hook
    if value == "True":
        print ("Submitting a request to set an alert on: "+emailid)
    else:
        print ("Submitting a request to turn off the alert on: "+emailid)

    apistring = mailip + "/monitor"

    print(apistring)

    headers = {
        'Content-Type': 'application/json'
    }

    user = {}
    user['email'] = emailid
    user['status'] = value

    print(user)
    try:
        resp = requests.post(apistring, data=json.dumps(user),
                                 headers=headers)
    except requests.exceptions.RequestException as e:
        flash("ERROR: Error when attempting to toggle status of user : "+str(e))
        print(e)

    if resp.status_code == 200:
        data=resp.text
        print(str(data))
    else:
        flash ("ERROR: Synchronization failed to ("+apistring+"): "+" Status Code ("+str(resp.status_code)+"): "+str(resp.reason))

    return redirect("/", code=302)


# API Handler to Change the Out of Office Status
@app.route('/api/setstatus', methods=['POST','GET'])
def setstatus():

    if WEBDEBUG:
        print_details(request)

#    if not request.is_json:
#        return jsonify({"result": "Not JSON"}),400

    req_data = request.get_json(force=True, silent=True)


    try:
        email = req_data['email']
        status = req_data['status']
    except (KeyError, TypeError, ValueError):
        return jsonify({"result":"Invalid JSON"}),400

    try:
        message = req_data['message']
    except (KeyError, TypeError, ValueError):
        print("Incoming Message doesn't include a OOO message")
    else:
        print("Incoming Message does include a OOO message")
        print("The message is: '"+message+"'")


    print("Setting the status for: "+email+" to: "+ status)

    ret, msg = db.search_database(dbname, "users", "Alias", email)

    if not ret:
        return jsonify({"result":"Not Found"}),404


    apistring = vmip+"/ucxn/users/"+msg['CallHandlerObjectId']+"/greeting"

    headers = {
        'Content-Type': 'application/json'
    }

    jsonmsg = {}
    jsonmsg['action']=status
    if message:
        jsonmsg['message']=message


    print (apistring)
    print (jsonmsg)

    try:
        resp = requests.post(apistring,data=json.dumps(jsonmsg),headers=headers,timeout=10)
    except requests.exceptions.RequestException as e:
        flash("ERROR: Error when attempting to set status: "+str(e))
        return jsonify({"result":str(e)}),403

    print (resp.status_code)
    if resp.status_code == 200:
        data=resp.json()
        print(str(data))

        updatestring = "AlternateGreetingEnabled='" + status +"'"
        ret, msg = db.update_database(dbname, "users", updatestring, "Alias='" + email + "'")

        data = db.search_db(dbname, "users")

        return jsonify({"result":"True"}),200
    else:
        print("ItExecuted")
        flash ("ERROR: Unable to set status failed to ("+apistring+"): "+" Status Code ("+str(resp.status_code)+"): "+str(resp.reason))
        return jsonify({"result": "Internal Error"}),resp.status_code

@app.route('/api/setup', methods=['POST','GET'])
def setup():

    if WEBDEBUG:
        print_details(request)




    data = db.search_db(dbname, "users")
    for i in data:
        print ("Send Register Event to Email Server for: "+i[2]+" to "+i[6])

        apistring = mailip+"/monitor"

        print (apistring)

        headers = {
            'Content-Type': 'application/json'
        }

        user={}
        user['email'] = i[2]
        user['status'] = i[6]

        test_user = {
            "email": i[2],
            "status": i[6]
        }


        print ("Original Dict: "+json.dumps(user))
        print ("Clint's Format: "+json.dumps(test_user))
        try:
            response = requests.post(apistring, data=json.dumps(user),
                                     headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            print(e)

        else:
            print ("Response Code: "+str(response.status_code))
            print ("Response: "+response.text)
            if response.status_code == 200:
                data=response.text
                print(str(data))
                print("")


    return jsonify({"result": "True"}), 200

if __name__ == '__main__':
    app.run(debug=True,host=listenip,port=listenport)