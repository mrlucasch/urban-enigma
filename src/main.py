#
# Author: Lucas Chaufournier
# Date: August 27,2016
# This file controls functionality for starting the program
#
#
#
#
from parse_config import *
from test import *
from global_vals import *
#import global_vals
from exp_prep import *


## Start Program here
if __name__ == "__main__":
    global details
    global workloads
    # If config file not specified error out
    if len(sys.argv) != 2:
        print "Usage: python main.py config_file"
        sys.exit(0)
    #Store argument 1 as configuration file to use.
    configFile = sys.argv[1]

    #Call function to parse file, store in variables
    global_vals.details,global_vals.workloads = parseFile(configFile)

    #Create filestructure for storing results
    createFileStructure()

    #Collect the configured information from all the machines
    #collect_config("spark1.local","ubuntu","key","sample1/forloop")
    collect_info_from_machines(0)
