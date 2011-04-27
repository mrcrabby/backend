import mylog
import pymongo
import random
import sys
import time
import tracker
import zmq

from zmq.eventloop import ioloop, zmqstream
from zmq.utils.jsonapi import dumps, loads

class Worker:
    """ 	                

     	                         pull from tracker
		                         |
		                      ___| ___
             			     |        |
      req router 9999 (rtr_sock)-----| worker |--- broker 4444 (brk_sock) 
		                     |________|
		                         |
		                         |
		                push to proxy/stream server

    """

    def __init__(self):
        self.logger = mylog.logstart('worker_log')

        self.ctx = zmq.Context.instance()
        self.loop = ioloop.IOLoop.instance()
        
        brk_sock = self.ctx.socket(zmq.REQ)
        brk_sock.connect('tcp://127.0.0.1:4444')
        self.brk = zmqstream.ZMQStream(brk_sock, self.loop)
        self.brk.on_recv(self.brokerRecv)
        self.brk.on_send(self.brokerSend)

        rtr_sock = self.ctx.socket(zmq.REQ)
        rtr_sock.setsockopt(zmq.IDENTITY, sys.argv[1])
        rtr_sock.connect('tcp://127.0.0.1:9999')
        self.rtr = zmqstream.ZMQStream(rtr_sock, self.loop)
        self.rtr.on_recv(self.routerRecv)
        self.rtr.on_send(self.routerSend)
        self.rtr.send('ready')
        self.loop.start()

    def routerSend(self, *args):
        #self.logger.debug('sent to router: %s' % str(args))
        pass 

    def routerRecv(self, message):
        """
        request = {'timestamp': timestamp, 
                   'task': 'detection'/'recognition'/'tracking',
                   'parameters': (...)}
        """
        request = loads(message[-2])
        
        if request['task'] == 'detection':
            self.logger.debug('start detection')
            with open('image.jpg', 'wb') as f:
                f.write(message[-1])
            sleep = random.randint(1, 10)
            time.sleep(sleep)
            message = message[:-1]
            message[-1] = dumps('detection')
            self.rtr.send_multipart(message)
        
        elif request['task'] == 'tracking':
            self.logger.debug('prepare to tracking')
            tracker.Tracker(self.rtr, message)

    def brokerSend(self):
        pass

    def brokerRecv(self):
        pass

    def register(self, address, speed):
	message = dumps(('register', address, speed))
	print message
	self.brk.send_multipart(message)
    
    def unregister(self, address):
	message = dumps(('unregister', address, '0'))
	print message
	self.brk.send_multipart(message)

    def proxing(self):
        pass

    def detection(self):
        pass

    def blur(self):
        pass

    def test(self):
        pass

if __name__ == '__main__':
    worker = Worker()
