import logging

class Pipeline(object):
    '''
    '''
    def __init__(self,pipes=[]):
        self.pipes = pipes
        self.dead = False

    def __iter__(self):
        return self

    def _execute(self):
        for x in range(1,len(self.pipes)):
            a = self.pipes[x-1]
            b = self.pipes[x]
            logging.debug('execute %d %s | %s' % (x,type(a),type(b)))

            # somewhere in the middle of the pipeline
            output = a.output()
            if output:
                b.pipe_cache.append(b.execute(output))
            else:
                b.pipe_cache.append(None)

            # if the input is dead, so is the pipeline
            # FIX - this needs to flush the output
            if a.dead:
                self.dead = True
                return None

            # if any pipe in the pipeline returns None, there should be
            # no output, clean up the entire pipeline so we can try again.
            if b.is_empty():
                self.clean()
                return None

            # done, return what we got from the last pipe
            if x == len(self.pipes) - 1:
                logging.debug('end of pipe %s' % type(b))
                return b.output()

        self.clean()
        return None

    def next(self):
        if len(self.pipes) <= 1:
            raise StopIteration, "a pipeline must contain at least two pipes"
        while(True):
            output = self._execute()
            if self.dead:
                raise StopIteration
            if output:
                logging.debug('execute breaks to return %s' % output)
                break
        return output

    def clean(self):
        for pipe in self.pipes:
            pipe.pipe_cache = []


class ParallelPipeline(Pipeline):
    '''
    A pipeline that runs as many parallel processes.  It uses a hidden
    zeromq input and output.  A parallel pipeline is useful for parsing
    and reformatting on a multi-processor machine.
    '''    
    # fix - need to find a way for ports to be chosen automatically.  zeromq
    # does not support this.  Maybe bind to port O, grab the port number,
    # shut down the socket, and give it to zeromq.


    # from the parent process, this pipeline should appear to be just an
    # zmqoutput and an zmqinput. from the point of view of the children,
    # it should be the pipeline grabbing data from a socket and sending it
    # to a socket.

    def __init__(self,pipes=[],maxprocs=2,output_port=5557,input_port=5558):
        self.pipes = pipes
        self.maxprocs = maxprocs
        self.procs = []
        self.output_port = output_port
        self.input_port = input_port
        # need to create the ZMQ start and end of this pipeline
        # the start and end would be part of the parent process
        # the children would be the pipeline in between
        self.zmqout = ZeroMQParallelOutput()
        self.zmqin = ZeroMQParallelInput()
        super(ParallelPipeline, self).__init__(pipes=pipes)
        self.create_parallel_processes()

    def create_parallel_processes(self):
        from multiprocessing import Process
        for x in range(self.maxprocs):
            self.procs[x] = Process(target=self.next)
            self.procs[x].start()
            self.procs[x].join()

    def next(self):
        # parent process should not be able to run next
        # need to verify this is not the parent
        pass

    def _execute(self):
        '''
        The parallel pipeline has a special _execute because it must
        grab data from a zeromq socket, do all the normal pipeline processing
        and then send it to a zeromq socket.
        '''

        # establish output and input ports
        if not self.context:
            self.context = zmq.Context()
        if not self.receiver:
            self.receiver = self.context.socket(zmq.PULL)
            self.receiver.connect("tcp://127.0.0.1:%s" % self.output_port)
        if not self.sender:
            self.sender = self.context.socket(zmq.PUSH)
            self.sender.connect("tcp://127.0.0.1:%s" % self.input_port)

        # grab data from output
        # somehow have to merry up the data with the pipe. 
 
        for x in range(1,len(self.pipes)):
            a = self.pipes[x-1]
            b = self.pipes[x]
            logging.debug('execute %d %s | %s' % (x,type(a),type(b)))

            # somewhere in the middle of the pipeline
            output = a.output()
            if output:
                b.pipe_cache.append(b.execute(output))
            else:
                b.pipe_cache.append(None)

            # if the input is dead, so is the pipeline
            # FIX - this needs to flush the output
            if a.dead:
                self.dead = True
                return None

            # if any pipe in the pipeline returns None, there should be
            # no output, clean up the entire pipeline so we can try again.
            if b.is_empty():
                self.clean()
                return None

            # done, return what we got from the last pipe
            if x == len(self.pipes) - 1:
                logging.debug('end of pipe %s' % type(b))
                return b.output()

        self.clean()
        return None

    


class Pipe(object):
    def __init__(self,name=''):
        self.pipe_cache = []
        self.dead = False
        self.name = name

    def __unicode__():
        return self.name

    def is_empty(self):
        if len(self.pipe_cache) == 0:
            return True
        for item in self.pipe_cache:
            if item:
                return False
        return True

    def output(self):
        if self.pipe_cache:
            return self.pipe_cache.pop(0)
        return None

    # fix = this should be an iterator. powered by a generator?
    def execute(self,data):
        '''
        default behavior is to pass data through.
        children are expected to override 
        '''
        # fix self.name wont always be set
        logging.debug('%s execute with data %s' % (self.name,data))
        return data

