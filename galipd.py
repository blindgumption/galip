#!/usr/bin/env python3

##  generic notes for galipd.py 
# I was getting an error when processing a request with garbage characters    
#     UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92 in position 95: invalid start byte
# found this post helpful: https://stackoverflow.com/questions/22216076/unicodedecodeerror-utf8-codec-cant-decode-byte-0xa5-in-position-0-invalid-s
# most of the comments are about trying to figure out what the character is supposed to be.  
# I just wanted to ignore the character as it was from some hacking URL
# what worked was opening the file as binary, read each line, decode and ignore errors.
## 

import os
import json 
import time
import sys 
import logging


logger = logging.getLogger("test-logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

def is_json(tstr):

    ret = None
    try:
        ret = json.loads(tstr)
    except ValueError:
        pass
    return ret


def get_location(ip_addr): 
    logger.info("looking up location for IP address: %s", ip_addr)


def read_ad_nauseam(filename):
    with open(filename, 'rb') as logs:
        while(True):
            time.sleep(3)  # easier to keep track of the sleep indentation here...
            ## logger.debug('anyting to read in the access logs?')
            for binary_log in logs:
                logger.info('=-=-=-=-')
                log = binary_log.decode(errors='ignore')
                log_obj = is_json(log)
                if log_obj:
                    get_location(log_obj['remote_addr'])
                else: 
                    logger.warning('WARNING: log statementis NOT JSON!!')


if __name__ == '__main__':
    logfile = os.getenv('GALIP_ACCESS_LOG_FILE')
    if not logfile: logfile = '/var/log/nginx/access.log'
    read_ad_nauseam(logfile)


