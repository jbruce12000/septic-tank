from pipeline import Pipe
import logging
import json
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

class FileInput(Input):
    '''
    read a file as input line by line
    '''
    def __init__(self,file):
        super(FileInput, self).__init__()
        self.file = file
        self.f = open(self.file, 'rb')

    def output(self):
        if self.f:
            line = self.f.readline()
            if line == '':
                self.dead = True
            return line
        return None

