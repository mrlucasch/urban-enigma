#
# Author: Lucas Chaufournier
# Date: August 27,2016
# This file controls functions for the master to run
#
#
#
#
#from requests import put,get
import paramiko
import requests
import getopt,sys
import json
from parse_config import *
import global_vals
from exp_prep import *
from filesystem import *
port ="5000"


def sftp(host,source,dest):
    hostname = host
    username = global_vals.details["username"]
    port = 22
    key_location = global_vals.details["key_location"]
    key = paramiko.RSAKey.from_private_key_file(key_location)

    try:
        t = paramiko.Transport((hostname, port))
        t.connect(username=username, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(source,dest )

    finally:
        t.close()





#Function to fetch monitor results
def fetchMonitorResults(index):
    dest = global_vals.details["results_dir"]+global_vals.workloads[index]["results_dir"]+"/results/"
    for machines in global_vals.workloads[index]["machines"]:
        for result in global_vals.workloads[index]["monitor_results"]:
            sftp(machines,"/workloads/"+result,dest+"monitors/"+machines+"/"+result)

#Function to fetch results file
def fetchWorkloadResults(host,destination):
    sftp(host,"/workloads/out",destination)


#Function to check the status of a monitor
#returns the status
def checkStatus(host,pid):
    url = "http://"+host+":"+port+"/"+str(pid)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.get(url, headers=headers)
    print r.content

#Function to reset slaves
def reset(host):
    url = "http://"+host+":"+port+"/reset"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.put(url, headers=headers)
    print r.content

#Function to launch the workload
def launchWorkload(workload,host,workload_location):
    url = "http://"+host+":"+port+"/start"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {'script_name': "/workloads/"+workload_location+"/"+workload}
    r = requests.put(url, data=json.dumps(data), headers=headers)
    print r.json()

#Function to check run the monitor
#Take the host and the command to run
def runMonitor(host,cmd):
    url = "http://"+host+":"+port+"/monitor"
    print url
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {'script_name': cmd}
    r = requests.put(url, data=json.dumps(data), headers=headers)
    print r.json()["index"]
    return r.json()["index"]

#Function to kill the monitor
# returns status
def killMonitor(host,pid):
    url = "http://"+host+":"+port+"/kill"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {'index': pid}
    r = requests.put(url, data=json.dumps(data), headers=headers)
    print r.content

#Function to run setup on node
def runSetup(host,script):
    url = "http://"+host+":"+port+"/setup"
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {"script_name":script}
    r = requests.put(url, data=json.dumps(data), headers=headers)
    print r.content


def talk_to_slave(host,command,):
    url = "http://localhost:8080"
    data = {'sender': 'Alice', 'receiver': 'Bob', 'message': 'We did it!'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)


def test(args):
    host = "spark1.local"
    help_string = ""
    try:
        #parse arguments
        opts, args = getopt.getopt(args,"c:i:")
    except getopt.GetoptError: #if error print help string and exit
        print help_string
        sys.exit(2)
    command = ""
    pid = ""
    # iterate through arguments
    for opt, arg in opts:
        # if slave set start up restful server
        if opt in ("-c"):
            command = arg
        elif opt in ("-i"):
            pid = arg
        else:
            print help_string
            sys.exit(2)
    if command == "status":
        checkStatus(host,pid)
    elif command == "kill":
        killMonitor(host,pid)
    elif command == "start":
        runMonitor(host,"top")
    elif command == "setup":
        runSetup(host,"/workspace/experiment_framework/src/workloads/configure_for_loop.sh")


##Function to run setup on all machines
def setupSlaves(machines,setup_script):
    for hosts in machines:
        runSetup(hosts,setup_script)


#Function to reset all slaves
def resetMonitors(index):
    for hosts in global_vals.workloads[index]["machines"]:
            reset(hosts)
            global_vals.workloads[index]["monitor_processes"][hosts]=[]


#Function to kill remaining machines
def killMonitors(index):
    for hosts in global_vals.workloads[index]["machines"]:
        for mon in range(0,len(global_vals.workloads[index]["monitor_processes"][hosts])):
            killMonitor(hosts,mon)

#Function to run monitors on machines
def startMonitors(index,monitors,results):
    for hosts in global_vals.workloads[index]["machines"]:
        global_vals.workloads[index]["monitor_processes"][hosts]=[]
        for mon in range(0,len(monitors)):
            pid = runMonitor(hosts,str(monitors[mon])+">>"+"/workloads/"+str(results[mon]))
            global_vals.workloads[index]["monitor_processes"][hosts].append(pid)


#Function to run for masters
#takes configFile as argument
def master(configFile):
    #Call function to parse file, store in variables
    global_vals.details,global_vals.workloads = parseFile(configFile)

    #Create filestructure for storing results
    createFileStructure()
    #Copy the workloads directory to the slaves
    copyFiles()

    #iterate through workloads and run experiments
    for i in range(0,len(global_vals.workloads)):
        #run the setup on all machines listed
        setupSlaves(global_vals.workloads[i]["machines"],"/workloads/"+global_vals.details["workloads"]+"/"+global_vals.workloads[i]["env_script"])

        #Collect all the info for machines
        collect_info_from_machines(i)

        #start monitors on machines
        startMonitors(i,global_vals.workloads[i]["monitors"],global_vals.workloads[i]["monitor_results"])

        #Start the actual workload
        status = launchWorkload(global_vals.workloads[i]["workload"],global_vals.details["master"],global_vals.details["workloads"])

        #if status ==0:

        #Kill the monitors
        killMonitors(i)

        destination = global_vals.details["results_dir"]+global_vals.workloads[i]["results_dir"]+"/results/workload/out"
        #Gather Results
        fetchWorkloadResults(global_vals.details["master"],destination)
        fetchMonitorResults(i)
        #Reset
        resetMonitors(i)

#test(sys.argv[1:])
