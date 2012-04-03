#!/usr/bin/env python
import logging
from inputs import StdInput
from parsers import RegexParser
from filters import ZuluDateFilter, RemoveFieldsFilter, GrepFilter, LCFilter
from outputs import JSONOutput, STDOutput
from pipeline import Pipeline

# create a log called debug.log in this directory
logging.basicConfig(filename='./debug.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == "__main__":

    # The logs we are going to parse look like this...
    #
    # 2012-04-03 09:22:14.684057 - ERROR, "bob" - 10.0.0.2: some message
    #
    # We use a regular expression parser to parse the log.  Below are some
    # regular expressions that parser will use.
    #
    # note 
    #   1. the use of substitution and capturing
    #   2. ordering of regular expressions does not matter
    #   3. see regexes.py for some re-usable regular expressions
    #
    regs = { 'yyyy-mm-dd': '\d{4}-\d{2}-\d{2}',
             'hh:mm:ss' : '\d{2}:\d{2}:\d{2}',
             'datetime' : '(?P<date>{{yyyy-mm-dd}} {{hh:mm:ss}}).\d+',
             'level' : '(?P<level>[A-Z]+)',
             'user' : '(?P<user>\w+)',
             'ip' : '(?P<ip>\d+.\d+.\d+.\d+)',
             'msg' : '(?P<msg>.*)',
             'samplelog' : '{{datetime}} - {{level}}, "{{user}}" - {{ip}}: {{msg}}'
    }              

    # read from stdin
    stdin = StdInput()

    # remove all records that contain jbruce before parsing
    remove_jbruce = GrepFilter(regex='jbruce', reverse=True)

    # parse the sample log file
    p = RegexParser(regs = regs, use = ['samplelog'])

    # remove all records that contain DEBUG level
    remove_debug = GrepFilter(regex='DEBUG', reverse=True, fields=['level'])

    # output to stdout in easy to read json format
    jsout = JSONOutput(sort_keys=True, indent=2)

    # try swapping outputs from jsout to stdout
    stdout = STDOutput()

    # create the pipeline
    pipeline = Pipeline(pipes = [stdin,remove_jbruce,p,remove_debug,jsout])
    
    # run data through the pipeline
    for data in pipeline:
        pass 
