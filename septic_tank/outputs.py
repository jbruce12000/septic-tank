from pipeline import Pipe
from pysolr import Solr
import json
import logging
import sys
import zmq

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
        sys.stdout.flush()
        
        return data

class JSONOutput(Output):
    def __init__(self, **hints):
        self.hints = hints
        super(JSONOutput, self).__init__()

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        print json.dumps(data,**self.hints)
        sys.stdout.flush()
        return data

class ZeroMQOutput(Output):
    def __init__(self,host='127.0.0.1', port='8001'):
        super(ZeroMQOutput, self).__init__()
        self.host = host
        self.port = port
        self.addr = 'tcp://%s:%s' % (host,port)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.addr)
        self.poller = zmq.Poller()
        # zmq.POLLIN|zmq.POLLOUT
        self.poller.register(self.socket, zmq.POLLIN)
       
    def reconnect(self):
        logging.warn('%s reconnecting to %s' % (type(self),self.addr))
        self.socket.close()
        self.context.term()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.addr)
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
 
    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        msg = json.dumps(data,separators=(',',':'))
        try:
            self.socket.send(msg,zmq.NOBLOCK)
        except Exception,err:
            logging.error('zeromq socket send error: %s' % str(err))
            self.reconnect()
            return None

        # if the server disconnects, reconnect in one second
        socks = dict(self.poller.poll(1000))
        if socks:
            try:
                ignore = self.socket.recv()
                return data
            except Exception,err:
                logging.error('zeromq socket recv error: %s' % str(err))

        # if I get here something bad happened.  reconnect.
        self.reconnect()
        return None


class SOLROutput(Output):
    def __init__(self,solrurl,commitrate=10000):
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
        # FIX - this needs to be passed in because everyone's config will
        # be different
        for key in data:
            if 'date' in key:
                skey = "%s_dt" % key
            elif ('path' in key) or ('uri' in key) or ('url' in key):
                skey = "%s_tp" % key
            elif ('ip' in key) or ('host' in key):
                skey = "%s_ti" % key
            elif 'msg' == key:
                skey = key
            elif 'id' == key:
                skey = key
            else:
                skey = "%s_t" % key
            solrdata[skey] = data[key]
        self.solrcache.append(solrdata)
        self.commityet += 1

        # commit every once and a while
        if(self.commityet >= self.commitrate):
            logging.debug('adding %d docs to solr' % self.commityet)
            try:
                self.conn.add(self.solrcache)
                self.commityet = 0
                self.solrcache = []
            except Exception, err:
                # if solr is down, this fails at a rate of about 1/s until
                # solr comes back up.  the backlog in the cache then gets
                # written.
                logging.error('solr cache size: %d' % len(self.solrcache))
                logging.error('solr add error: %s' % str(err))
                return None 

        # required at end of pipeline
        return data
