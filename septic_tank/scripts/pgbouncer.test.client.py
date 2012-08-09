#!/usr/bin/env python
import logging
import socket
from pipeline import *
from inputs import *
from parsers import *
from filters import *
from outputs import *
from dirwatcher import *

logging.basicConfig(filename='./debug.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == "__main__":

    dw = DirWatcher(folder="/localfs/pgbouncer/",regex='.*.log',last_lines=0) 
    add_server = AddFieldsFilter({'server' : socket.gethostname()})
    zmq_out = ZeroMQOutput(host='10.216.32.173',port=8003)
    pipeline = Pipeline(pipes = [dw,add_server,zmq_out])
    for data in pipeline:
        pass 
