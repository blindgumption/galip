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
  this mechanism will survive logrotate as well
"""


import json
import sys 
import os.path as path 
import inotify.adapters as ina 
import inotify.constants as inc

def getFileComponents(name):
    """
    return (apspath, dirname, filename) if name is the name of a file, else throw exception.

    if 'name' is the name of a file, 
    get its absolute path and return that 
    along with the directory the file is in and the filename itself 
    """
    assert path.isfile(name), "input [{}] must be the name of a file".format(name)
    abs = path.abspath(name)
    (dirname, filename) = path.split(abs)
    return (abs, dirname, filename)


def isJson(tstr):
    """ if tstr is valid JSON, return object created from the string, else, return None """ 
    ret = None
    try:
        ret = json.loads(tstr)
    except ValueError:
        pass
    return ret


def getJsonObjectFromLog(binary_log):
    """ take the binary string and return an object if the string is valid JSON """ 
    log = binary_log.decode(errors='ignore')
    return isJson(log)


def getFileEvents(dirname, filename):
    """ generator yielding events on file, filename, in directory, dirname """
    inot = ina.Inotify()
    events_to_watch = inc.IN_MODIFY | inc.IN_CREATE | inc.IN_DELETE
    inot.add_watch(dirname, mask = events_to_watch)
    for event in inot.event_gen(yield_nones=False):
        (_, type_names, path, eventfile) = event
        if eventfile ==filename:
            for ev in type_names: yield ev


def getJsonObjectsFromFileInfinite(infile):
    """ 
    Read lines from the file and return objects if the line is valid JSON.
    Do this forever and ever, amen.

    this is a generator that will return objects based on the log line read from the file.
    If the log line is not valid JSON, it is ignored.

    The generator will keep the file open to keep pulling log lines as they are written.
    The generator will even detect when the log file is rotated and open the newly created file to keep reading logs.

    Notes on how this works:
      first, get a generator that listens for events on the given file.
      this generator blocks and returns events when the file is
      modified, written to, or created, after logrotate.
      The event generator is used within the while True to trigger the reading of more data
      If the file event is "created":
        the loop needs to make sure it has read everything from the file it already had open,
        then break out of the with ... loop to go back and open the newly created file 
        and read from that one.
        event notifications will follow the logrotate automagically  
    """ 
    (abs, dirname, filename) = getFileComponents(infile) 
    file_events = getFileEvents(dirname, filename)
    while True:
        with open(abs,'rb') as logs:
            #, first, get anything already in the file 
            for binary_log in logs:
                log_obj = getJsonObjectFromLog(binary_log)
                if log_obj: yield log_obj
            #, now, listen for file events and act accordingly 
            for fev in file_events:
                if fev == 'IN_DELETE': 
                    raise Exception("file [{}] was deleted".format(abs)) 
                for binary_log in logs:
                    log_obj = getJsonObjectFromLog(binary_log)
                    if log_obj: yield log_obj
                if fev == 'IN_CREATE': 
                    # getting a created event on the filename means the file we currently have opened 
                    # has been renamed and a new file of the same name has been created.   
                    #  this is the signature of a logrotate 
                    # by now, we should have already read what was left in the file that was moved.
                    # break will take us back to the top to open the new file
                    break


def getJsonObjectsFromFile(filename):
    """ simply read all lines from the file and return objects for valid JSON lines """ 
    with open(filename,'rb') as logs:
        for binary_log in logs:
            log_obj = getJsonObjectFromLog(binary_log)
            if log_obj: yield log_obj


""" examples of using the getJsonObjectsFromFile generator """ 

def printJsonLogs(filename, property_to_print):
    count = 0
    for log_obj in getJsonObjectsFromFile(filename):
        print(log_obj[property_to_print])
        count += 1
    print('retrieved {} objects from file {}'.format(count, filename))


def printJsonLogsUsingNext(filename, property_to_print):
    """ use next() and wait for more input """
    jobjs = getJsonObjectsFromFileInfinite(filename) 
    count = 0
    while True:
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
    object_property_to_print = 'message'
    if (len(sys.argv) < 2):
        print("Usage: readJsonFile.py <logfilename> [str:object_property_to_print]")
    else:
        logfileName = sys.argv[1]
    if (len(sys.argv) > 2): object_property_to_print = sys.argv[2]
    printJsonLogsUsingNext(logfileName, object_property_to_print)
