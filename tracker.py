import logging
logger = logging.getLogger('worker_log')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formater = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
handler.setFormatter(formater)
logger.addHandler(handler)


import collections
import errno
import functools
import pymongo
import random
import socket
import sys
import time
import zmq

from tornado import iostream

from zmq.eventloop import ioloop, zmqstream
loop = ioloop.IOLoop.instance()

from zmq.utils.jsonapi import dumps, loads

class Tracker:
    """                     

			      push to workers (implemented in C tracker)
				     |
				 ____|____
				|         |
	requests to workers  ---| tracker |--- broker 4444 (brk_sock) 
				|____ ____|
				     |
				     |
			      push to proxy/stream server (implemented in C Tracker)

    """

    def __init__(self, wrk, message):

        self.fifo_send = collections.deque()
        self.fifo_recv = collections.deque()

        self.ctx = zmq.Context.instance()
        self.loop = ioloop.IOLoop.instance()

        self.current = None #most up to date timestamp from camera
        self.routerConnect()
        self.brokerSubscribe()
        self.cameraCreate('camera server')
        self.ctrackerStart()
        message[-1] = self.camera_port
        logger.debug('respond to broker, being tracker, from worker sock (: %s' % message)
        wrk.send_multipart(message) #notify router that role has change
        #wrk.close() #not so fast

    def ctrackerStart(self):
        pass
 
    def brokerSubscribe(self):
        brk_sock = self.ctx.socket(zmq.SUB)
        brk_sock.connect('tcp://127.0.0.1:4444')
        self.brk = zmqstream.ZMQStream(brk_sock, self.loop)
        self.brk.on_recv(self.brokerRecv)
        self.brk.on_send(self.brokerSend)

    def routerConnect(self):
        rtr_sock = self.ctx.socket(zmq.REQ)
        rtr_sock.connect('tcp://127.0.0.1:7777')
        self.rtr = zmqstream.ZMQStream(rtr_sock, self.loop)
        self.rtr.on_recv(self.routerRecv)
        self.rtr.on_send(self.routerSend)
        self.tasks = ioloop.PeriodicCallback(self.workerRequest, 1, self.loop)
        self.tasks.start()
    
    def cameraCreate(self, camera):
        
        if camera == 'camera server': 
            icm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            icm_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            icm_sock.setblocking(0)
            min_port = 40000
            max_port = 50000
            while True:
                try:
                    port = random.randint(min_port, max_port)
                    icm_sock.bind(('', port))
                    break
                except socket.error as e:
                    raise e
            icm_sock.listen(1)
            callback = functools.partial(self.cameraConnect, icm_sock)
            self.loop.add_handler(icm_sock.fileno(), callback, loop.READ)
            self.camera_port = str(port)

        elif camera == 'camera client':
            pass

    def cameraConnect(self, sock, fd, events):

        try:
            self.connection, address = sock.accept()
            logger.info('icm connection accepted')
        except socket.error, e:
            if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return
        self.connection.setblocking(0)
        stream = iostream.IOStream(self.connection, self.loop)
        stream.read_until('\n', self.cameraRead)

    def cameraRead(self, message):
        try:
            logger.info('camera client notification: %s ' % message)
            self.fifo_send.append(message)
            self.fifo_recv.append(message)
            #self.connection.send('hello\n')
            #connection.close()
        except socket.error, e:
            print e
        finally:
            self.loop.add_callback(self.cameraRead)

    def cameraReconfigure(self):
        self.connection.send('reconfigure\r\n')

    def workerRequest(self):
        """
        request = {'timestamp': timestamp, 
                   'task': 'detection',
                   'parameters': (...)}
        message = [dumps(request), image]
        """
        
        if len(self.fifo_send) > 0:
            timestamp = self.fifo_send.popleft()
            request = {'timestamp': timestamp, 'task': 'detection'}
            with open('mountain.jpg', 'rb') as f:
                self.rtr.send_multipart([dumps(request), f.read() ])

    def routerSend(self, *args):
        pass

    def routerRecv(self, message):
        """
        response = {'timestamp': timestamp,
                    'results': (...)}
        """

        response = loads(message[-1])
        logger.debug(response)
        self.fifo_recv.popleft()

        if len(self.fifo_recv) > 20: #congestion control...
            pass
            #    self.cameraReconfigure()
        #trk.send(response)


    def brokerRecv(self, message):
        print message

    def brokerSend(self, *args):
        print args



if __name__ == '__main__':
    ctx = zmq.Context()
    tracker = Tracker()
    loop.start()
                           
