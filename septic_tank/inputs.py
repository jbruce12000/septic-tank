from pipeline import Pipe
import logging
import json
import re
import sys
import zmq

class Input(Pipe):
    pass

class ZeroMQInput(Input):
    '''
    can handle line based input, or line based input in json format
    host in this case is an interface.  used if you want zeromq to listen
    on a specific interface.
    '''
    def __init__(self,host='*', port='8001'):
        super(ZeroMQInput, self).__init__()
        self.host = host
        self.port = port
        self.addr = 'tcp://%s:%s' % (host,port)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.addr)

    def reconnect(self):
        logging.warn('%s reconnecting to %s' % (type(self),self.addr))
        self.socket.close()
        self.context.term()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(self.addr)

    def output(self):
        try:
            msg = self.socket.recv()
            logging.debug('zeromq msg received: %s' % msg)
            # must send something to make zeromq happy
            self.socket.send('k')
            msg = self.from_json(msg)
            return msg
        except Exception, err:
            logging.error('zeromq error: %s' % str(err))
            self.reconnect()
            return None

    def from_json(self,msg):
        '''
        convert msg from json if possible, or return msg
        '''
        try:
            msg = json.loads(msg)
        except: 
            pass
        return msg


class MultilineFileInput(Input):
    '''
    read a file line by line, combine lines that look like tracebacks

    inputs

        reverse = boolen, default False, reverses the regular expression 
            similar to grep -v
             
    '''
    def __init__(self,filename=sys.stdin,multiline_regex='^(\s+|Traceback|ValueError|UnboundLocalError|IntegrityError)', reverse=False):
        super(MultilineFileInput, self).__init__()
        self.file = filename
        self.multiline_regex = re.compile(multiline_regex)
        self.multiline_cache = ''
        self.reverse = reverse
        if isinstance(self.file,file):
            self.f = self.file
        else:
            self.f = open(self.file, 'rb')

    def get_combined_line(self):
        if not self.multiline_cache:
            self.prime_cache()

        while True:
            line = self.get_single_line()
            if self.dead:
                # FIX - this is not returning the last record.
                return self.combined(line)        
            # if it looks like a traceback, combine it with what we have
            if self.reverse:
                if self.multiline_regex.search(line):
                    return self.combined(line)
                else:
                    self.multiline_cache = '%s%s' % (self.multiline_cache,line)
            else:
                if self.multiline_regex.search(line):
                    self.multiline_cache = '%s%s' % (self.multiline_cache,line)
                else:
                    return self.combined(line)

    def combined(self,line=''):
        combined = ''.join(self.multiline_cache)
        self.multiline_cache = line
        return combined

    def prime_cache(self):
        while True: 
            # get a line that does not look like a traceback
            line = self.get_single_line()
            if self.dead:
                return
            # we are dropping content here, because we have nothing to
            # tie it to.  we have started reading in the middle of a 
            # traceback.
            if self.reverse:
                if self.multiline_regex.search(line):
                    self.multiline_cache = "%s%s" % (self.multiline_cache,line)
                    return
                continue
            else:
                if self.multiline_regex.search(line):
                    continue
                self.multiline_cache = "%s%s" % (self.multiline_cache,line)
                return

    def get_single_line(self):
        line = self.f.readline()
        if line == '':
            self.dead = True
        return line

    def output(self):
        if self.f:
            return self.get_combined_line()
        return None
 

class FileInput(Input):
    '''
    read a file as input line by line
    '''
    def __init__(self,filename=sys.stdin):
        super(FileInput, self).__init__()
        self.file = filename
        if isinstance(self.file,file):
            self.f = self.file
        else:
            self.f = open(self.file, 'rb')

    def output(self):
        if self.f:
            line = self.f.readline()
            if line == '':
                self.dead = True
            return line
        return None

class StdInput(FileInput):
    pass
