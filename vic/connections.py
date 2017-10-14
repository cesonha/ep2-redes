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
            activeConnections.append(sock)
    except (ConnectionRefusedError, OSError) as e:
        sock.close()


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


# TODO when does this thread dies?
def heartbeat(scheduler):
    global activeConnections

    with lock:
        if not len(activeConnections):
            scheduler.enter(0.1, 0.5, heartbeat, (scheduler,))
            return

        connection = activeConnections.pop(0)

    try:
        ping(connection)
        data = connection.recv(4096)
        if 'PONG' not in data.decode('utf-8'):
            raise Exception()

        with lock:
            activeConnections.append(connection)
    except:
        connection.close()

    scheduler.enter(0.1, 0.5, heartbeat, (scheduler,))


def startHeartbeat():
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(1, 0.5, heartbeat, (scheduler,))
    scheduler.run()


def handlePeer(connection, address):
    global PORT

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
        for connection in activeConnections:
            try:
                hello(connection)
                data = connection.recv(4096)
            except:
                pass
