#!/usr/bin/env python
import logging
import socket
from pipeline import Pipeline
from inputs import FileInput, ZeroMQInput, StdInput
from parsers import RegexParser 
from filters import ZuluDateFilter, RemoveFieldsFilter, GrepFilter, LCFilter, UniqFilter, AddFieldsFilter
from outputs import *
from dirwatcher import DirWatcher

logging.basicConfig(filename='./debug.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == "__main__":

    stdin = StdInput()
    p = RegexParser(use = ['apachelog']) 
    gf = GrepFilter(fields=['uri'],regex='health_check_status', reverse=True)
    rff = RemoveFieldsFilter(fields = ['msg'])
    zdf = ZuluDateFilter(fields=['date'],informat="%d/%b/%Y:%H:%M:%S")
    uniq = UniqFilter()
    solr_typemap = { 'date'        : '_dt',
                     'hostname'    : '_ip',
                     'client_ip'   : '_ip',
                     'uri'         : '_tp',
                     'server'      : '_s',
                     'file'        : '_tp',
                     'serve_time'  : '_l', }

#    solr_typemap = { 'date'        : '_dt',
#                     'hostname'    : '_ti',
#                     'client_ip'   : '_ti',
#                     'uri'         : '_tp',
#                     'server'      : '_s',
#                     'file'        : '_tp',

#    solr = SOLROutput('http://localhost:8983/solr/collection1',
#        commitrate=1000, typemap=solr_typemap )

    sqlite = SQLiteOutput(commitrate=10000)
    pipeline = Pipeline(pipes = [stdin,p,gf,rff,zdf,uniq,sqlite])
    for data in pipeline:
        pass 
