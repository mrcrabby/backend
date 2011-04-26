"""                        _______
                          |       |
broker 2222 (brk_sock) ---|  GUI  |
                          |_______|

"""

import zmq

ctx = zmq.Context()
brk_sock = ctx.socket(zmq.REQ)
brk_sock.connect('tcp://localhost:2222')

while True:
      brk_sock.send('Hello from gui!')
      print brk_sock.recv()


