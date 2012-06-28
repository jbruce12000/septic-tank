#!/usr/bin/env python    

from pysolr import *
conn = Solr('http://localhost:8080/solr/medley')
conn.delete(q='*:*')
#conn.delete(q='date_dt:[* TO NOW/DAY-2DAYS]')


#curl "http://localhost:8983/solr/update?commit=true" -H "Content-Type: text/xml" 
#   --data-binary "<delete><query>timestamp:[* TO NOW/DAY-30DAYS]</query></delete>

# you can do this in a browser too
#http://virtdev.cei.cox.com:8080/solr/medley/update?stream.body=%3Cdelete%3E%3Cquery%3Edate_dt:[*%20TO%20NOW-2DAYS]%3C/query%3E%3C/delete%3E&commit=true
