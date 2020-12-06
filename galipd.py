#!/usr/bin/env python3
"""
the module that is the galipd systemd service 

galipd.processAccessLogs(filename) will continuously read lines from filename.
If the line is syntactically valid JSON, and the log line contains a "remote_addr" field, 
the value for 'remote_addr' will be used to find the geolocation from which the request originated.

The geolocation data will be stored in a database with some meta data 
the data can be accessed later using the galip module also in this package. 
""" 


import os
import jsonLogging
from readJsonFile import getJsonObjectsFromFileInfinite as log_generator 


jogger = jsonLogging.getJsonLogger("galipd")


def getGeolocation(ip_addr): 
    jogger.info("looking up location for IP address: %s", ip_addr)


def processAccessLogs(filename):
    jogger.info("Processing access logs from {}".format(filename))
    logs = log_generator(filename)
    while True:
        try:
            alo = next(logs)   # access log object  
            getGeolocation(alo['remote_addr'])
        except ValueExcept:
            jogger.warning("hmmm...something bad happened?  Carry on")

if __name__ == '__main__':
    logfile = os.getenv('GALIP_ACCESS_LOG_FILE')
    if not logfile: logfile = '/var/log/nginx/access.log'
    processAccessLogs(logfile) 
