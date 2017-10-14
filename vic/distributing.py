import threading
import math
from connections import *


state = 'FOLLOWER'
p = None
intervals = None
original_interval_count = None
processed_count = 0
isPrime = True
computing_lock = threading.Lock() 
test_range = 1000


def sendChunkRequest(connection):
    global computing_lock
    global lock
    global processed_count
    global intervals
    global isPrime

    try:
        with computing_lock:
            interval = intervals.pop(0)
    except:
        return

    try:
        chunk(connection, interval, -1)
        data = sock.recv(4096)

        if len(data):
            with computing_lock:
                processed_count += 1

            msg = data.decode('utf-8').split(' ')

            if msg[0] == 'COMPOSITE':
                with computing_lock:
                    isPrime = False
    except:
        with computing_lock:
            intervals.insert(0, interval)


def leader():
    global state
    global isPrime
    global processed_count
    global original_interval_count
    global lock
    global computing_lock
    global activeConnections

    while True:
        with computing_lock:
            if state != 'LEADER' or not isPrime or processed_count >= original_interval_count:
                print(isPrime)
                break

        threads = []
        with lock:
            for connection in activeConnections:
                threads.append(threading.Thread(target=sendChunkRequest, args=[connection]))
                threads[-1].start()

        for thread in threads:
            thread.join()


def startLeaderThread(prime, start = 2):
    global intervals
    global p
    global state
    global test_range
    global original_interval_count
    global processed_count
    global computing_lock

    with computing_lock:
        state = 'LEADER'
        p = prime
        intervals = [(2 + i * test_range, min(math.sqrt(p) + 1, 2 + (i+1) * test_range)) for i in range((start - 2) // test_range, math.ceil((math.sqrt(p) - 1) / test_range))]
        processed_count = 0
        original_interval_count = len(intervals)

    threading.Thread(target=leader).start()

