from pipeline import Pipe
from pysolr import Solr
import json
import logging
import sys
import time
import zmq
import sqlite3 as lite
from collections import defaultdict

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
    def __init__(self,host='127.0.0.1', port='8001', zmq_socket_type=zmq.REQ):
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

class ZeroMQParentParallelOutput(Output):
    '''
    An output used to load balance records across multiple processes.
    This is used by the parent process to get data to the children in
    load balanced fashion.
    '''
    def __init__(self, host='*', port=6666):
        super(ZeroMQParentParallelOutput, self).__init__()
        self.host = host
        self.port = port
        self.addr = 'tcp://%s:%s' % (host,port)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.bind(self.addr)

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        msg = json.dumps(data,separators=(',',':'))
        try:
            self.socket.send(msg)
        except Exception,err:
            logging.error('zeromq socket send error: %s' % str(err))
            return None
        return data

class ZeroMQChildParallelOutput(Output):
    '''
    An output used to return data from multiple parallel processes to 
    the parent.
    '''
    def __init__(self, host='127.0.0.1', port=6667):
        super(ZeroMQChildParallelOutput, self).__init__()
        self.host = host
        self.port = port
        self.addr = 'tcp://%s:%s' % (host,port)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.connect(self.addr)

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        msg = json.dumps(data,separators=(',',':'))
        try:
            self.socket.send(msg)
        except Exception,err:
            logging.error('zeromq socket send error: %s' % str(err))
            return None
        return data



class SOLROutput(Output):
    def __init__(self,solrurl,commitrate=10000,typemap={}):
        super(SOLROutput, self).__init__()
        self.solrurl = solrurl
        self.conn = Solr(self.solrurl)
        self.commitrate = commitrate
        self.solrcache = []
        self.commityet = 0
        self.typemap = typemap
        # post 0 docs to solr:
        # 1. verify we can post to solr
        # 2. load libs for __del__
        self.commit_to_solr()

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        if self.data_invalid(data):
            logging.debug('data is invalid %s' % data)
            return None

        solrdata = {}
        for key in data:
            if key in self.typemap:
                skey = "%s%s" % (key,self.typemap[key])
            elif key == 'id':
                skey = key
            elif key == 'msg':
                skey = key
            else:
                skey = "%s_t" % key
            solrdata[skey] = data[key]
        self.solrcache.append(solrdata)
        self.commityet += 1

        # commit every once and a while
        if(self.commityet >= self.commitrate):
            self.commit_to_solr()

        # required at end of pipeline
        return data

    def commit_to_solr(self):
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
            time.sleep(1);
            return None 

    def __del__(self):
        self.commitrate = 0
        logging.debug('shutting down, clearing cache to solr')
        self.commit_to_solr()

class SQLiteOutput(Output):

    # FIX - needs to handle uniq id as docid???

    def __init__(self,path="ft.db",commitrate=10000):
        super(SQLiteOutput, self).__init__()
        self.path = path
        self.commitrate = commitrate
        self.sqlitecache = defaultdict(list)
        self.commityet = 0
        self.tables = {};

    def create_table_sql_for(self,data):
        columns=",".join(data.keys())
        #return "create virtual table %s using fts4(%s)" % (data['type'],columns)
        return "create table if not exists %s (%s)" % (data['type'],columns)

    def create_insert_sql_for(self,data):
        columns = sorted(data.keys())
        return "insert into %s (%s) values (%s)" % (data['type'],','.join(columns),','.join("?" for x in columns))

    def create_insert_tuple_for(self,data):
        values = []
        for key in sorted(data.iterkeys()):
            if data[key]:
                values.append(unicode(data[key], errors='ignore'))
            else:
                values.append(unicode("", errors='ignore'))
        return values

    def execute(self,data):
        logging.debug('%s execute with data %s' % (type(self),data))
        if self.data_invalid(data):
            logging.debug('data is invalid %s' % data)
            return None

        # create table sql
        if data['type'] not in self.tables:
            self.tables['type']=self.create_table_sql_for(data)
         
        # this is a defaultdict like this...
        # "insert into table (col1,col2) values (?,?)" => [(1,2),(3,4)]
        sql = self.create_insert_sql_for(data)
        self.sqlitecache[sql].append(self.create_insert_tuple_for(data))
        self.commityet += 1

        # commit every once and a while
        if(self.commityet >= self.commitrate):
            self.commit_to_sqlite()

        # required at end of pipeline
        return data

    def create_tables(self):
        for sql in self.tables.values():
            cur = self.conn.cursor()
            try:
                cur.execute(sql)
            except lite.OperationalError:
                continue

    # FIX - should this fail forever?  if there is just a single column
    # added to the data, it will cause this to fail.   
    def commit_to_sqlite(self):
        self.conn = lite.connect(self.path)
        self.create_tables()
        self.conn.commit()
        #logging.error(self.sqlitecache)
        #sys.exit()
        #import pdb; pdb.set_trace()
        try:
            cur = self.conn.cursor()
            for sql in self.sqlitecache:
                cur.executemany(sql,self.sqlitecache[sql])    
            self.conn.commit()
            self.conn.close()
            self.tables = {}
            self.sqlitecache = defaultdict(list)
            logging.debug('committed %s recs to sqlite' % self.commityet)
            self.commityet = 0
        except Exception, e:
            # yes, except everything.
            logging.error('error committing to SQLite %s' % e)
            logging.error(self.sqlitecache)
    
    def __del__(self):
        logging.debug('shutting down, clearing cache to sqlite')
        self.commit_to_sqlite()
