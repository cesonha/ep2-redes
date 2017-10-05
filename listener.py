import socket
import sys
import time
import threading
from queue import Queue
from computingThread import ComputingThread

class Listener(threading.Thread):

    peers = ['localhost']
    
    def __init__(self, host, port, number, communicationQueue, leader = False, \
                    group=None, target=None, name=None, args=(), kwargs={}, daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # o proprio ta por default na lista dele
        # peers e um dicionario com endereco e porta
        self.host = host
        self.port = port
        self.leader = leader
        self.number = number

    def run(self):
        try :
            self.listenerSocket.bind((self.host, self.port))
        except socket.error as msg:
            print("Bind failed. Error Code : {} Message {}".format(msg[0], msg[0]))
            sys.exit()

        self.listenerSocket.listen(10)
        while True:
           conn, addr = self.listenerSocket.accept()
           peers.append(addr[0])
           handlerThread = threading.Thread(self.handlePeer, args=(conn, addr))
           handlerThread.start()

    def handlePeer(self, conn, addr):
        try :
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                if "PEERS" in data:
                    conn.sendall(message )
                elif "CHUNK" in data:
                    print("recebido: " + data)
                    conn.sendall("OK " + data)
        finally:
            conn.close()

    def peers(self):
        message = "PEERS "
        message += "(" + ", ".join("{}:{}".format(host, port) for host, port in self.peers.items()) + ")"
        return message
