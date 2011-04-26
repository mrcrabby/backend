import logging
logger = logging.getLogger('worker_log')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formater = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
handler.setFormatter(formater)
logger.addHandler(handler)

import pymongo
import random
import sys
import time
import zmq

from zmq.eventloop import ioloop, zmqstream
loop = ioloop.IOLoop.instance()

from zmq.utils.jsonapi import dumps, loads

class Worker:
    """ 	                

     	                         pull from tracker
		                         |
		                      ___| ___
             			     |        |
    req router 9999   (rtr_sock)-----| worker |--- broker 4444 (brk_sock) 
		                     |________|
		                         |
		                         |
		                push to proxy/stream server

    """

    def __init__(self, ctx):
 
        brk_sock = ctx.socket(zmq.REQ)
        brk_sock.connect('tcp://127.0.0.1:4444')
        self.brk = zmqstream.ZMQStream(brk_sock, loop)
        self.brk.on_recv(self.brk_recv)
        self.brk.on_send(self.brk_send)

        rtr_sock = ctx.socket(zmq.REQ)
        rtr_sock.connect('tcp://127.0.0.1:9999')
        self.rtr = zmqstream.ZMQStream(rtr_sock, loop)
        self.rtr.on_recv(self.rtr_recv)
        self.rtr.on_send(self.rtr_send)
        self.rtr.send('ready')

    def rtr_send(self, *args):
        #logger.debug('sent to router: %s' % str(args))
        pass 

    def rtr_recv(self, message):
        #logger.debug('received from router: %s' % str(message))
        #print len(message)
        #print message[-3]
        command = message[-2]
        image = message[-1]
        with open('image.jpg', 'wb') as f:
             f.write(image)
        sleep = random.randint(1, 10)
        time.sleep(sleep)
        message = message[:-1]
        message[-1] = dumps('detection')
        self.rtr.send_multipart(message)

    def brk_send(self):
        pass

    def brk_recv(self):
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
    ctx = zmq.Context()
    worker = Worker(ctx)
    loop.start()
