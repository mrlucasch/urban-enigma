#
# Author: Lucas Chaufournier
# Date: August 27,2016
# This file controls functionality for interacting with file system.
# i.e. Creating directories, checking directories
#
# A sample filestructure can be found in docs/fs_tree

import os
from datetime import datetime
import sys
#from global_vals import *
import global_vals


def copyFiles():
    #store username
    user = global_vals.details["username"]
    key = global_vals.details["key_location"]
    #iterate through slaves and copy files
    for slaves in global_vals.details["slaves"]:
        #ssh command
        ssh1 = user+"@"+slaves
        ssh2 = " -i "+key+" "+ssh1
        #create new /workloads dir and fix permissions
        os.system("ssh "+ssh2+" 'sudo mkdir -p /workloads && sudo chown "+user+": /workloads'")
        #copy files to /workloads
        os.system("scp -r "+" -i "+key+" "+global_vals.details["workloads"]+" "+ssh1+":/workloads")


#function to make a directory. If it exists, append the current time to the name
# returns a tuple of the form (true | false, new_name)
# True means operation was a success with provided name
# False means operation was a failure with provided name
def mkdir(dir_name):
    try:
        #Try to create the directory
        os.mkdir(dir_name)
        #If successful return true and the given name
        return (True,dir_name)
    except OSError: # catch any errors
        #store current time and date as new suffix
        suffix = datetime.now().strftime('%Y-%m-%d_%H:%M:%S:%f')
        try:
            # Try to make directory with new suffix attached(SHOULD BE UNIQUE)
            os.mkdir(dir_name+"_"+suffix)
        except OSError: #Catch error just in case
            print "Unable to create directories!" # PRINT ERROR MESSAGE
            sys.exit(0) # EXIT
    #retrieve original name so we can modify it
    index = dir_name.rfind('/')

    #Return false so they know to use the new dir name
    return (False,dir_name[index+1:]+"_"+suffix)




# Function to set up file structure for experiments
def createFileStructure():

    #Create the top level directory for results
    success,res = mkdir(global_vals.details["results_dir"])

    #Check if mkdir was sucessful
    if not success:
        #if not successful store new name
        global_vals.details["results_dir"] = res

    #Check if top level directory has trailing slash
    #if true append value without slash
    if global_vals.details["results_dir"][len(global_vals.details["results_dir"])-1] != "/":
        global_vals.details["results_dir"]=global_vals.details["results_dir"]+"/"

    for workload in global_vals.workloads:
        #Create the top level directory for results
        success,res = mkdir(global_vals.details["results_dir"]+workload["results_dir"])
        #Check if mkdir was sucessful
        if not success:
            #if not successful store new name
            workload["results_dir"] = res

        #Create the configuration directory
        success,res = mkdir(global_vals.details["results_dir"]+workload["results_dir"]+"/config")

        #Iterate through the config_options dict defined in global_Vals to create folders
        for options in global_vals.configuration_options:
            #Create the networking directory
            success,res = mkdir(global_vals.details["results_dir"]+workload["results_dir"]+"/config/"+options)

        #Create a directory for results
        success,res = mkdir(global_vals.details["results_dir"]+workload["results_dir"]+"/results")

        #Create a directory for monitor results
        success,res = mkdir(global_vals.details["results_dir"]+workload["results_dir"]+"/results/monitors")

        #Create a directory to store the workload results
        success,res = mkdir(global_vals.details["results_dir"]+workload["results_dir"]+"/results/workload")

        #Iterate through the machines and create a directory for each under monitors
        for machines in workload["machines"]:
            #Create a directory for each machine under monitors
            success,res = mkdir(global_vals.details["results_dir"]+workload["results_dir"]+"/results/monitors/"+machines)
