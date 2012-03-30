#!/usr/bin/env python
import logging
from pipeline import Pipeline
from inputs import FileInput
from parsers import RegexParser 
from filters import ZuluDateFilter, RemoveFieldsFilter, GrepFilter, LCFilter, UniqFilter
from outputs import STDOutput, JSONOutput, SOLROutput

logging.basicConfig(filename='./debug.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == "__main__":

    # get data to flow through objects, kinda like unix pipes
    #i = FileInput('all.txt')
    #p = RegexParser(use = ['irclog']) 
    #zdf = ZuluDateFilter(fields=['date'],informat="%Y-%m-%d %H:%M")

    #i = FileInput('solr.txt')
    #p = RegexParser(use = ['solrlog','solradd']) 
    #zdf = ZuluDateFilter(fields=['date'])

    i = FileInput('all.access.log')
    p = RegexParser(use = ['apachelog']) 
    zdf = ZuluDateFilter(fields=['date'])


    rff = RemoveFieldsFilter(fields = ['ip'])
    gf = GrepFilter(regex='459184')
    lcf = LCFilter()
    uniq = UniqFilter()
    stdout = STDOutput()
    jsout = JSONOutput(sort_keys=True, indent=2)
    solr = SOLROutput('http://localhost:8080/solr/medley')

    # fix there is a bug in jsout for the all.access.log
    pipeline = Pipeline(pipes = [i,p,uniq,jsout])
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
