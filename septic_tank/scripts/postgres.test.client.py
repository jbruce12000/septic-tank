#!/usr/bin/env python
import logging
import socket
from pipeline import Pipeline
from inputs import FileInput, ZeroMQInput, StdInput, MultilineFileInput
from parsers import RegexParser, CSVParser
from filters import ZuluDateFilter, RemoveFieldsFilter, GrepFilter, LCFilter, UniqFilter, AddFieldsFilter
from outputs import STDOutput, JSONOutput, SOLROutput, ZeroMQOutput
from dirwatcher import DirWatcher

logging.basicConfig(filename='./debug.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

import csv

if __name__ == "__main__":

    dw = DirWatcher(folder='/data_postgres_tst3/9.0/data/pg_log',
        regex='.*.csv',
        multiline=True,
        multiline_regex='^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
        reverse=True)

    add_server = AddFieldsFilter({'server' : socket.gethostname()})
    zmq_out = ZeroMQOutput(host='virtdev.cei.cox.com',port=8003)
    pipeline = Pipeline(pipes = [dw,add_server,zmq_out])

    for data in pipeline:
        pass
