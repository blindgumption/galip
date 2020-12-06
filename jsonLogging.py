#!/usr/bin/env python3
"""
wrapper on logging to use JSON for log to file output 

Sssee https://pypi.org/project/python-json-logger/  for JSON formatting 
logs to stdout will be as simple as possible to avoid long gibberish from the screen reader.
Could not get the python logging module to format the timestamp in the iso8601 format I wanted.
was able to find way using datetime and CustomJasonFormatter 

TODO: at some point, the logging config should be moved to a file or dict.
"""

import logging 
from pythonjsonlogger import jsonlogger 
import datetime
import time
import sys 


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] =  datetime.datetime.fromtimestamp(record.created).astimezone().isoformat()

""" logfile defaults to local directory using timestamp in name but can be set explicitly """
logfileName = './jsonlog_{}.log'.format(time.time())
def setLogfile(filename):
    logfileName = filename


def getJsonLogger(name):
    # setup console handler with only module, level, and message 
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    cf = logging.Formatter('%(module)s %(name)s %(levelname)s %(message)s')
    ch.setFormatter(cf)

    # setup file handler to log JSON with more info and debug default 
    fh = logging.FileHandler(logfileName)
    fh.setLevel(logging.DEBUG)
    jf = CustomJsonFormatter('%(timestamp)s %(module)s %(name)s %(levelname)s %(message)s')
    fh.setFormatter(jf)

    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


if __name__ == '__main__':
    mainLogger = getJsonLogger('mainLogger')
    secondLogger = getJsonLogger('mainLogger.second')

    mainLogger.info('info log from mainLogger')
    secondLogger.info('info log from secondLogger')

    mainLogger.debug('debug log from mainLogger')
    secondLogger.debug('debug log from secondLogger')

    mainLogger.warning('warning log from mainLogger')
    secondLogger.warning('warning log from secondLogger')
