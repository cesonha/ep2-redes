import socket
import sys
import time
import threading
from queue import Queue
from computingThread import ComputingThread

class Manager:

    peers = {}
    connections = []
    communicationQueue = Queue()

    def __init__(self, host, port, number):
        self.listenerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # o proprio ta por default na lista dele
        # peers e um dicionario com endereco e porta
        self.host = host
        self.port = port
        self.peers[host] = port
        self.number = number

    def run(self):
        try :
            self.listenerSocket.bind((self.host, self.port))
        except socket.error as msg:
            print("Bind failed. Error Code : {} Message {}".format(msg[0], msg[0]))
            sys.exit()

        running = True
        self.listenerSocket.listen(10)
        calculationThread = ComputingThread(kwargs={'number': self.number, 'queue': self.communicationQueue})
        calculationThread.start()
        while running:
           conn, addr = self.listenerSocket.accept()
           self.connections.append(conn)
           self.peers[addr[0]] = addr[1]
           handlerThread = threading.Thread(self.handlePeer, args=(conn, addr))
           handlerThread.start()

    def handlePeer(self, conn, addr):
        while True:
            data = conn.recv(1024)
            if not data:
                break
            if ("any" in data):
                conn.sendall("any")
            else:
                print("recebido: " + data)
                conn.sendall("OK " + data)

    def updatePeers(self):
        message = "PEERS "
        message += "(" + ", ".join("{}:{}".format(host, port) for host, port in self.peers.items()) + ")"

        for connection in self.connections:
            connection.send(message)

