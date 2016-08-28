#
# Author: Lucas Chaufournier
# Date: August 27,2016
# This file controls all the global values
#
#
#
#

#Variable that stores all the details for the experiment, setup in main
details = {}

#Variable that stores all the details for each workload, setup in main
workloads = []

#Variable that stores the configuration information to get for each machine
# Each key represents a directory where the commands are stored.
# If you want to add a new directory simply add a new key
# Each key represents a list of dicts of the form:
# {"heading":"","command":""}
configuration_options = {}

#Sample Config setup
#configuration_options["SET KEY HERE"] = []
#configuration_options["SET KEY HERE"].append({"heading":"SET HEADING IN FILE",command:" SET COMMAND TO RUN"})

#Represents all system config options
configuration_options["system"] = []
configuration_options["system"].append({"heading":"Kernel Version","command":"cat /proc/version"})
configuration_options["system"].append({"heading":"OS RELEASE","command":"cat /etc/*release* "})
configuration_options["system"].append({"heading":"Block Devices","command":"lsblk"})
configuration_options["system"].append({"heading":"CPUs ","command":"cat /proc/cpuinfo"})
configuration_options["system"].append({"heading":"Memory","command":"cat /proc/meminfo"})
configuration_options["system"].append({"heading":"Memory Max","command":"sudo lshw -short -C memory"})

#Represnts Networkign Specific options
configuration_options["networking"] = []
configuration_options["networking"].append({"heading":"MPTCP Configuration",\
                                    "command":"sudo sysctl -a | grep mptcp"})
configuration_options["networking"].append({"heading":"TCP Configuration",\
                                    "command":"sudo sysctl -a | grep tcp"})
configuration_options["networking"].append({"heading":"Networking Interfaces"\
                                    ,"command":"sudo lshw -class network"})
configuration_options["networking"].append({"heading":"IP Rules","command":"ip rule show"})
configuration_options["networking"].append({"heading":"IP Routes","command":"ip route"})
configuration_options["networking"].append({"heading":"MPTCP Route 1","command":"ip route show table 1"})
configuration_options["networking"].append({"heading":"MPTCP Route 2","command":"ip route show table 2"})

#Represents Hardware Specific Options
configuration_options["hardware"] = []
configuration_options["hardware"].append({"heading":"Hardware","command":"sudo lshw"})
