#!/bin/bash


echo "Installing Pre-reqs"
sudo apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev zlib1g-dev

echo "Installing Paramiko"
sudo pip install paramiko

echo "Installing flask"
pip install flask

echo "Installing requests"
pip install requests

echo "Installing flask_restful"
pip install flask_restful
