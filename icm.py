from twisted.internet import reactor, protocol, task
from twisted.protocols.basic import LineReceiver

import time


class ICMtoBroker(LineReceiver):
    
    def connectionMade(self):
        self.transport.write("Hello Broker\n")

    def lineReceived(self, data):
        print data
        newConnection('127.0.0.1', 11111, ICMtoTracker)        
        self.transport.write("Goodbye Broker\n")

    def connectionLost(self, *args):
        print args
        print 'connection lost'

class ICMtoTracker(LineReceiver):
    
    def connectionMade(self):
        self.transport.write("Hello Tracker")

    def lineReceived(self, data):
        print data

    def connectionLost(self, *args):
        print 'connection lost'

class ICMFactory(protocol.ClientFactory):
    protocol = ICMtoBroker

def newConnection(addr, port, protocol):
    factory = ICMFactory()
    factory.protocol = protocol
    reactor.connectTCP(addr, port, factory)

newConnection('127.0.0.1', 3333, ICMtoBroker)
reactor.run()
