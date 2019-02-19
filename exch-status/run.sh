#!/usr/bin/env bash

echo
echo "################################################"
echo "This script will collect environment variables"
echo "for the exch-usr-status.py script"
echo "################################################"
echo

echo "Press Enter to continue..."
read confirm



export TENANT
export CLIENT_ID
export CLIENT_SECRET

python schedule.py