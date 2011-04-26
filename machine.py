import zmq

class Machine():
    brk_sock = ctx.socket(zmq.REQ)
    brk_sock.connect('tcp://127.0.0.1:4444')
    self.brk = zmqstream.ZMQStream(brk_sock, loop)
    self.brk.on_recv(self.brokerRecv)

