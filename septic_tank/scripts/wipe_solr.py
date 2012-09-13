#!/usr/bin/env python    

from pysolr import *
conn = Solr('http://localhost:8080/solr/medley')
conn.delete(q='*:*')
#conn.delete(q='date_dt:[* TO NOW/DAY-2DAYS]')


#curl "http://localhost:8983/solr/update?commit=true" -H "Content-Type: text/xml" 
#   --data-binary "<delete><query>timestamp:[* TO NOW/DAY-30DAYS]</query></delete>

# you can do this in a browser too
#http://virtdev.cei.cox.com:8080/solr/medley/update?stream.body=%3Cdelete%3E%3Cquery%3Edate_dt:[*%20TO%20NOW-2DAYS]%3C/query%3E%3C/delete%3E&commit=true


#http://slrjboprd5.ddtc.cmgdigital.com:8080/solr/medley/update?stream.body=<delete><query>id:photos.medleygallery.86894</query></delete>&commit=true


#http://slrjboprd5.ddtc.cmgdigital.com:8080/solr/medley/select/?q=id%3Aphotos.medleygallery.86894&version=2.2&start=0&rows=10&indent=on
#http://slrjboprd4.ddtc.cmgdigital.com:8080/solr/medley/select/?q=id%3Aphotos.medleygallery.86894&version=2.2&start=0&rows=10&indent=on
#http://slrjboprd3.ddtc.cmgdigital.com:8080/solr/medley/select/?q=id%3Aphotos.medleygallery.86894&version=2.2&start=0&rows=10&indent=on
