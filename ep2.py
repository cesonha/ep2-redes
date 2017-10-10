import sys
import math
import json
import socket
import re
import time
import sched
import threading
import connections
import logging

PORT = 5999
test_range = 1000

processed_count = 0
threads = []
activeConnections = []
lock = threading.Lock() 
isComposite = False
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name="peer-{}".format(connections.getMyIp()))


p = None if len(sys.argv) < 2 else int(sys.argv[1])
intervals = [] if len(sys.argv) < 2 else [(2+test_range*i, min(p-1, 2+test_range*(i+1))) for i in range(math.ceil((p-2) / test_range))]
original_interval_count = None if len(sys.argv) < 2 else len(intervals)


def checkServer(address, port):
    global p
    global intervals
    global original_interval_count
    global processed_count
    global lock
    global isComposite
    global activeConnections
    global logger

    while True:
        with lock:
            if original_interval_count <= processed_count or isComposite:
                break

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (address, port)
            sock.connect(server_address)
            logger.debug("connectado a: {}".format(address))
            activeConnections.append(address)
            while True:
                with lock:
                    try:
                        interval = intervals.pop(0)
                        logger.info("recebi: {}".format(interval))
                    except IndexError:
                        logger.info("tentando receber de novo um intervalo")
                        if original_interval_count <= processed_count or isComposite:
                            break
                        continue

                try:
                    logger.info("enviando intervalo: {}".format(interval))
                    sock.send(bytes(json.dumps((p, interval)), 'utf-8'))

                    data = sock.recv(4096)
                    if len(data):
                        with lock:
                            processed_count += 1

                        if data.decode('utf-8') == 'True':
                            with lock:
                                isComposite = True
                    else:
                        break
                except:
                    with lock:
                        intervals.append(interval)
                    raise

        except (ConnectionRefusedError, OSError) as e:
            sock.close()


def connectionDetector():
    myIP = connections.getMyIP()
    for i in range(1, 255):
        ip = connections.getLanPrefix(myIP) + str(i)
        threads.append(threading.Thread(target=checkServer, args=[ip, PORT]))
        threads[-1].start()


def foundDivisor(p, interval):
    for d in range(interval[0], interval[1] + 1):
        if p % d == 0:
            return True
    return False


def handlePeer(connection, address):
    try:
        while True:
            data = conncetion.recv(4096)
            if len(data):
                p, interval = json.loads(data.decode('utf-8'))
                print("received:", p, interval)
                connection.send(bytes(str(foundDivisor(p, interval)),'utf-8'))
            else:
                    break
    except socket.error as error:
        logger.error("erro ao se comunicar :(")
    finally:
        connection.close()
    return

def follower():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', PORT)
    sock.bind(server_address)
    sock.listen(1)
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(10, 1, connections.heartbeat, (scheduler, activeConnections, logger, port,))
    scheduler.run()
    while True:
        connection, client_address = sock.accept()
        connectionThread = threading.Thread(target=handlePeer, args=(connection, client_address))
        connectionThread.daemon = True
        connectionThread.start()
        activeConnections.append(connection)

def main():
    global isComposite

    if len(sys.argv) < 2:
        follower()
    else:
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(10, 1, connections.heartbeat, (scheduler, activeConnections, port,))
        scheduler.run()
        threads.append(threading.Thread(target=connectionDetector))
        threads[0].start()
        while True:
            with lock:
                if original_interval_count <= processed_count or isComposite:
                    break

            time.sleep(2) #TODO MULTIPROCESS WHATS BELOW
            try:
                with lock:
                    interval = intervals.pop(0)
                if foundDivisor(p, interval):
                    with lock:
                        isComposite = True
            except:
                continue

        print(isComposite)
        for thread in threads:
            thread.join()

if __name__ == '__main__':
    main()

