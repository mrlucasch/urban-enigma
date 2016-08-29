#
# Author: Lucas Chaufournier
# Date: August 27,2016
# This file controls setting environment information
# This file must print 0 if things are correct. If not print 1
# These can be the only things that are printed!
#
#
#
import subprocess
from subprocess import Popen,PIPE
import sys
import os

debug = False

###Runs sysctl and returns the value
def check_value(key):
	output = subprocess.check_output("sudo sysctl -n "+key, shell=True)
	return output.replace("\n","")


###Runs sysctl and returns the value
def set_value(key,value):
    #use sysctl to set key to value
    cmd = "sudo sysctl -w "+key+"="+"\""+value+"\""
    #use subprocess to run it
    p = Popen(cmd , shell=True, stdout=PIPE, stderr=PIPE)
    #get output
    out, err = p.communicate()
    # if return code is not 0 there was an error
    if(p.returncode != 0):
        return 1
    resultsLine = out.rstrip()
    return 0

## Reads the given filename and returns a dict with the key being the sysctl key and the value being the expected
def read_file(filename):
	#file descriptor to operate on
	f = open(filename,"r")
	# Dict for the vaues
	expected = {}
	for line in f:
		# Split along equals sign
		res = line.split("=")
		#Replace new line at end of line
		expected[res[0]] = res[1].replace("\n","")
	#Close the file
	f.close()
	#Return the dict
	return expected


#function that sets kernel options with sysctl
def configure_kernel_options(expected):
    for key in expected:
        #set value to needed value
        res = set_value(key,expected[key])
        if res == 1:
            if debug == True:
                print "Failed at setting value"
            print res
            exit(1)

#function to double check value
def doublecheck(expected, actual,key):
    #if matches success, return 0
	if expected == actual:
		return 0
	else:
		return 1

# For every item in the expected dict, check the value.
def validate(expected):
	for key in expected:
        #check the current system value
		actual = check_value(key)
        #if there is a list then we neeed to handle it specially
		if " " in expected[key]:
            #validate the list regardless of order
			res= validate_list(expected[key],actual,key)
		else:
            #double check value
			res = doublecheck(expected[key],actual,key)
        #if a 1 was returned thats an error. so print and exit
        if res == 1:
            if debug == True:
                print "Failed the double check"
            print 1
            exit(1)

## If a list is returned, this function is called to compare the values regardless of order
def validate_list(expected,actual,key):
	expected_list = expected.split(" ")
	actual_list = actual.split(" ")
	if set(expected_list) == set(actual_list):
		return 0
	else:
        return 1
#store the  config file name
filename = sys.argv[1]
if len(sys.argv) == 3:
    debug = True
#check if file exists
if not os.path.isfile(filename):
    if debug == True:
        print "File not found"
    print 1
    exit(1)

#read the actual file
expected = read_file(filename)

#set the kernel options
configure_kernel_options(expected)

#double check that everything is good
validate(expected)

#if we made it this far. We are good. Print 0
print 0
