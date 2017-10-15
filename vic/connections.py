import socket
import threading
import sched
import time
from protocol import *


PORT = 5999
activeConnections = []
lock = threading.Lock() 


def getMyIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 80))
    return sock.getsockname()[0]


def getLanPrefix(myIP):
    return myIP[0:myIP.rfind('.')]


def tryToAddToPool(ip, port):
    global activeIPs
    global activeConnections
    global lock

    if ip == getMyIP():
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    try:
        sock.connect(server_address)
        print("connected to", server_address)
        with lock:
            activeConnections.append(server_address)
    except (ConnectionRefusedError, OSError) as e:
        pass
    finally:
        sock.close()
    return

def findAvailableMachines():
    global PORT

    threads = []
    my_ip = getMyIP()
    ip_prefix = getLanPrefix(my_ip)

    for i in range(1, 255):
        ip = ip_prefix + '.' + str(i)
        thread = threading.Thread(target=tryToAddToPool, args=[ip, PORT])
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    print("founded active connections")

def heartbeat():
    global activeConnections

    with lock:
        connectionAddr = activeConnections.pop(0) if len(activeConnections) > 0 else None

    if connectionAddr is not None:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            connection.connect(connectionAddr)
            ip = connection.getpeername()[0]
            ping(connection)
            data = connection.recv(4096)
            if 'PONG' not in data.decode('utf-8'):
                raise Exception()

            with lock:
                activeConnections.append(connection)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print("disconnecting from", connection_addr)
        finally:
            connection.close()

    timer = threading.Timer(0.5, heartbeat)
    timer.daemon = True
    timer.start()


def startHeartbeat():
    timer = threading.Timer(0.5, heartbeat)
    timer.daemon = True
    timer.start()


def handlePeer(connection, address):
    global PORT
    print("peer at {} is connected".format(address))
    try:
        while True:
            data = connection.recv(4096)
            if len(data):
                decoded_data = data.decode('utf-8')

                if "PING" in decoded_data:
                    answerPing(connection)


                elif "HELLO" in decoded_data:
                    tryToAddToPool(address[0], PORT)
                    answerHello(connection)

                elif "CHUNK" in decoded_data:
                    answerChunk(connection, decoded_data)

            else:
                break
    except:
        pass
    finally:
        connection.close()


def listen():
    global PORT

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', PORT)
    sock.bind(server_address)
    sock.listen(1)
    while True:
        try:
            connection, client_address = sock.accept()
            connectionThread = threading.Thread(target=handlePeer, args=[connection, client_address])
            connectionThread.daemon = True
            connectionThread.start()
        except:
            pass


def startListening():
    thread = threading.Thread(target=listen)
    thread.daemon = True
    thread.start()


def broadcastArrival():
    global activeConnections

    with lock:
        for connectionAddr in activeConnections:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                connection.connect(connectionAddr)
                hello(connection)
                data = connection.recv(4096)
            except:
                pass
