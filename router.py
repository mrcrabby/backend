import logging

logger = logging.getLogger('router_log')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formater = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
handler.setFormatter(formater)
logger.addHandler(handler)

import time
import zmq
ctx = zmq.Context()

class Router:
    """

         tracker    tracker    tracker
            |          |          |
            |__________|__________|
                       |
                       | trk_sock 7777
                   ____|____                               ____ broker 
                  |         |  brk_sock 8888 prioritized  |
                  |  Router |-----------------------------|---- broker
                  |_________|                             |____ 
                       |                                        broker
                       |
                       | wrk_sock 9999
             __________|___________
            |          |           |
            |          |           |
         worker      worker      worker

    """
    def __init__(self):
        wrk_sock = ctx.socket(zmq.XREP)
        wrk_sock.bind('tcp://127.0.0.1:9999')
        
        brk_sock = ctx.socket(zmq.XREP)
        brk_sock.bind('tcp://127.0.0.1:8888')
        
        trk_sock = ctx.socket(zmq.XREP)
        trk_sock.bind('tcp://127.0.0.1:7777')
        
        available_workers = 0
        workers = []  #avaiable worker's addresses

        poller = zmq.Poller()
        
        poller.register(trk_sock, zmq.POLLIN)
        poller.register(wrk_sock, zmq.POLLIN)
        poller.register(brk_sock, zmq.POLLIN)

        while True:
            active_socks = dict(poller.poll())

            if wrk_sock in active_socks and active_socks[wrk_sock] == zmq.POLLIN:

               wrk_addr = wrk_sock.recv()
               logger.debug('worker address: %s' % wrk_addr)
               workers.append(wrk_addr)
               available_workers += 1
               logger.debug('workers: %s' % available_workers)

               empty = wrk_sock.recv()
               assert empty == ''
               trk_addr = wrk_sock.recv()
               logger.debug('trk_addr: %s' % trk_addr)

               if trk_addr != 'ready':

                   empty = wrk_sock.recv()
                   assert empty == ''
                   reply = wrk_sock.recv(copy=False)
                   logger.debug('reply: %s' % reply)
                   trk_sock.send_multipart([trk_addr, '', wrk_addr, '', reply])

            if available_workers > 0:
                
                logger.debug('workers are available - polling broker before polling trackers')
                if brk_sock in active_socks and active_socks[brk_sock] == zmq.POLLIN:
                    logger.debug('activity on broker')
                    brk_addr = brk_sock.recv()

                    empty = brk_sock.recv()
                    assert empty == ''
                    request = brk_sock.recv(copy=False)
                    logger.debug('request: %s' % request)
                    request2 = brk_sock.recv(copy=False)

                    available_workers -= 1

                    wrk_addr = workers.pop() #strongest machine
                    wrk_sock.send_multipart([wrk_addr, '', brk_addr, '', request, request2])


                logger.debug('workers are available - polling trackers')
                if trk_sock in active_socks and active_socks[trk_sock] == zmq.POLLIN:
                    logger.debug('activity on trackers')                
	            trk_addr = trk_sock.recv()
	    
  	            empty = trk_sock.recv()
	            assert empty == ''
  	            request = trk_sock.recv(copy=False)
	            logger.debug('request: %s' % request)
                    image = trk_sock.recv(copy=False)

	            available_workers -= 1 

	            wrk_addr = workers.pop()
	            wrk_sock.send_multipart([wrk_addr, '', trk_addr, '', request, image])  

if __name__ == '__main__':
    router =  Router()
