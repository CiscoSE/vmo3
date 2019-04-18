# VMO<sup>3</sup> outlook-monitor

## Description
Outlook-monitor is a Python Flask microservice that is one piece of the VMO<sup>3</sup> application. It listens for 
the vmo-mediator microservice to specify an Active Directory user to either start or stop monitoring. Outlook-monitor 
queries Microsoft Graph to determine if a users exists in Microsoft Azure Active Directory and then checks the 
Office 365 Outlook/Exchange Automatic Replies (Out of Office) status of that user. 

## Functional Details
Outlook-monitor begins by checking if the vmo-mediator microservice is reachable. If reachability is
established a function is run to query Microsoft Graph for an Authorization Token. This token will expire in 1 hr, so 
the function is scheduled to request a new token approximately every 58 minutes to ensure there is always an active 
Authorization Token. Once a token has been received, outlook-monitor listens for a POST request from vmo-mediator.

When a POST is received from vmo-mediator, outlook-monitor will parse the request for the users email address 
and status. The status field indicates whether vmo-mediator wants to start or stop monitoring this user. 
If status is True, outlook-monitor makes an API call to Microsoft Graph to verify that the user contained in the 
request exist in Active Directory and then will make a second API call to check that users Outlook Automatic Replies 
setting. This status along with the text from the users Out of Office message is sent to the vmo-mediator.

Continuous, real-time interaction with vmo-mediator allows for users to be added and their monitor status 
to be changed dynamically. 

Let's take a look at the work flow. The diagram below is not exhaustive, however, it will help explain at a high level 
the components that make up this microservice and their roles. 


<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Outlook_monitor_workflow.gif" />


1.  This microservice can be executed locally by executing the run.sh bash script and entering your variables at the 
prompts. It can also be executed in a PaaS environment. For our testing, we used the Heroku cloud platform. Instructions 
for executing this microservice in Heroku are listed below in the 
<a href="#executing-the-application">Executing the Application</a> section

2. The variable values are sent to main.py, which is the Main Module for this microservice. 

3. After reading in the variable values, main.py enables MEDIATOR SYNC API which is simply a URL, and waits.
 
4. A user browse to the MEDIATOR SYNC API URL will trigger a sync up with the vmo-mediator microservice. 

5. The mediator_sync.py module is called. 

6. The purpose of mediator_sync.py is to determine if the vmo-mediator microservice is accessible. It accomplishes this
by initiating a simple GET request to the vmo-mediator URL. 

7. If the vmo-mediator is available and functioning properly it will respond with a 200 OK

8. The response from the vmo-mediator is sent back to main.py to be processed. 

9. If the response from vmo-mediator it is a 200 OK, main.py will call the auth_token function in the get_token.py module. 
main.py will also schedule this "get token" workflow to run every 58 minutes in order for their to alway be an active 
token available. 

10. The auth_token function will make a POST request to the Microsoft Graph Get Token API to get an Authorization Token.

    ```bash
    https://login.microsoftonline.com/{tenantID}/oauth2/token

    ```

11. Microsoft Graph will respond back with an Authorization Token. The token will have an expiration of 3600 seconds. 

12. main.py will then schedule the process_users function to run every 2 seconds. 

    12a. The process_users function will first look at the VMOusers list to determine if it contains any users. At initial 
start-up it will not. 

    12b. If the process_users function finds users in VMOusers, it will call the post_mediator function in mediator_post.py
which will post the user information to the vmo-mediator MEDIATOR POST API.

13. When the VMO<sup>3</sup> application the vmo-mediator microservice will POST the first user to be monitored to the 
MONITOR API. Once the application is up and running, the vmo-mediator will POST request to the MONITOR API to monitor
new users or make a request to stop monitoring existing users. The POST request will contain the users email address and
monitor status.

    ```bash
    {
      "email" : ”user@domain.com",
      "status" : "True"
    }
    ```

14. The monitor_users function in main.py checks if there was anything POSTED from vmo-mediator. If there was the data 
is parsed to extract the users email address and monitor status.

15. monitor_users then calls the check_activedir_users function in the checkMSgraph.py module.

16. The check_activedir_users function will the send a GET request to the MS Graph Check AutoReply API to get the 
users in Active Directory.

    ```bash
    https://graph.microsoft.com/v1.0/users
    ```

17. The MS Graph Check AutoReply API will respond with the users in Active Directory. 

18. The data is send back to the monitor_users function where it is parsed to determine if the email address POSTED 
from vmo-mediator exists in Active Directory.

