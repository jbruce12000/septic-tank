#!/usr/bin/env python    

from pysolr import *
conn = Solr('http://localhost:8080/solr/medley')
#conn.delete(q='*:*')
conn.delete(q='date_dt:[* TO NOW/DAY-2DAYS]')


#curl "http://localhost:8983/solr/update?commit=true" -H "Content-Type: text/xml" 
#   --data-binary "<delete><query>timestamp:[* TO NOW/DAY-30DAYS]</query></delete>
