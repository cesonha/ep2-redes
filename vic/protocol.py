import socket
import threading
from computing import *

def ping(connection):
    connection.send(bytes('PING', 'utf-8'))

def answerPing(connection):
    connection.send(bytes('PONG', 'utf-8'))

def hello(connection):
    connection.send(bytes('HELLO', 'utf-8'))

def answerHello(connection):
    connection.send(bytes('OK', 'utf-8'))

def chunk(connection, interval, checkpoint):
    connection.send(bytes('CHUNK ' + str(interval[0]) + ' ' + str(interval[1]) + ' ' + str(checkpoint), 'utf-8'))

def answerChunk(connection, recv_data):
    # TODO guardar checkpoint
    args = recv_data.split(' ')
    i = int(args[1])
    j = int(args[2])
    print("computando o intervalo {} a {}".format(i, j))
    connection.send(bytes(searchDivisor(prime, (i, j)), 'utf-8'))
