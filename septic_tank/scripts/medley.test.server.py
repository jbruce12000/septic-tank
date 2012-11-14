#!/usr/bin/env python
import logging
import socket
from pipeline import Pipeline
from inputs import FileInput, ZeroMQInput, StdInput
from parsers import RegexParser
from filters import ZuluDateFilter, RemoveFieldsFilter, GrepFilter, LCFilter, UniqFilter, AddFieldsFilter
from outputs import *
from dirwatcher import DirWatcher

logging.basicConfig(filename='./debug.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == "__main__":

    i = FileInput('/home/jbruce/septic_tank/septic_tank/logs/archives/all.medleypid.log')
    p = RegexParser(use = ['medleypidlog'])
    rff = RemoveFieldsFilter(fields = ['msg'])
    zdf = ZuluDateFilter(fields=['date'],iszulu=True)
    uniq = UniqFilter()
    sqlite = SQLiteOutput(commitrate=10000)

    pipeline = Pipeline(pipes = [i,p,rff,zdf,uniq,sqlite])
    for data in pipeline:
        pass