19. If the email address exist in Active Directory and the monitor status of the user from vmo-mediator is set to TRUE, 
the user and their status is added to VMOusers.

20. The process_users function, which was scheduled at start-up to check VMOusers ever 2 seconds, will now find a user
and status in VMOusers. If the users status is TRUE, which means we want to monitor that users Out of Office status, 
this will trigger a call to the check_auto_reply function in the checkMSgraph.py module. 

21. The check_auto_reply function in the checkMSgraph.py module will send a GET request to the MS Graph Check AutoReply
API to determine the users current Automatic Replies Setting. 

    ```bash
    https://graph.microsoft.com/v1.0/users/{user email address}/mailboxSettings/automaticRepliesSetting
    ```

22. The MS Graph Check AutoReply API will respond with the users AutoReply "status" along with the "internalReplyMessage"
and "externalReplyMessage".

    ```bash
    {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('user%40domain.com')/mailboxSettings/automaticRepliesSetting",
        "status": "scheduled",
        "externalAudience": "none",
        "internalReplyMessage": "<html>\n<body>\n<div>Hello I am so glad my vacation is here, I may never Return. </div>\n</body>\n</html>\n",
        "externalReplyMessage": "<html>\n<body>\n<div>Hello I am so glad my vacation is here, I may never Return. </div>\n</body>\n</html>\n",
        "scheduledStartDateTime": {
        "dateTime": "2019-04-17T16:00:00.0000000",
        "timeZone": "UTC"
        },
        "scheduledEndDateTime": {
        "dateTime": "2019-04-18T16:00:00.0000000",
        "timeZone": "UTC"
        }
    }
    ```
23. The check_auto_reply function will send this data back to the process_users function where it will be parsed. 
If the status matches the status in VMOusers for that particular user (email_address), nothing has changed, 
so no action is taken.

24. If, however, the status does not match what is in VMOusers for the particular user, this indicates that the user 
has made a change to their AutoReplySettings or Out of Office status and we need to take action to alert the 
vmo-mediator microservice.

25. A POST request will be made to the MEDIATOR POST API to alert the vmo-mediator microservice that a user they have 
requested be monitored, has made a change to their AutoReplySettings or Out of Office status. The post_mediator function
in the mediator_post module will sent vmo-mediator the payload shown below. The message will be the externalReplyMessage
which will later be translated from text to speech and become the users voicemail greeting. 

    ```bash
    profile_payload = {
                    "email": email_address,
                    "status": ooo_profile_status,
                    "message": message
    }
    ```


### API Descriptions

#### Get MS Graph Authorization Token

**Description:** This API call will be used to get an Authorization Token that your application will use to make requests to 
Microsoft Graph. https://docs.microsoft.com/en-us/azure/active-directory/develop/v1-protocols-oauth-code

**Path:** https://login.microsoftonline.com/{tenantID}/oauth2/token

**Method:** POST

**Parameters:**

   ```bash
    client_id= {clientID}
    client_secret= {clientSecret}
    resource= https://graph.microsoft.com
    grant_type= client_credentials

    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        }
   ```

**Return:**

   ```bash
    {
        "token_type": "Bearer",
        "expires_in": "3600",
        "ext_expires_in": "3600",
        "expires_on": "1555530120",
        "not_before": "1555526220",
        "resource": "https://graph.microsoft.com",
        "access_token": " <your super secret token>"
    }
   ```


#### Get AD Users
**Description:** This API call will be used to query Active Directory for users.

**Path:** https://graph.microsoft.com/v1.0/users

**Method:** GET

**Parameters:**

   ```bash
       headers = {
           'Authorization': "Bearer " + {your token}
       }
   ```

**Return:**

```bash
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users",
    "value": [
        {
            "businessPhones": [],
            "displayName": "User Name",
            "givenName": "User",
            "jobTitle": null,
            "mail": "user@domain.com",
            "mobilePhone": null,
            "officeLocation": null,
            "preferredLanguage": "en-US",
            "surname": "Mann",
            "userPrincipalName": "user@domain.com",
            "id": "< user id >"
        }
}
```


#### Get Mailbox Automatic Reply Setting
**Description** This API call will be used to get the mailbox Automatic Reply Setting for a particular user.

**Path:** https://graph.microsoft.com/v1.0/users/{user email address}/mailboxSettings/automaticRepliesSetting

**Method:** GET

**Parameters:** 
   ```bash
       headers = {
           'Authorization': "Bearer " + {your token}
       }
   ```

