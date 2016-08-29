#
# Author: Lucas Chaufournier
# Date: August 27,2016
# This file controls functionality for parsing configuration files
#
#
#
#
import ConfigParser
import sys


#data structure that specifies the type for the given key
config_types = {"workload_num":"int","results_dir":"string","master":"string",\
                "slaves":"list","workloads":"string","experiment":"string",\
                "num_trials":"int","workload":"string",\
                "monitor_results":"list","machines":"list",\
                "start":"time","finish":"time","args":"list","monitors":"list",\
                "username":"string","key_location":"string","env_script":"string"}


# Function that parses lines that are lists
# returns a list
def parseList(line):
    new_list = line.split(",")
    for index in range(0,len(new_list)):
        new_list[index] = new_list[index].replace("\"","")
    return new_list

#Function that parses lines that are time
# returns an int
def parseTime(line):
    if line == "START":
        return 0
    if line == "END":
        return 0
    new_line = line.replace("min","")
    return int(new_line)

#Function that parses lines that are int
# returns an int
def parseInt(line):
    return int(line)


## Function to parse the configuration file.
## Returns tuple (experiment_details,workloads)
def parseFile(configFile):

    # Create a configuration file parser
    Config = ConfigParser.ConfigParser()

    #Open the config file so we can read it
    Config.read(configFile)

    #list to store workload details
    workloads = []

    #dictionary to store experiment values in
    experiment_details = {}
    #iterate through general section so we can overall information for test run
    for options in Config.options("General"):
        #store the experiment details in dictionary
        temp_line = Config.get("General",options)
        if config_types[options]== "string":
            experiment_details[options] = temp_line
        elif config_types[options] == "time":
            experiment_details[options] = parseTime(temp_line)
        elif config_types[options] == "int":
            experiment_details[options] = parseInt(temp_line)
        elif config_types[options] == "list":
            experiment_details[options] = parseList(temp_line)
    #index to use for workloads array
    index = 0
    # for every workload, store experiment details
    for section in Config.sections()[1:]:
        #create a new dictionary and add it to workloads
        workloads.append({})
        #iterate through worload options
        for options in Config.options(section):
            temp_line = Config.get(section,options)
            if config_types[options]== "string":
                workloads[index][options] = temp_line
            elif config_types[options] == "time":
                workloads[index][options] = parseTime(temp_line)
            elif config_types[options] == "int":
                workloads[index][options] = parseInt(temp_line)
            elif config_types[options] == "list":
                workloads[index][options] = parseList(temp_line)
        for i in range(0,len(workloads)):
            workloads[i]["monitor_processes"] = {}
        index += 1
    return experiment_details,workloads
