import socket
import gvars as gl
from network import *

def hello(connection):
    with gl.lock:
        p = gl.p

    if p is None:
        connection.send(bytes("HELLO", "utf-8"))
    else:
        connection.send(bytes("OBEY {} {}".format(p, getMyIP()), "utf-8"))

def answerHello(connection):
    connection.send(bytes("HI", "utf-8"))

def chunk(connection, interval, left_end):
    connection.send(bytes("CHUNK {} {} {}".format(interval[0], interval[1], left_end), "utf-8"))

def answerChunk(connection, recv_data):
    args = recv_data.split(" ")
    i = int(args[1])
    j = int(args[2])
    left_end = int(args[3])
    print("computando o intervalo {} a {}".format(i, j))

    with gl.lock:
        p = gl.p
        gl.start = left_end

    for d in range(i, j):
        if p % d == 0:
            connection.send(bytes("COMPOSITE " + str(d), "utf-8"))
            return

    connection.send(bytes("UNKNOWN", "utf-8"))


def ping(connection):
    connection.send(bytes("PING", "utf-8"))

def answerPing(connection):
    connection.send(bytes("PONG", "utf-8"))
