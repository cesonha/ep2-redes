import socket
import sys
import time
import threading
from queue import Queue

class Listener(threading.Thread):

    peers = set()
    numbers = []

    def __init__(self, host, port, communicationQueue, number=None, logger=None, leader=False, \
                    group=None, target=None, name=None, args=(), kwargs={}, daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # o proprio ta por default na lista dele
        self.host = host
        peers.add(host)
        self.port = port
        self.leader = leader
        self.logger = logger
        self.queue = communicationQueue
        self.number = number
        if Leader is True:
            numbers = [False for i in range(number)]

    def run(self):
        try :
            self.listenerSocket.bind((self.host, self.port))
        except socket.error as msg:
            self.logger.error("Problemas na hora de fazer o binding erro: {} {}".format(msg[0], msg[1]))
            sys.exit()
        self.logger.info("Consegui me conectar!")
        self.listenerSocket.listen(10)
        while True:
           conn, addr = self.listenerSocket.accept()
           self.logger.debug("A maquina no IP {} se conectou comigo".format(addr[0]))
           peers.add(addr[0])
           handlerThread = threading.Thread(self.handlePeer, args=(conn, addr))
           handlerThread.start()

    def handlePeer(self, conn, addr):
        try :
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                if "PEERS" in data:
                    self.logger.debug("Pediram a lista de PEERS")
                    conn.sendall(peersList())
                elif "CHUNK" in data:
                    self.logger.debug("Recebido {}".format(data))
                    conn.sendall("OK " + data)
        finally:
            conn.close()

    def peersList(self):
        message = "PEERS "
        message += "(" + ", ".join("{}".format(peer) for peer in peers) + ")"
        return message
