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

    zmq_in = ZeroMQInput()
    p = RegexParser(use = ['apachelog']) 
    gf = GrepFilter(fields=['uri'],regex='health_check_status', reverse=True)
    rff = RemoveFieldsFilter(fields = ['msg'])
    zdf = ZuluDateFilter(fields=['date'],informat="%d/%b/%Y:%H:%M:%S")
    uniq = UniqFilter()
    solr_typemap = { 'date'        : '_dt',
                     'hostname'    : '_ti',
                     'client_ip'   : '_ti',
                     'uri'         : '_tp',
                     'server'      : '_s',
                     'file'        : '_tp',
                     'serve_time'  : '_l', }

    solr = SOLROutput('http://localhost:8080/solr/medley',
        commitrate=1000, typemap=solr_typemap )

    pipeline = Pipeline(pipes = [zmq_in,p,gf,rff,zdf,uniq,solr])
    for data in pipeline:
        pass 
