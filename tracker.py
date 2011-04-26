import logging
logger = logging.getLogger('worker_log')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formater = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
handler.setFormatter(formater)
logger.addHandler(handler)

import functools
import pymongo
import random
import socket
import sys
import zmq

from tornado import iostream

from zmq.eventloop import ioloop, zmqstream
loop = ioloop.IOLoop.instance()

from zmq.utils.jsonapi import dumps, loads

class Tracker:
    """                     

			      push to workers
				     |
				 ____|____
				|         |
	requests to workers  ---| tracker |--- broker 4444 (brk_sock) 
				|____ ____|
				     |
				     |
			      push to proxy/stream server

    """

    def __init__(self, ctx):

        brk_sock = ctx.socket(zmq.REQ)
        brk_sock.connect('tcp://127.0.0.1:4444')
        self.brk = zmqstream.ZMQStream(brk_sock, loop)
        self.brk.on_recv(self.brokerRecv)
        self.brk.on_send(self.brokerSend)

        icm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        icm_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        icm_sock.setblocking(0)
        icm_sock.bind(('', 11111))
        icm_sock.listen(128)
        callback = functools.partial(self.cameraConnect, icm_sock)
        loop.add_handler(icm_sock.fileno(), callback, loop.READ)
    
        rtr_sock = ctx.socket(zmq.REQ)
        rtr_sock.connect('tcp://127.0.0.1:7777')
        self.rtr = zmqstream.ZMQStream(rtr_sock, loop)
        self.rtr.on_recv(self.routerRecv)
        self.rtr.on_send(self.routerSend)
        self.tasks = ioloop.PeriodicCallback(self.workerSend, 1, loop)
        self.tasks.start()

    def cameraConnect(self, sock, fd, events):

        try:
            connection, address = sock.accept()
            logger.info('icm connection accepted')
        except socket.error, e:
            if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return
        connection.setblocking(0)
        stream = iostream.IOStream(connection, loop)
        stream.read_bytes(22, self.cameraRead)
        #callback = functools.partial(self.cameraRead, connection, address)
        #loop.add_callback(callback)

    def cameraRead(self, connection, address):
        try:
            message = connection.recv(10)
            logger.info('Camera client ready received: %s from %s' % (message, address))
            connection.send('hello\n')
            #connection.close()
        except socket.error, e:
            print e
            #logger.debug('icm read nothing')
        finally:
            callback = functools.partial(self.cameraRead, connection, address)
            loop.add_callback(callback)

    def workerSend(self):
        with open('mountain.jpg', 'rb') as f:
            self.rtr.send_multipart(['task', f.read() ])

    def brokerRecv(self, message):
        print message

    def brokerSend(self, *args):
        print args

    def routerRecv(self, message):
        print message

    def routerSend(self, *args):
        pass

if __name__ == '__main__':
    ctx = zmq.Context()
    tracker = Tracker(ctx)
    loop.start()
                           
