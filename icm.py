from twisted.internet import reactor, protocol, task
from twisted.protocols.basic import LineReceiver

import time
import mylog

class ICMtoBroker(LineReceiver):
    
    def connectionMade(self):
        logger.debug('connection with broker established')
        self.transport.write("Hello Broker\r\n")

    def lineReceived(self, data):
        port = data.strip()
        logger.debug(port)
        newConnection('127.0.0.1', int(port), ICMtoTracker)        
        self.transport.write("Goodbye Broker\r\n")

    def connectionLost(self, *args):
        logger.debug(args)
        logger.debug('connection lost')

class ICMtoTracker(LineReceiver):
    
    def connectionMade(self):
        logger.debug('connection with tracker established')
        self.timestamp = (i for i in xrange(1000))
        t = task.LoopingCall(self.photoReceived)
        t.start(1)
    
    def photoReceived(self):
        try:
            photo='%s\r\n' % str(self.timestamp.next())    
            logger.debug('send photo to tracker %s ' % photo)
            self.transport.write(photo)
        except:
            self.transport.loseConnection()

    def lineReceived(self, data):
        logger.debug(data)

    def connectionLost(self, *args):
        logger.debug('connection lost')

class ICMFactory(protocol.ClientFactory):
    protocol = ICMtoBroker

def newConnection(addr, port, protocol):
    factory = ICMFactory()
    factory.protocol = protocol
    reactor.connectTCP(addr, port, factory)

logger = mylog.logstart('icm_camera')
newConnection('127.0.0.1', 3333, ICMtoBroker)
reactor.run()
