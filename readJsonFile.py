#!/usr/bin/env python3
""" 
generators that return objects from files containing lines of text each which is syntactically valid JSON

lazy iterator to get JSON objects from file.
The expectation is each line in the file is syntactically valid JSON.
Lines that are not valid JSON will be ignored.

There are two generators in this module, they both return the same types of objects.
The difference is in how long they run.
getJsonObjectsFromFile(filename) will iterate through each line in the file and return an object if the line is valid JSON
getJsonObjectsFromFileInfinite(filename) will open filename, iterate through all lines currently in the file, then wait for new lines to be added to the file.
  As new lines are added, the generator returns objects if the added line is valid JSON.
"""


import json
import sys 
import time


def isJson(tstr):
    """ if tstr is valid JSON, return object created from the string, else, return None """ 
    ret = None
    try:
        ret = json.loads(tstr)
    except ValueError:
        pass
    return ret


def getJsonObjectFromLog(binary_log):
    log = binary_log.decode(errors='ignore')
    return isJson(log)


def getJsonObjectsFromFileInfinite(filename):
    with open(filename,'rb') as logs:
        while True:
            """ this doesn't survive logrotate, need another solution... """ 
            for binary_log in logs:
                log_obj = getJsonObjectFromLog(binary_log)
                if log_obj: yield log_obj


def getJsonObjectsFromFile(filename):
    with open(filename,'rb') as logs:
        for binary_log in logs:
            log_obj = getJsonObjectFromLog(binary_log)
            if log_obj: yield log_obj


""" examples of using the getJsonObjectsFromFile generator """ 

def printJsonLogs(filename):
    count = 0
    for log_obj in getJsonObjectsFromFile(filename):
        print(log_obj['request'])
        count += 1
    print('retrieved {} objects from file {}'.format(count, filename))

def printJsonLogsUsingNext(filename):
    """ use next() and wait for more input """
    jobjs = getJsonObjectsFromFileInfinite(filename) 
    count = 0
    while True:
        time.sleep(3)
        print('found {} objects so far'.format(count))
        try:
            jobj = next(jobjs)
            while jobj:
                print(jobj['request'])
                count += 1
                print('count is now {}'.format(count))
                jobj = next(jobjs)
        except StopIteration:
            print('caught StopIteration')
            ## pass 


if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Usage:readJsonFileprintjsonlogs.py <logfilename> ")
    else:
        logfileName = sys.argv[1]
    printJsonLogsUsingNext(logfileName)