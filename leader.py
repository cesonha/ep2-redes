from network import *
from protocol import *
import threading
import time
import gvars as gl


def talkToServer(address, port):
    while True: # try to connect loop 
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (address, port)
            connection.connect(server_address)
            print("New server:", address)
            hello(connection)
            data = connection.recv(4096)

            time_of_last_interaction = time.time()

            with gl.lock:
                gl.connected_ips.append(address)

            while True: # try to make request loop 
                willSleep = False
                with gl.lock:
                    if gl.state == "FOLLOWER":
                        willSleep = True
                if willSleep:
                    if (time.time() - time_of_last_interaction) > 5: # 5 seconds without communicating
                        try:
                            print("pinging", address)
                            ping(connection)
                            pong = connection.recv(4096)
                            if "PONG" not in pong.decode("utf-8"):
                                raise Exception()
                            time_of_last_interaction = time.time()
                        except:
                            raise
                            break
                    time.sleep(1)
                    continue

                with gl.lock:
                    done = (gl.isComposite or gl.processed_count >= gl.original_interval_count) and state == "LEADER"
                    is_prime = not gl.isComposite
                if done:
                    try:
                        finished(connection, is_prime, getMyIP())
                        xoxo = connection.recv(4096)
                        if "XOXO" not in xoxo.decode("utf-8"):
                            raise Exception()
                        with gl.lock:
                            gl.broadcasted_count += 1
                    except:
                        raise
                        break

                try:
                    with gl.lock:
                        interval = gl.intervals.pop(0)
                except IndexError:
                    continue

                try:
                    print("sending", interval, "to", server_address)
                    with gl.lock:
                        left_end = gl.calculated_intervals[0][0]
                    chunk(connection, interval, left_end)

                    data = connection.recv(4096)
                    if len(data):
                        time_of_last_interaction = time.time()

                        if "COMPOSITE" in data.decode("utf-8"):
                            with gl.lock:
                                gl.isComposite = True

                        with gl.lock:
                            gl.processed_count += 1
                            gl.calculated_intervals.remove(interval)
                    else:
                        break
                except:
                    with gl.lock:
                        gl.intervals.append(interval)
                    raise
        except OSError:
            pass
        finally:
            with gl.lock:
                try:
                    gl.connected_ips.remove(address)
                except:
                    pass
            connection.close()


def testIntervalMyself():
    while True:
        willSleep = False
        with gl.lock:
            if gl.state != "LEADER":
                willSleep = True
        if willSleep:
            time.sleep(1)
            continue

        try:
            with gl.lock:
                interval = gl.intervals.pop(0)
        
            for d in range(interval[0], interval[1]):
                with gl.lock:
                    if gl.p % d == 0:
                        gl.isComposite = True
            with gl.lock:
                gl.processed_count += 1
                gl.calculated_intervals.remove(interval)
        except:
            pass


def startLeaderThread():
    my_ip = getMyIP()
    ip_prefix = getLanPrefix(my_ip)
    for i in range(1, 255):
        ip = ip_prefix + "." + str(i)
        if ip == my_ip:
            continue

        thread = threading.Thread(target=talkToServer, args=[ip, gl.PORT])
        thread.daemon = True
        thread.start()

    thread = threading.Thread(target=testIntervalMyself)
    thread.daemon = True
    thread.start()
