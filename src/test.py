
#
# Author: Lucas Chaufournier
# Date: August 27,2016
# This file controls functionality for testing various functionality
#
#
#
#

from parse_config import *
from filesystem import *

ERROR="\033[31m"
PASS="\033[32m"
RESET="\033[0m"

def test(testname,expected,actual):
    if expected == actual:
        print testname+PASS+" Success"+RESET
    else:
        print testname+ERROR+" Failed"+RESET
        print "\tExpected: "+str(expected)
        print "\tActual: "+str(actual)

def booleanTest(testname,expected,result,excess):
    if result == expected:
        print testname+PASS+" Success"+RESET
    else:
        print testname+ERROR+" Failed"+RESET
        print "\t"+excess


def runFSTests():
    success,name = mkdir("sample")
    booleanTest("Fresh Directory",True,success,name)
    success,name = mkdir("sample")
    booleanTest("Duplicate Directory",False,success,name)


def runConfigTests():

    configFile = "../sample_config"
    details,workloads = parseFile(configFile)

    expected_details = {}
    expected_details["workload_num"] = 2
    expected_details["results_dir"] = "sample1"
    expected_details["master"] = "spark1.local"
    expected_details["slaves"] = ["spark1.local","spark2.local","spark3.local"]
    expected_details["workloads"] = "workloads"

    expected_workloads = []
    expected_workloads.append({})
    expected_workloads.append({})
    expected_workloads[0]["experiment"] = "for_loop"
    expected_workloads[0]["num_trials"] = 3
    expected_workloads[0]["workload"] = "for_loop.sh"
    expected_workloads[0]["results_dir"] = "forloop"
    expected_workloads[0]["machines"] = ["spark1.local","spark2.local","spark3.local"]
    expected_workloads[0]["start"] = 0
    expected_workloads[0]["finish"] = 0
    expected_workloads[0]["args"] = [""]
    expected_workloads[0]["monitors"] = ['"vmstat 10"', '"free -mh"']
    expected_workloads[0]["monitor_results"] = ['"vmstat.dat"','"memory.dat"']


    expected_workloads[1]["experiment"] = "while_loop"
    expected_workloads[1]["num_trials"] = 3
    expected_workloads[1]["workload"] = "while_loop.sh"
    expected_workloads[1]["results_dir"] = "whileloop"
    expected_workloads[1]["machines"] = ["spark1.local","spark2.local","spark3.local"]
    expected_workloads[1]["start"] = 0
    expected_workloads[1]["finish"] = 0
    expected_workloads[1]["args"] = [""]
    expected_workloads[1]["monitors"] = ['"vmstat 10"', '"free -mh"']
    expected_workloads[1]["monitor_results"] = ['"vmstat.dat"','"memory.dat"']

    for option in expected_details:
        test(option,expected_details[option],details[option])

    for i in range(0,len(expected_workloads)):
        for option in expected_workloads[i]:
            test(option,expected_workloads[i][option],workloads[i][option])
