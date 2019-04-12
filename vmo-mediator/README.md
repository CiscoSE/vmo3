# VMO<sup>3</sup> - vmo-mediator

## Description
The vmo-mediator is the microservice that is responsible for bridging together the functionality of the Outlook Monitor and the TODO.  It allows the user to select what users will be monitored for Out of Office functionality.   In addition, it will forward the appropriate requests between the Outlook Monitor and the TODO.

## Functional Details
When the vmo-mediator first starts it will be looking for either API requests or process functionality from the GUI.  

### Database Synchronization
On the main GUI, there is an option for database synchronization.   When you start this function, the vmo-mediator will go out to the Unity Connection server and download all the users that are in the database.   From here we can activate the VMO functionality for individual users and monitor their functionality.

### Outlook Monitor
The application will also receive request calls from the Outlook Monitor piece.   There is an exposed REST API that will be used to communicate status to and from the Outlook Monitor and vmo-mediator.   Anytime, the Outlook Monitor detects a change in the OOO status, it will alert the vmo-mediator via a REST API and then the appropriate status will be communicated to the Unity Connection

## Requirements

The vmo-mediator.py was writting using Python 3.6.   It also seems to work with Python 3.7 as well.   The ```requirements.txt``` file describes the requirements of modules when using the vmo-mediator application.   You can install these requirements by doing the following:

```bash
pip install -r requirements.txt 
```



## Configuration
The vmo-mediator.py uses a configuration file to handle all the options that need to be set.   This file will be located into the directory where the vmo-mediator.py is run.    The file is called ```package-config.ini```   The following is an example:

```bash
[vmo-mediator]
listen-ip: {Insert IP to Listen on}
listen-port: {Insert Port to Listen on}
vm-interface: {Insert Voicemail Interface IP:Port Module}
mail-interface: {Insert Mail Interface IP:Port Module}
webdebug: False
```
#### listen-ip
This ip address represents the ip address where the vmo-mediator runs on.    Normally, you can set it to ```0.0.0.0``` which would represent all ip addresses.

#### listen-port
This port is the TCP port that the local application is bound to.   You can use any port that is unused currently.

#### vm-interface
This is the full URL to the voice mail interface application

#### mail-interface
This is the full URL to the outlook interface module

#### wedbdebug
This parameter is either ```True``` or ```False```.   It represents if we turn on enhanced debugging.

## Executing the Application
To start the application, once the requirents are installed (see above), you can do the following:

```python vmo-mediate.py```

You will then see the following output:

```bash
VMO3 Mediator Starting...

Configuration Options:
listenip: 0.0.0.0
listenport: 5000
VM-interface: http://ucxn.test.com
Mail-interface: https://mail-interface.test.com
Initializing the database: vmo3.sqlite
2.6.0

```

Then to start the GUI just bring up a Web Browser to the IP Address specified in the configuration.    For example:

```http://127.0.0.0:5000```

## GUI

## API Description




