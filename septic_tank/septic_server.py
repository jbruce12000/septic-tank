#!/usr/bin/env python
import logging
from pipeline import Pipeline
from inputs import FileInput, ZeroMQInput
from parsers import RegexParser
from filters import ZuluDateFilter, RemoveFieldsFilter, GrepFilter, LCFilter, UniqFilter
from outputs import STDOutput, JSONOutput, SOLROutput, ZeroMQOutput
import time

logging.basicConfig(filename='./debug.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == "__main__":
    zmq_in = ZeroMQInput()
    p = RegexParser(use = ['apachelog'])
    zdf = ZuluDateFilter(fields=['apache_date'],informat="%d/%b/%Y:%H:%M:%S")
    lcf = LCFilter()
    uniq = UniqFilter()
    stdout = STDOutput()

    pipeline = Pipeline(pipes = [zmq_in,p,lcf,zdf,uniq,stdout])
    for data in pipeline:
        pass
