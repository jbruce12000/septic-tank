import logging
import os

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
    def is_parent(self):
        if os.getpid() == self.parentpid:
            return True
        return False

    def __init__(self,pipes=[],maxprocs=2,output_port=6666,input_port=6667):
        from outputs import ZeroMQParentParallelOutput
        from inputs import ZeroMQParentParallelInput

        self.parentpid = os.getpid()
        self.pipes = pipes
        self.parent_input = self.pipes.pop(0)
       
        self.maxprocs = maxprocs
        self.procs = []

        # fix - not yet used
        self.output_port = output_port
        self.input_port = input_port

        super(ParallelPipeline, self).__init__(pipes=pipes)
        self.create_parallel_processes()

        # the pipeline looks different depending on whether this is parent
        # or one of the potential many children.  The parent sees only
        # an output to the children.
        # The children receive the data from the parent and process the 
        # pipeline
        if self.is_parent():
            self.parentzmqout = ZeroMQParentParallelOutput()
            self.pipes = [ self.parent_input, self.parentzmqout ]

    def create_parallel_processes(self):
        '''
        create the children
        '''
        from multiprocessing import Process
        for x in range(self.maxprocs):
            self.procs.append(Process(target=self.loop_forever))
            self.procs[x].start()

    def loop_forever(self):
        from outputs import ZeroMQChildParallelOutput
        from inputs import ZeroMQChildParallelInput
        self.childzmqin = ZeroMQChildParallelInput()
        self.pipes.insert(0,self.childzmqin)

        while(True):
            self.next();

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
        logging.debug('%s execute with data %s' % (type(self),data))
        return data

