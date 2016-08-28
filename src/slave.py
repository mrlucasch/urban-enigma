#
# Author: Lucas Chaufournier
# Date: August 27,2016
# This file controls restful server information
#
#
#
#

from flask import Flask, request
from flask_restful import Resource, Api
from subprocess import Popen,PIPE

app = Flask(__name__)
api = Api(app)




# Function to run the monitor command
# Returns a tuple containing the index in processes as well as the lust of ps
def runMonitor(cmd,processes):
    #record the index for the new process
    index = len(processes)
    #Append the process to the list of processes while running it.
    processes.append(Popen(cmd , shell=True, stdout=PIPE, stderr=PIPE))
    #return the process list and index
    return (index,processes)


def setupEnvironment():
    cmd = "python environment.py"
    p = Popen(cmd , shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if(p.returncode != 0):
        print "Return code: ", p.returncode
        print err.rstrip()
    resultsLine = out.rstrip()
    return resultsLine



# Class to control the monitors
class Monitor(Resource):
    #List to store all processes running or killed
    processes = []

    #GET function for rest. Used for checking status of monitor
    def get(self,pid):
        #store the status code for processes using poll
        status_code = self.processes[pid].poll()
        #if status_code is none type then still running
        if status_code == None:
            status = "Running"
        #if the status_code is 127 then the command failed to run
        elif status_code == 127:
            status = "Command Not Found"
        #if the status_code is not these then it was likely terminated
        else:
            status = "Terminated using "+str(status_code)
        #return the status message
        return {"Status":status}

    #Put function for rest
    def put(self,command):
        #check if the command was monitor
        if command == "monitor":
            #record the monitor script to run
            script = request.json['script_name']
            #run the monitor script and record the index and process list
            index,processes = runMonitor(script,self.processes)
            #return the pid of the process as well as the index
            return {"pid":self.processes[index].pid,"index":index}
        #check if the command was kill
        elif command == "kill":
            #record the given index
            index = request.json['index']
            # store the process
            p = self.processes[index]
            # kill the process
            p.kill()
            #return status kill
            return {"status":"killed"}
        #check if command was setup. this sets up the environment for things to
        #run
        elif command == "setup":
            setupEnvironment()
            return {"status":"configured"}


api.add_resource(Monitor,'/<string:command>','/<int:pid>')
if __name__ == '__main__':
    app.run(debug=True)
