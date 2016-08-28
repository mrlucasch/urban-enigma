#
# Author: Lucas Chaufournier
# Date: August 27,2016
# This file controls functions for the master to run
#
#
#
#
from requests import put,get


url = "http://localhost:8080"
data = {'sender': 'Alice', 'receiver': 'Bob', 'message': 'We did it!'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)
