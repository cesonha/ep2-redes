import threading
import socket
import sys

class Communicator(threading.Thread):

    def __init__(self, addr, message, port=5000, \
            group=None, target=None, name=None, args=(), kwargs={},  daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.addr = addr
        self.port = port
        self.message = message
        self.communicatorSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        try:
            self.communicatorSocket.connect((self.addr, self.port))
        except ConnectionRefusedError:
            print("Nao consegui me conectar com {}:{}".format(self.addr, self.port))
        return

