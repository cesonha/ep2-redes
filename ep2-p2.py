import sys
import math
import json
import socket
import re
import time
import threading


test_range = 1000

processed_count = 0
threads = []
lock = threading.Lock() 
isComposite = False

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

    while True:
        with lock:
            if original_interval_count <= processed_count or isComposite:
                break

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (address, port)
            sock.connect(server_address)
            print("connected to", address)

            while True:
                with lock:
                    try:
                        interval = intervals.pop(0)
                        print("got", interval)
                    except IndexError:
                        print("retrying")
                        if original_interval_count <= processed_count or isComposite:
                            break
                        continue

                try:
                    print("sending", interval)
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
    for i in range(1, 255):
        ip = '172.17.0.' + str(i)
        threads.append(threading.Thread(target=checkServer, args=[ip, 5999]))
        threads[-1].start()


def foundDivisor(p, interval):
    for d in range(interval[0], interval[1]+1):
        if p % d == 0:
            return True
    return False


def follower():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', 5999)
    sock.bind(server_address)
    sock.listen(1)
    connection, client_address = sock.accept()
    try:
        while True:
            data = connection.recv(4096)
            if len(data):
                p, interval = json.loads(data.decode('utf-8'))
                print("received:", p, interval)
                connection.send(bytes(str(foundDivisor(p, interval)),'utf-8'))
            else:
                break
    finally:
        connection.close()


def main():
    global isComposite

    if len(sys.argv) < 2:
        follower()
    else:
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

