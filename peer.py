import socket
import sys
import time
import logging
import threading #TODO: precisamos disso aqui mesmo?

from listener import Listener


def geMyIpAddress():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 80))
    return sock.getsockname()[0]

logger = logging.getLogger('peer')
PORT = 5000 # porta do socket que ouve as conexoes
leader = False
number = -1
if (len(sys.argv) > 1):
    leader = True
    number = int(sys.argv[1])

hostIp = getMyIpAddress()
communicationQueue = Queue()
listener = Listener(hostIp, PORT, communicationQueue, number=number, logger=logger, leader=leader)


