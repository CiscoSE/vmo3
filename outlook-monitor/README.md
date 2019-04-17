# VMO<sup>3</sup> outlook-monitor

## Description
Outlook-monitor is a Python Flask microservice that is one piece of the VMO<sup>3</sup> application. It listens for the vmo-mediator 
microservice to specify an Active Directory user to either start or stop monitoring. Outlook-monitor queries 
Microsoft Graph to determine if a users exists in Microsoft Azure Active Directory and then checks the 
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

### API Descriptions

#### Get MS Graph Authorization Token

**DESCRIPTION**
This API call will be used to get an Authorization Token that your application will use to make requests to 
Microsoft Graph.

**PATH:** https://login.microsoftonline.com/< your TENANT ID >/oauth2/token

**METHOD:** POST

**PARAMETERS:** 
```bash
client_id= < your client id >
client_secret= < your client secret >
resource= https://graph.microsoft.com
grant_type= client_credentials

```

```bash
headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
    }
```

**RETURN:** 
```bash
{
    "token_type": "Bearer",
    "expires_in": "3600",
    "ext_expires_in": "3600",
    "expires_on": "1555530120",
    "not_before": "1555526220",
    "resource": "https://graph.microsoft.com",
    "access_token": " < your super secret token >"
}
```


#### Get AD Users
**Description**
This API call will be used to query Active Directory for users.

**PATH:** https://graph.microsoft.com/v1.0/users

**METHOD:** GET

**PARAMETERS:** 
```bash
    headers = {
        'Authorization': "Bearer " + < your token>
    }
```

**RETURN:**

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
**Description**
This API call will be used to get the mailbox Automatic Reply Setting for a particular user.

**PATH:** https://graph.microsoft.com/v1.0/users/user@domain.com/mailboxSettings/automaticRepliesSetting

**METHOD:** GET

**PARAMETERS:** 
```bash
    headers = {
        'Authorization': "Bearer " + < your token >
    }
```

**RETURN:**
```bash
{
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('user%40domain.com')/mailboxSettings/automaticRepliesSetting",
    "status": "scheduled",
    "externalAudience": "none",
    "internalReplyMessage": "<html>\n<body>\n<div>Hello I am so glad my vacation is here, I may never return. </div>\n</body>\n</html>\n",
    "externalReplyMessage": "<html>\n<body>\n<div>Hello I am so glad my vacation is here, I may never return. </div>\n</body>\n</html>\n",
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
**Description:** 
This API call is used to syncronize with the vmo-mediator microservice. 
**/api/**

**METHOD:** GET

**PARAMETERS:** None

**RETURN:** 200 OK



#### Mediator Monitor API
**Description:** 
This API call is used by the vmo-mediator to POST a monitor request. 

**/api/monitor**

**METHOD:** POST

**PARAMETERS:**
```bash
{
    "email" : "user@domain.com",
    "status" : "True"
}	
```
**RETURN:**
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

<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/App_registration.gif" width="800" height="500" />


Give your application a name, Sign-on  URL and click **Create**


<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/Create_app.gif" width="300" height="300" />

 
Next you will need to generate a key for you application to use. 
Click **Settings > Keys**

<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/Settings_generate_key.gif" width="800" height="500" />


Give your Key a Description and Expiration time and click **Save** to generate the key

<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/Keys.gif" width="500" height="200" />

 
Our application with be interacting with Microsoft Graph via REST APIs. We will want to assign the appropriate level of permissions to grant acces only to the APIs we need and nothing more. 
Do this by checking the box next to the access you would like to assign. 

<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/Required_permission.gif" width="800" height="400" />


For this application we are going to enable 1 permission for Azure AD and three permissions for Microsoft Graph.

**Windows Azure Active Directory API Permissions**
1. Read directory data

<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/Enable_Access_AzureAD.gif" width="800" height="400" />


**Microsoft Graph API Permissions**
1. Read all users' full profiles
2. Read all user mailbox settings
3. Read directory data

<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/Enable_Access_Graph.gif" width="800" height="900" />

 
Finally you must click **Grant permissions** in order for your choices to take affect.

<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/Grant_permissions.gif" width="600" height="300" />


For more information take a look at this [tutorial](https://docs.microsoft.com/en-us/azure/active-directory-b2c/tutorial-register-applications#register-a-web-app)

## Executing the Application

This microservice was deployed onto the [Heroku](https://www.heroku.com/) cloud platform. 

Here is a fantastic [example](https://github.com/datademofun/heroku-basic-flask) of how to deploy a 
Python Flask application onto Heroku via ther Heroku toolbelt.

### Heroku deploy via GUI

You can also deploy via the Heroku dashboard

Under the **Deploy** menu choose GitHub as your Deployment method. This will link to the your GitHub repository 
containing the code.


<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/Heroku_GitHub_deploy.gif" width="900" height="400" />

Under the **Settings** menu, make sure to add in the Config variables. 

<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/Heroku_variables.gif" width="800" height="300" />

Back under the **Deploy** menu scroll down the **Manual Deploy** to deploy the application

<img src= "https://github.com/clintmann/vmo3/tree/master/outlook-monitor/images/Heroku_manual_deploy.gif" width="950" height="300" />


