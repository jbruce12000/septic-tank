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

    fieldnames = [
        'date',
        'user',
        'db_name',
        'pid',
        'connection_from',
        'session_id',
        'session_line_num',
        'command_tag',
        'session_start_time',
        'virtual_transaction_id',
        'transaction_id',
        'level',
        'sql_state_code',
        'message',
        'detail',
        'hint',
        'internal_query',
        'internal_query_pos',
        'context',
        'query',
        'query_pos',
        'location',
        'app_name', ]

    zmq_in = ZeroMQInput(port=8003)

    p = CSVParser(fieldnames=fieldnames, record_type='postgres',
                  quotechar='"', delimiter=',')
                 
    lcf = LCFilter()
    rff = RemoveFieldsFilter(fields = ['msg'])
    zdf = ZuluDateFilter(fields=['date'],informat="%Y-%m-%d %H:%M:%S.%f %Z")
    uniq = UniqFilter()
    solr_typemap = { 'date'        : '_dt',
                     'hostname'    : '_ti',
                     'ip'          : '_ti',
                     'module'      : '_ti',
                     'client_ip'   : '_ti',
                     'uri'         : '_tp',
                     'server'      : '_ti',
                     'file'        : '_tp', }
    solr = SOLROutput('http://localhost:8080/solr/medley',
        typemap=solr_typemap,
        commitrate=100)

    pipeline = Pipeline(pipes = [zmq_in,p,lcf,rff,zdf,uniq,solr])
 
    for data in pipeline:
        pass 
