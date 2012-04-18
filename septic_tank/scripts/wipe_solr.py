#!/usr/bin/env python    

from pysolr import *
conn = Solr('http://localhost:8080/solr/medley')
conn.delete(q='*:*')
