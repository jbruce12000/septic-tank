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

    zmq_in = ZeroMQInput(port=8003)
    p = RegexParser(use = ['pgbouncerlog'])
    rff = RemoveFieldsFilter(fields = ['msg'])
    # 2012-08-08 01:36:16.667
    zdf = ZuluDateFilter(fields=['date'],informat="%Y-%m-%d %H:%M:%S.%f")
    uniq = UniqFilter()
    solr_typemap = { 'date'        : '_dt',
                     'ip'          : '_ti',
                     'dbconnection' : '_s',
                     'database'    : '_s',
                     'user'        : '_s',
                     'server'      : '_ti',
                     'file'        : '_tp',
                     'port'        : '_l', }

    solr = SOLROutput('http://localhost:8080/solr/medley',
        commitrate=1000, typemap=solr_typemap )

    pipeline = Pipeline(pipes = [zmq_in,p,rff,zdf,uniq,solr])
    for data in pipeline:
        pass
