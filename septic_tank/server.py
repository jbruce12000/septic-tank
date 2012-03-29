#!/usr/bin/env python
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver

class Answer(LineReceiver):
    def __init__(self):
        self.delimiter = '\n' 

    def lineReceived(self, line):
        print line
        #self.transport.write("%s\r\n" % line) 

    def connectionMade(self):
        peer = self.transport.getPeer()
        host = self.transport.getHost()
        print "connection from peer = %s, here = %s" % (peer,host)

# Next lines are magic:
factory = Factory()
factory.protocol = Answer

# 8007 is the port you want to run under. Choose something >1024
reactor.listenTCP(8007, factory)
reactor.listenTCP(8008, factory)
reactor.run()

