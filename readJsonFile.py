#!/usr/bin/env python3
""" 
read lines of text expected to be in JSON format

lazy iterator to get JSON objects from file
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