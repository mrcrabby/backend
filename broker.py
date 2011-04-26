import datetime
import errno
import functools
import logging
import pymongo

logger = logging.getLogger('broker_log')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formater = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
handler.setFormatter(formater)
logger.addHandler(handler)
										
import socket
import time

import zmq
from zmq.utils.jsonapi import dumps, loads

from zmq.eventloop import ioloop, zmqstream
loop = ioloop.IOLoop.instance()

ctx = zmq.Context()

class Broker():
    """

                     intelligent cameras' server 3333 (icm_sock)
				      |
				  ____|____
				 |         |
     workers 4444 (wrk_sock)  ---|  broker |--- GUI 2222 (gui_sock)
				 |_________|
                                      |
                                      |
                      mongo database connection (db_conn)

    """

    def __init__(self):

	gui_sock = ctx.socket(zmq.REP)
	gui_sock.bind('tcp://*:2222')
	self.gui = zmqstream.ZMQStream(gui_sock, loop)
        self.gui.on_recv(self.guiRecv)
        self.gui.on_send(self.guiSend)

	icm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	icm_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	icm_sock.setblocking(0)
	icm_sock.bind(('', 3333))
	icm_sock.listen(128)
	callback = functools.partial(self.cameraConnect, icm_sock)
	loop.add_handler(icm_sock.fileno(), callback, loop.READ)

	wrk_sock = ctx.socket(zmq.REP)
	wrk_sock.bind('tcp://*:4444')
	self.wrk = zmqstream.ZMQStream(wrk_sock, loop)
        self.wrk.on_recv(self.workerRecv)
        self.wrk.on_send(self.workerSend)

        db_conn = pymongo.Connection('localhost', 27017)
        self.db = db_conn['database']
        self.workers = self.db['workers']

    def cameraConnect(self, sock, fd, events):

	try:
	    connection, address = sock.accept()
	    logger.info('icm connection accepted')
	except socket.error, e:
	    if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
		raise
	    return
	connection.setblocking(0)
	callback = functools.partial(self.cameraRead, connection, address)
	loop.add_callback(callback)
	    

    def cameraRead(self, connection, address):
	try:
	    message = connection.recv(10)
            self.createTracker(connection, message)
            logger.info('Camera client ready received: %s from %s' % (message, address))
	    connection.send('hello')
	    #connection.close()
	except socket.error:
            pass
	    #logger.debug('icm read nothing')
	finally:
	    callback = functools.partial(self.cameraRead, connection, address)
	    loop.add_callback(callback)


    def createTracker(self, connection, message):
        #connection.send(tracker)
        pass


    def workerRecv(self, message):
        logger.info('Message from worker')
	command, address, speed =  loads(''.join(message))
        if command == 'register':
            self.workers.insert({'state': 'registered', 'address': address, 'speed': speed})
            self.wrk.send_json('accepted')

        elif command == 'unregister':
            self.workers.update({'address': address}, {'$set': {'state': 'unregistered'}})
        else:
            pass
           
        self.wrk.send_json(message) 

    def guiRecv(self, message):
	print message 
	self.gui.send_multipart(message) 

    def workerSend(self, message, *args):
	print 'sending: ',
	print message 

    def guiSend(self, message, *args):
	print 'sending: ',
	print message 

if __name__ == '__main__':
    broker  = Broker()   
    loop.start()


