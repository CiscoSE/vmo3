#!/usr/bin/env bash

echo
echo "################################################"
echo "Thank you for using the Exchange Monitor App "
echo "--"
echo "This script will collect environment variables"
echo "for the main.py script"
echo "################################################"
echo

echo "Press Enter to continue..."
read confirm

echo "Please enter the Active Directory TENANT ID : "
read TENANT

echo "Please enter the Graph Application CLIENT ID : "
read CLIENT_ID

echo "Please enter the Graph Application CLIENT SECRET : "
read CLIENT_SECRET

echo "Please enter the MEDIATOR Application IP ADDRESS : "
read MEDIATOR_IP

echo "Please enter the MEDIATOR Application PORT : "
read MEDIATOR_PORT

echo "Please enter the LISTENER Application IP ADDRESS : "
read LISTENER_IP

echo "Please enter the LISTENER Application PORT : "
read LISTENER_PORT


export TENANT
export CLIENT_ID
export CLIENT_SECRET
export MEDIATOR_IP
export MEDIATOR_PORT
export LISTENER_IP
export LISTENER_PORT

python main.py
