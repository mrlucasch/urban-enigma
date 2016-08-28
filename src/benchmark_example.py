#Author: Lucas Chaufournier
#
# This script is used to run benchmarks on various vms and containers. 
#
#########Running the Script################
# python benchmark.py configFile
#
# To debug:
# python benchmark.py configFile d
##########Steps Performed###########
#
# 1. Parses the config and produces three dicts: experiment, vms,containers
#	Experiment: used to hold general infor for the benchmark
#	Vms: Holds each of the vms info
#	Containers: Holds all container data
# 2. Starts the vms and waits a set amount of time for them to initizalize
# 3. Starts the containers and waits a set amount of time for them to initialize.
# 4. It makes the directory structure. This consists of the root being the name of the experiment
#    then there is a directory for each vm, container and monitor being run. Inside each of these
#    is an out folder for the results. Need to be carefule because data is overwritten each time 
#    the experiment is run.
# 5. Transfers the scripts to be run to the vms and the containers. Fixes permissions along the way.
# 6. The monitors on the host are then started up and left running.
# 7. The benchmarks on the containers are started followed by the vms.
# 8. Every set amount of time the script checks the directories of the remaining machines to see
#    if the results file is present. If so that machine is removed from the list.
# 9. When the list is empty the script stops the host monitoring and promptly exits. 
#
#####################

import ConfigParser
import os
import time
import errno
import sys


#configFile = "configContainers"

configFile = sys.argv[1]

if len(sys.argv)>2 and sys.argv[2] == "d":
	debug = True
else:
	debug = False


benchmarks = {'filebench':'run_filebench.sh','iozone':'run_iozone.sh','fio':'run_fio.sh','bonnie':'run_bonnie.sh','nbench':'run_nbench.sh','ycruncher':'run_ycruncher.sh','mmtests':'run_mmtests.sh','kernel':'run_compile.sh'}
benchmark_status = []

def parseOptions(obj,key):
    #create a temporary string for options
    tempstr =  obj[key]
    #SPlit on the comma store array
    obj[key]=tempstr.split(',')
    #return the list
    return obj

#Function to parse the configuration file and organize the data in the file.
def parseFile():
    print "Now parsing configuration file!"
    # Open up the configuration file parser
    Config = ConfigParser.ConfigParser()
    # Open up the file to read in the current directory
    Config.read(configFile)
    #Dictionary to store information on vms(KEY:Seciton Name)
    vms = {}
    #Dictionary to store info on containers(KEY:Section Name)
    containers = {}
    #Dictionary to store info on vmcontainers(KEY:Section Name)
    vmcontainers = {}
    #Dictionary to store info on experiment(Key:Section Name)
    experiment = {}
    for options in Config.options("General"):
        experiment[options] = Config.get("General",options)
    #Seperate list of options for monitoring
    experiment = parseOptions(experiment,"monitors")
    #Loop through all the machine sections 
    for section in Config.sections()[1:]:
        #If the type of the section is a vm
        if Config.get(section,"type") == "vm":
            #temp dictionary to hold machine info
            options = {}
            #Scan through all the options for the machine
            for opt in Config.options(section):
                #Append to the dictionary using the option as a key
                options[opt] = Config.get(section,opt)
            options = parseOptions(options,"options")
            #Append the dictionary to the vm dictionary
            vms[section] = options
        #Check if the type of the section is Containter
        elif Config.get(section,"type") == "lxc":
            #Temp dict to hold machine info
            options = {}
            #Loop through all options for the machine
            for opt in Config.options(section):
                #Append to temp dict using option as key
		if opt == "container_opts":
			options[opt] = Config.get(section,opt).split(",")
                else:
			options[opt] = Config.get(section,opt)
            #Append the dict to the vm dict
            options = parseOptions(options,"options")
            containers[section] = options
	elif Config.get(section,"type") == "vmlxc":
            #Temp dict to hold machine info
            options = {}
            #Loop through all options for the machine
            for opt in Config.options(section):
                #Append to temp dict using option as key
		if opt == "container_opts":
			options[opt] = Config.get(section,opt).split(",")
                else:
			options[opt] = Config.get(section,opt)
            #Append the dict to the vm dict
            options = parseOptions(options,"options")
            vmcontainers[section] = options
    return (experiment,(vms,containers,vmcontainers))

#Function to start each of the vms
def startVMS(vms):
    print "Now Starting VMS"
    print vms
    for name in vms:
        #This is the command to be run. Make sure to daemonize qemu
        cmd = "cd /extra/vm_resources/"+name+" && sudo qemu-system-x86_64 -readconfig "+name+"cfg -m "+vms[name]["memory"]+" -daemonize -display none"
        if debug:
            print cmd
        os.system(cmd)
    wait = 30
    #Sleep for a minute to allow vms to initialize
    print "Waiting for vms to initialize("+str(wait)+" seconds)"
    time.sleep(wait)


