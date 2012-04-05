#!/usr/bin/env python
import logging
import socket
from pipeline import Pipeline
from inputs import FileInput, ZeroMQInput, StdInput
from parsers import RegexParser 
from filters import ZuluDateFilter, RemoveFieldsFilter, GrepFilter, LCFilter, UniqFilter, AddFieldsFilter
from outputs import STDOutput, JSONOutput, SOLROutput, ZeroMQOutput
from dirwatcher import DirWatcher

logging.basicConfig(filename='./debug.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

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
    p = RegexParser(use = ['apachelog']) 
    # 29/Mar/2012:02:06:49 -0400
    zdf = ZuluDateFilter(fields=['apache_date'],informat="%d/%b/%Y:%H:%M:%S")

    dw = DirWatcher(folder="/home/jbruce/septic_tank/septic_tank/logs") 

    rff = RemoveFieldsFilter(fields = ['msg'])
    add_server = AddFieldsFilter({'server' : socket.gethostname()})
    gf = GrepFilter(regex='459184')
    lcf = LCFilter()
    uniq = UniqFilter()
    stdout = STDOutput()
    jsout = JSONOutput(sort_keys=True, indent=2)
    solr = SOLROutput('http://localhost:8080/solr/medley')
    zmq_out = ZeroMQOutput()
    zmq_in = ZeroMQInput()

    # fix there is a bug in jsout for the all.access.log
    #pipeline = Pipeline(pipes = [i,p,lcf,zdf,uniq,stdout])
    pipeline = Pipeline(pipes = [dw,p,rff,add_server,lcf,zdf,uniq,jsout])
    #pipeline = Pipeline(pipes = [dw,stdout])
    for data in pipeline:
        pass 
    

    # need a director which makes flow decisions based on dict contents
    # need a way to split flow to two outputs
    # need augmentor to add content to the flow based on record type
      # may need environment, hostname augmented
    # need filters to remove unwanted content
    # need filters to modify input like lc, normalize, lt white
    # need outputs like sqlite, file (json), solr

    # to clean out SOLR
    # >>> from pysolr import *
    # >>> conn = Solr('http://localhost:8080/solr/medley')
    # >>> conn.delete(q='*:*')

    # status:1 in solrconfig.xml is causing no recs to be returned
    # solr wants dates like this... 2010-11-03T15:51:27.928Z
    # faceting works by adding &facet=true&facet.field=user_t&facet.field=team_t&facet.field=type_t
