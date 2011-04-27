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

class Ventilator:

    def __init__(self, ctx):
 
        push_sock = ctx.socket(zmq.PUSH)
        push_sock.bind('tcp://127.0.0.1:13131')
        for i in range(1000):
            push_sock.send(str(i))
            time.sleep(0.5)
        

if __name__ == '__main__':
    ctx = zmq.Context()
    worker = Ventilator(ctx)
    loop.start()
