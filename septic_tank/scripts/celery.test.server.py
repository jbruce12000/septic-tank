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

    # get data to flow through objects, kinda like unix pipes
    #i = FileInput('all.txt')
    #p = RegexParser(use = ['irclog']) 
    #zdf = ZuluDateFilter(fields=['date'],informat="%Y-%m-%d %H:%M")

    #i = FileInput('solr.txt')
    #p = RegexParser(use = ['solrlog','solradd']) 
    #zdf = ZuluDateFilter(fields=['date'])

    #stdin = StdInput()
    #i = FileInput('all.access.log')
    p = RegexParser(use = ['celerylog']) 
    zdf = ZuluDateFilter(fields=['date'],iszulu=True)
    rff = RemoveFieldsFilter(fields = ['msg'])
    lcf = LCFilter()
    uniq = UniqFilter()
    stdout = STDOutput()
    jsout = JSONOutput(sort_keys=True, indent=2)
    solr_typemap = { 'date'        : '_dt',
                     'server'      : '_s',
                     'file'        : '_tp',
                     'celery_task' : '_ti' }

    solr = SOLROutput('http://localhost:8080/solr/medley',
        commitrate=1000,
        typemap=solr_typemap,)
    #zmq_out = ZeroMQOutput()
    zmq_in = ZeroMQInput(port=8002)

    # fix there is a bug in jsout for the all.access.log
    #pipeline = Pipeline(pipes = [i,p,lcf,zdf,uniq,stdout])
    pipeline = Pipeline(pipes = [zmq_in,p,rff,lcf,zdf,uniq,solr])
    #pipeline = Pipeline(pipes = [dw,stdout])
    for data in pipeline:
        pass 
