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

#Function that runs the setup environment script. Wait until completed to continue
def setupEnvironment(env_script):
    #create the command
    cmd = "/workloads/./"+env_script
    #open process
    p = Popen(cmd , shell=True, stdout=PIPE, stderr=PIPE)
    #start/read
    out, err = p.communicate()
    #check for errors, return 1 if errored
    if(p.returncode != 0):
        print "Return code: ", p.returncode
        return 1
        #print err.rstrip()
    #format results
    #resultsLine = out.rstrip()
    #return 0 for success
    return 0



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
            #fetch script to run
            script = request.json['script_name']
            #run the set environment script
            result = setupEnvironment(script)
            #if zero returned no errors. This does not mean env is correct!
            if result ==0:
                return {"status":"configured"}
            #otherwise we saw an error
            else:
                return {"status":"unconfigured"}


api.add_resource(Monitor,'/<string:command>','/<int:pid>')
if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')
