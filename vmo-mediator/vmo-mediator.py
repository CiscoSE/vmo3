import configparser
import requests
import datetime
from utilities import print_details
from flask import Flask,jsonify,request,render_template,redirect
import db

print("VMO3 Mediator Starting...\n")

print("Configuration Options:")

app = Flask(__name__,static_url_path='/static')

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

    resp = requests.post(apistring)
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

    return redirect("/", code=302)


# API Handler to Change the Out of Office Status
@app.route('/api/setstatus', methods=['POST','GET'])
def setstatus():

    if WEBDEBUG:
        print_details(request)

    req_data = request.get_json()
    email=req_data['email']
    status=req_data['status']

    print("Setting the status for: "+email+" to: "+ status)

    ret, msg = db.search_database(dbname, "users", "Alias", email)
    print(msg)


    apistring = vmip+"/ucxn/users/"+msg['CallHandlerObjectId']+"/greeting/"+status

    print (apistring)

    resp = requests.post(apistring)
    data=resp.json()
    print(str(data))

    updatestring = "AlternateGreetingEnabled='" + status +"'"
    ret, msg = db.update_database(dbname, "users", updatestring, "Alias='" + email + "'")

    data = db.search_db(dbname, "users")

    return jsonify({"result":"True"})


if __name__ == '__main__':
    app.run(debug=True,host=listenip,port=listenport)