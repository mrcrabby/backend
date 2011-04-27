import logging
logger = logging.getLogger('proxy_log')
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

class Sink:

    def __init__(self, ctx):
 
        pull_sock = ctx.socket(zmq.PULL)
        pull_sock.connect('tcp://127.0.0.1:12121')
        self.pull = zmqstream.ZMQStream(pull_sock, loop)
        self.pull.on_recv(self.pullRecv)
        
    def pullRecv(self, message):
        print message

        

if __name__ == '__main__':
    ctx = zmq.Context()
    worker = Sink(ctx)
    loop.start()
