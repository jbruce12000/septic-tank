from pipeline import Pipe
from pysolr import Solr
import json
import logging

class Output(Pipe):
    def data_invalid(self,data):
        if 'type' not in data:
            return True
        if len(data.keys()) < 2:
            return True
        return False

class STDOutput(Output):
    '''
    output that prints data to stdout
    '''
    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        print data
        return data

class JSONOutput(Output):
    def __init__(self, **hints):
        self.hints = hints

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        print json.dumps(data,**self.hints)
        return data

class SOLROutput(Output):
    def __init__(self,solrurl,commitrate=1000):
        super(SOLROutput, self).__init__()
        self.solrurl = solrurl
        self.conn = Solr(self.solrurl)
        self.commitrate = commitrate
        self.solrcache = []
        self.commityet = 0

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        if self.data_invalid(data):
            logging.debug('data is invalid %s' % data)
            return None

        solrdata = {}
        for key in data:
            if 'date' in key:
                skey = "%s_dt" % key
            else:
                skey = "%s_t" % key
            solrdata[skey] = data[key]
        self.solrcache.append(solrdata)
        self.commityet += 1

        # commit every once and a while
        if(self.commityet >= self.commitrate):
            logging.debug('adding %d docs to solr: %s' % (self.commityet,self.solrcache))
            self.conn.add(self.solrcache)
            self.commityet = 0
            self.solrcache = []

        # required at end of pipeline
        return data