**Return:**
   ```bash
   {
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('user%40domain.com')/mailboxSettings/automaticRepliesSetting",
    "status": "scheduled",
    "externalAudience": "none",
    "internalReplyMessage": "<html>\n<body>\n<div>Hello I am so glad my vacation is here, I may never Return. </div>\n</body>\n</html>\n",
    "externalReplyMessage": "<html>\n<body>\n<div>Hello I am so glad my vacation is here, I may never Return. </div>\n</body>\n</html>\n",
    "scheduledStartDateTime": {
        "dateTime": "2019-04-17T16:00:00.0000000",
        "timeZone": "UTC"
    },
    "scheduledEndDateTime": {
        "dateTime": "2019-04-18T16:00:00.0000000",
        "timeZone": "UTC"
    }
}
   ```


#### Mediator Sync API
**Description:** This API call is used to syncronize with the vmo-mediator microservice. 
**Path:** /

**Method:** GET

**Parameters:** None

**Return:** 200 OK



#### Mediator Monitor API
**Description:** This API call is used by the vmo-mediator to POST a monitor request. 

**Path:** /monitor

**Method:** POST

**Parameters:**

   ```bash
    {
        "email" : "user@domain.com",
        "status" : "True"
    }	
   ```
**Return:**

   ```bash
   <h1>You would like to monitor user@domain.com True</h1>
   ```

## Requirements
* Azure Active Directory
* Office 365 Outlook/Exchange mailbox(es)
* Cloud platform (PaaS) - not a strict requirement, but makes things easier. This microservice was tested in Heroku.
* Code written in Python 3.6.8

**Note:** This application will leverage the Microsoft Graph APIs.

## Getting Started with Microsoft Graph
In order to interact with Microsoft Graph your application must have an access token. 
To get an access token, the application must be able to successfully authenticate to the 
Azure Active Directory.  

The first thing we must do is register our application so that it can authenticate and 
receive a token from our Azure Active Directory Tenant.

### Application Registration
In your Azure portal

Choose **Azure Active Directory > App registrations > New application registration**

<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/App_registration.gif" width="800" height="500" />


Give your application a name, Sign-on  URL and click **Create**


<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Create_app.gif" width="300" height="300" />

 
Next you will need to generate a key for you application to use. 
Click **Settings > Keys**

<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Settings_generate_key.gif" width="800" height="500" />


Give your Key a Description and Expiration time and click **Save** to generate the key

<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Keys.gif" width="500" height="200" />

 
Our application with be interacting with Microsoft Graph via REST APIs. We will want to assign the appropriate level of permissions to grant acces only to the APIs we need and nothing more. 
Do this by checking the box next to the access you would like to assign. 

<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Required_permission.gif" width="800" height="400" />


For this application we are going to enable 1 permission for Azure AD and three permissions for Microsoft Graph.

**Windows Azure Active Directory API Permissions**
1. Read directory data

<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Enable_Access_AzureAD.gif" width="800" height="400" />


**Microsoft Graph API Permissions**
1. Read all users' full profiles
2. Read all user mailbox settings
3. Read directory data

<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Enable_Access_Graph.gif" width="800" height="900" />

 
Finally you must click **Grant permissions** in order for your choices to take affect.

<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Grant_permissions.gif" width="600" height="300" />


For more information take a look at this [tutorial](https://docs.microsoft.com/en-us/azure/active-directory-b2c/tutorial-register-applications#register-a-web-app)

## Executing the Application

Option 1: Local

run.sh will allow users to enter the necessary variables and execute outlook-monitor locally. This is a great option for testing and 
if all the microservices (vmo-mediator and uc-connector) are not running external to your network.  

Option 2: PaaS - recommended

This microservice was deployed onto the [Heroku](https://www.heroku.com/) cloud platform. 

Here is a fantastic [example](https://github.com/datademofun/heroku-basic-flask) of how to deploy a 
Python Flask application onto Heroku via their Heroku toolbelt.

### Heroku deploy via GUI

You can also deploy via the Heroku dashboard

Under the **Deploy** menu choose GitHub as your Deployment method. This will link to the your GitHub repository 
containing the code.


<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Heroku_GitHub_deploy.gif" width="900" height="400" />

Under the **Settings** menu, make sure to add in the Config variables. 

<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Heroku_variables.gif" width="800" height="300" />

Back under the **Deploy** menu scroll down the **Manual Deploy** to deploy the application

<img src= "https://github.com/clintmann/vmo3/blob/master/outlook-monitor/images/Heroku_manual_deploy.gif" width="950" height="300" />


