#
# Author: Lucas Chaufournier
# Date: August 27,2016
# This file controls functionality for getting machine configurations
#
#
#
#
import global_vals
import paramiko

#Function that collects info for a specific command and writes to a given file
def collect_info(client,machine,cmd,heading,location):
    #open the file to write to. In this case /TOPLEVELRESULTS/config/networking|system|hardware/hostname
    with open(location+"/"+machine,"a") as datafile:
        #Write the heading to the file
        datafile.write(heading+"\n")
        #Run the remote command
        stdin,stdout,stderr = client.exec_command(cmd)
        #Store results of stdout
        out_data = stdout.read()

        #Write stdout to file
        datafile.write(out_data+"\n")

        #Store results of stderr
        err_data = stderr.read()
        #Write stderr to file
        datafile.write(err_data+"\n")
        #Write inbetween stuff
        datafile.write("---\n")
        datafile.write("\n")

#Function that collects all configuration for a machine
def collect_config(host,user,key_location,file_location):
    #Read private key
    key = paramiko.RSAKey.from_private_key_file(key_location)
    #create a client
    client = paramiko.SSHClient()
    #Set misc options
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #connect client
    client.connect(hostname=host,username=user,pkey=key)

    #Iterate through configuration options defined in global_vals
    #For each options(aka System,Networking,hardware) run the provided command
    #Record result in folder config/system|networking|hardware/hostname
    for options in global_vals.configuration_options:
        for commands in global_vals.configuration_options[options]:
            collect_info(client,host,commands["command"],commands["heading"],\
                        file_location+"/config/"+options)

#function that iterates through all machines for a workload and calls collect_config
def collect_info_from_machines(index):
    #fetch username to use for ssh
    username = global_vals.details["username"]
    #fetch key to log in with
    key = global_vals.details["key_location"]
    #create the results location for all data
    result_location = global_vals.details["results_dir"]+\
                    global_vals.workloads[index]["results_dir"]

    #iterate through machines listed in workload and collect info
    for machine in global_vals.workloads[index]["machines"]:
        collect_config(machine,username,key,result_location)
#collect_config("spark1.local","ubuntu","KEY","sample1/forloop")
