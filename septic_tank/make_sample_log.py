#!/usr/bin/env python
import datetime
from random import randint

class SampleLog(object):
    '''
    creates a sample log file for parsing
    
    '''
    def __init__(self):
        self.levels = ['DEBUG', 'ERROR', 'INFO', 'WARN']
        self.users = ['fred', 'bill', 'bob', 'msimpson', 'jbruce']
        self.ips = ['10.0.0.1', '10.0.0.2', '192.168.1.35', '127.0.0.1']
        self.words = ['this','is','a','sample','log','file','generator']
        self.date = datetime.datetime.now()
        self.delta = datetime.timedelta(minutes=0,seconds=3)

    def __iter__(self):
        return self

    def randlst(self,lst):
        return lst[randint(0, len(lst) - 1)]

    def sentence(self,length=10):
        sentence = [self.randlst(self.words) for _ in range(1, length)]
        return ' '.join(sentence)

    def next(self):
        self.date = self.date + self.delta
        return '%s - %s, "%s" - %s: %s' % (self.date, self.randlst(self.levels),self.randlst(self.users), self.randlst(self.ips), self.sentence())

if __name__ == "__main__":
    log = SampleLog()
    for line in log:
        print line
        
