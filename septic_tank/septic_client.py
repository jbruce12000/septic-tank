#!/usr/bin/env python
import logging
from pipeline import Pipeline
from inputs import FileInput, ZeroMQInput
from parsers import RegexParser
from filters import ZuluDateFilter, RemoveFieldsFilter, GrepFilter, LCFilter, UniqFilter
from outputs import STDOutput, JSONOutput, SOLROutput, ZeroMQOutput

logging.basicConfig(filename='./debug.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == "__main__":
    i = FileInput('all.access.log')
    rg = GrepFilter(regex='health_check_status', reverse=True)
    p = RegexParser(use = ['apachelog'])
    zmq_out = ZeroMQOutput()

    pipeline = Pipeline(pipes = [i,rg,zmq_out])
    for data in pipeline:
        pass
