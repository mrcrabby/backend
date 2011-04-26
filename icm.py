from twisted.internet import reactor, protocol, task

import time


class ICMtoBroker(protocol.Protocol):
    
    def connectionMade(self):
        self.transport.write("Hello")

    def dataReceived(self, data):
        print data
        time.sleep(1)
        self.transport.write("Hello from ICM")
        #self.transport.loseConnection()

    def connectionLost(self, *args):
        print 'connection lost'


class ICMFactory(protocol.ClientFactory):
    protocol = ICMtoBroker



reactor.connectTCP('127.0.0.1', 3333, ICMFactory())
reactor.run()