def startContainers(containers):
    print "Now starting Containers"
    for name in containers:
        cmd = "lxc-start -n "+name+" -d"
        if debug:
            print cmd
        os.system(cmd)
    print "Applying configuration options"
    for name in containers:
	for opt in containers[name]["container_opts"]:
		cmd = "lxc-cgroup -n "+name+" "+opt+" "+containers[name][opt]
		if debug:
		    print cmd
		os.system(cmd)
    wait = 30
    print "Waiting for containers to initialize("+str(wait)+" seconds)"
    time.sleep(wait)


#Function to start containers in a vm
def startVMContainers(experiment,containers):
    print "Now starting VM Containers"
    cmd = "ssh -F "+experiment["sshfile"]+" "+experiment["vmhost"]+" 'bash -s' <<'ENDSSH'\n" 
    for con in containers:
    	cmd +="sudo lxc-start -n "+con+" -d\n"
    for name in containers:
	for opt in containers[name]["container_opts"]:
		cmd +="sudo lxc-cgroup -n "+name+" "+opt+" "+containers[name][opt]+"\n"
    cmd += "ENDSSH"
    if debug:
	print cmd
    os.system(cmd)
    wait = 30
    print "Waiting for containers to initialize("+str(wait)+"seconds)"
    time.sleep(wait)

#Function to create a directory and raise exception if error(does not raise error if already exists)
def mkdir(path):
    # Try to make the directory if fail print raise exception, ignores if they exist
    try:
        #print path
        os.makedirs(path)
    #Raise error if it can not make directory
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
            print "FAIL"

#Start vmstat
def vmstat(experiment):
    #Runs vmstat for memory updating every 15 seconds
    cmd = "vmstat 10 -S m >"+experiment["experiment"]+"/vmstat/results & "
    os.system(cmd)

#Function to start host monitoring.
def hostMonitors(experiment):
    print "Starting host monitors!"
    if "vmstat" in experiment["monitors"]:
        vmstat(experiment)
    else:
        print "No monitors to run"
    #Function to create the directory structure of the experiment
def makeDirectoryStructure(experiment,vms,containers,vmcontainers):
    print "Now making directory structure for experiment"
    #Root Path for experiment
    root_path = experiment["directory"]+"/"+experiment["experiment"]
    mkdir(root_path)
    #Iterate through the vms and create directories for them
    for vm in vms:
        #Path for the directory that represents the vm
        path = root_path+"/"+vm
        #Make the directory that represents the vm
        mkdir(path)
        #Make directory for vms results
        mkdir(path+"/out")
        #Appends the vm onto the list for checking status later.
        benchmark_status.append(vm)
    #Iterate through containers and create directories for them
    for cont in containers:
        #Path for the directory that represents the Container
        path = root_path+"/"+cont
        #Make the directory that represents the container
        mkdir(path)
        #Make directory for containers results
        mkdir(path+"/out")
        #Appends the container onto the list for checking status later
        benchmark_status.append(cont)
    for cont in vmcontainers:
        #Path for the directory that represents the Container
        path = root_path+"/"+cont
        #Make the directory that represents the container
        mkdir(path)
        #Make directory for containers results
        mkdir(path+"/out")
        #Appends the container onto the list for checking status later
        benchmark_status.append(cont)

    for mon in experiment["monitors"]:
        #Path for the directory that represents monitoring on host
        path = root_path+"/"+mon
        #Make directory for monitor
        mkdir(path)
    #make directory where we store done flags for machines
    mkdir(path+"/done")



    
def transferToVMContainerInsideVM(experiment,containers): 
    print "Transferring to vm containers" 
    #transfer scripts to vm first
    cmd = "scp -F "+experiment["sshfile"]+" -r "+experiment["scriptpath"]+"/*"
    cmd += " "+experiment["vmhost"]+":"+experiment["guestexpdir"]+"/."
    if debug:
	print cmd
    os.system(cmd)
    #transfer sshconfig file
    cmd = "scp -F "+experiment["sshfile"]+" "+experiment["sshfile"]+" "+experiment['vmhost']+":~/."
    print cmd
    os.system(cmd)
    #Transfer to each lxc
    cmd ="ssh -F "+experiment["sshfile"]+" "+experiment["vmhost"]+" 'bash -s' << 'ENDSSH'\n" 
    for con in containers:
	cmd += "scp -F ~/"+experiment["sshfile"]+" -r "+experiment["scriptpath"]+"/*"
	cmd += " "+con+":"+experiment["guestexpdir"]+"/.\n"
    cmd += "ENDSSH"
    if debug:    
	print cmd
    os.system(cmd)

