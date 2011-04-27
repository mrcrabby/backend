import os
import time

from zmq.eventloop import ioloop
loop = ioloop.IOLoop.instance()

def callback(*args):
    print args
    time.sleep(10)


loop.add_handler(os.open('.', os.O_RDONLY), callback, loop.READ)
loop.start()

