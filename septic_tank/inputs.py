from pipeline import Pipe
import logging

class Input(Pipe):
    pass

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

