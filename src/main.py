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
import getopt,sys
import slave
import master





## Start Program here
if __name__ == "__main__":
    global details
    global workloads

    #variable to store config file name
    configFile =""
    #help string to print when needed
    help_string = "SLAVE MODE: python main.py -s | MASTER MODE: python main.py -m"
    try:
        #parse arguments
        opts, args = getopt.getopt(sys.argv[1:],"hsm:")
    except getopt.GetoptError: #if error print help string and exit
        print help_string
        sys.exit(2)
    # iterate through arguments
    for opt, arg in opts:
        # if help mode requested, print help and exit
        if opt == '-h':
            print help_string
            sys.exit()
        # if slave set start up restful server
        elif opt in ("-s", "--slave"):
            print 'Running as a slave'
            slave.slave()
        #if master store the config file
        elif opt in ("-m", "--master"):
            print 'Running as a master'
            config_file = arg
            master.master(config_file)
        else:
            print help_string
            sys.exit(2)











    #Collect the configured information from all the machines
    #collect_config("spark1.local","ubuntu","key","sample1/forloop")
    #collect_info_from_machines(0)
