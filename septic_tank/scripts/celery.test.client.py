#!/usr/bin/env python
import logging
import socket
from pipeline import Pipeline
from inputs import FileInput, ZeroMQInput, StdInput
from parsers import RegexParser 
from filters import ZuluDateFilter, RemoveFieldsFilter, GrepFilter, LCFilter, UniqFilter, AddFieldsFilter
from outputs import STDOutput, JSONOutput, SOLROutput, ZeroMQOutput
from dirwatcher import DirWatcher

logging.basicConfig(filename='./debug.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == "__main__":

    dw = DirWatcher(folder = "/localfs/celery/",
                    regex = '.*.log',
                    last_lines=0,
                    multiline = True,
                    multiline_regex = '^(\s+|Traceback|ValueError|UnboundLocalError|IntegrityError)') 

    add_server = AddFieldsFilter({'server' : socket.gethostname()})
    zmq_out = ZeroMQOutput(host='10.216.32.173',port=8002)
    pipeline = Pipeline(pipes = [dw,add_server,zmq_out])

    for data in pipeline:
        pass 