def transferToVM(experiment,vms):
    print "Transferring Scripts to VMs"
    print "Current Directory: "
    os.system("pwd")
    #SSH Command to copy the files to the directory in the vm
    for vm in vms:
        #Creates the command to transfer the vm.
        # -F flag is for the sshconfig so we can specify address and key to be used.
        cmd = "scp -F "+experiment["sshfile"]+" -r "+experiment['scriptpath']+"/*"
        #cmd +="/"+benchmarks[vms[vm]['bench']]+" "
        cmd += " "+vm+":"+experiment["guestexpdir"]+"/."
        if debug:        
            print cmd
        #Run the command to transfer.
        os.system(cmd)
        #Reset the cmd string
        cmd = ""
        # adds ssh and the config file to use to cmd string
        cmd += "ssh -F "+experiment["sshfile"]+" "
        #adds the hostname and the chmod command
        cmd += vm+" \"sudo chmod a+x /"+experiment['scriptpath']+"/"
        #adds the file to chmod
        cmd += benchmarks[vms[vm]['bench']]+"\""
        os.system(cmd)
        if debug:
            print cmd

def transferToContainers(experiment,containers):
    print "Transferring Scripts to containers"
    for cont in containers:
	cmd = "lxc exec "+cont+" sudo rm -rf /benchmarks/*" 
        cmd = "lxc file push --mode=0777 "+experiment['scriptpath']+"/*"
        #cmd +="/"+benchmarks[containers[cont]['bench']]+" "
        cmd += " "+cont+experiment["guestexpdir"]+"/"
        if debug:        
            print cmd
	os.system(cmd)

def runBenchmarkVM(experiment,vms):
    print "Running Benchmarks on vms"
    for vm in vms:
        cmd = "ssh -F "+experiment["sshfile"]+" "
        cmd += vm+" -fn \""+experiment["guestexpdir"]+"/./"+benchmarks[vms[vm]['bench']]+" "
        #These are the command line arguments for the script
        cmd += experiment["guestexpdir"]+"/scriptResults "+experiment["resultshostuser"]+" "
        cmd += experiment["resultshost"]+" "+experiment["directory"]+"/"+experiment["experiment"]+"/"+vm+"/out/. "
        #iterate through benchmark options for the vm. Add them to the command. 
        #Need to escape each one, as some have spaces.
        for opt in vms[vm]['options']:
            cmd +="\\"
            cmd += "\""+opt+"\\\" "
        cmd += ">/dev/null &\""
        if debug:
	    print cmd
        os.system(cmd)

def runBenchmarkContainer(experiment,containers):
    print "Running Benchmarks on containers"
    #iterate through containers
    for con in containers:
        #change permission on script before running it.
        cmd = "lxc exec "+con+" -- sudo chmod a+x "+experiment["guestexpdir"]+"/"+benchmarks[containers[con]['bench']]
       # print cmd
        #os.system(cmd)
        #run the actual benchmark
        cmd = "lxc exec "+con+" -- /bin/bash -c "
        cmd += "\""+experiment["guestexpdir"]+"/./"+benchmarks[containers[con]['bench']]+" "
	#These are the command line arguments for the script
        cmd += experiment["guestexpdir"]+"/scriptResults "+experiment["resultshostuser"]+" "
        cmd += experiment["resultshost"]+" "+experiment["directory"]+"/"+experiment["experiment"]+"/"+con+"/out/. "
        #iterate through benchmark options for the vm. Add them to the command. 
        #Need to escape each one, as some have spaces.
        for opt in containers[con]['options']:
            cmd += "\\\""+opt+"\\\" "
	cmd += " >/dev/null &\" & "
        if debug:
            print cmd
        os.system(cmd)

def checkStatus(experiment):
    #make a copy of the items to prevent errors when removing from list
    status_copy = benchmark_status
    #Iterate through all remaining items in status list
    for item in status_copy:
        #If the directory is empty the benchmark is still running.
        if not os.listdir(experiment["directory"]+"/"+experiment["experiment"]+"/"+item+"/out"):
            continue
        #otherwise it is not empty and benchmark is complete.
        else:
            print "Complete"
            #Remove item from list since it is complete.
            benchmark_status.remove(item)

experiment,(vms,containers,vmcontainers) = parseFile()

if len(vms) != 0:
	startVMS(vms)
if len(containers) != 0 :
	startContainers(containers)
if len(vmcontainers) != 0:
	startVMContainers(experiment,vmcontainers)
makeDirectoryStructure(experiment,vms,containers,vmcontainers)

if len(vms) != 0:
	transferToVM(experiment,vms)
if len(containers) != 0:
	transferToVM(experiment,containers)
if len(vmcontainers) != 0:
	transferToVM(experiment,vmcontainers)

hostMonitors(experiment);
if len(vms) != 0:
	runBenchmarkVM(experiment,vms)
if len(containers) != 0:
	runBenchmarkVM(experiment,containers)
if len(vmcontainers) != 0:
	runBenchmarkVM(experiment,vmcontainers)





#OLD NOT USED FUNCTIONS FOR NOW
#transferToVMContainer(experiment,vmcontainers)
#transferToContainers(experiment,containers)



#Starts the monitors for the host
#runBenchmarkContainer(experiment,containers)


print "Now Checking status"
status = True
while status:
    print "Now checking status"
    time.sleep(20)
    checkStatus(experiment)
    print benchmark_status
    if len(benchmark_status) == 0:
	status = False
print "Script all finished!"
print "Stopping monitor"
os.system("sudo pkill -9 vmstat ")
