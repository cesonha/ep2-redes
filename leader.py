from network import *
from protocol import *
from math import *
import threading
import time
import gvars as gl


def talkToServer(address, port):
    while True: # try to connect loop 
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (address, port)
            connection.connect(server_address)
            hello(connection)
            data = connection.recv(4096)

            time_of_last_interaction = time.time()
            with gl.lock:
                if gl.debug:
                    gl.logger.debug("connected to {}".format(address))
                gl.connected_ips.append(address)

            while True: # try to make request loop 
                election = False
                with gl.lock:
                    if gl.state == "ELECTOR":
                        election = True
                if election:
                    should_send_vote = True
                    with gl.lock:
                        if address in gl.informed_electors:
                            should_send_vote = False
                    if should_send_vote:
                        try:
                            vote(connection)
                            response = connection.recv(4096)
                            time_of_last_interaction = time.time()
                            if "RECEIVED" in response.decode("utf-8"):
                                with gl.lock:
                                    gl.informed_electors.add(address)
                        except:
                            pass
                    time.sleep(1)
                    continue

                willSleep = False
                with gl.lock:
                    if gl.state == "FOLLOWER":
                        willSleep = True
                if willSleep:
                    if (time.time() - time_of_last_interaction) > 5: # 5 seconds without communicating
                        try:
                            ping(connection)
                            pong = connection.recv(4096)
                            if "PONG" not in pong.decode("utf-8"):
                                raise Exception()
                            time_of_last_interaction = time.time()
                        except:
                            with gl.lock:
                                if gl.debug:
                                    gl.logger.debug("machine at {} disconected".format(address))
                            raise
                            break
                    time.sleep(1)
                    continue

                with gl.lock:
                    done = (gl.isComposite or gl.processed_count >= gl.original_interval_count) and gl.state == "LEADER"
                    is_prime = not gl.isComposite
                if done:
                    with gl.lock:
                        gl.done = done
                    try:
                        finished(connection, is_prime,gl.foundBy)
                        xoxo = connection.recv(4096)
                        if "XOXO" not in xoxo.decode("utf-8"):
                            raise Exception()
                        with gl.lock:
                            gl.broadcasted_count += 1
                        return
                    except:
                        raise
                        break

                try:
                    with gl.lock:
                        interval = gl.intervals.pop(0)
                except IndexError:
                    continue

                try:
                    with gl.lock:
                        left_end = gl.calculated_intervals[0][0]
                        gl.start = left_end

                    chunk(connection, interval, left_end)

                    data = connection.recv(4096)
                    if len(data):
                        time_of_last_interaction = time.time()

                        if "COMPOSITE" in data.decode("utf-8"):
                            with gl.lock:
                                gl.isComposite = True
                                gl.foundBy = address

                        with gl.lock:
                            gl.processed_count += 1
                            gl.calculated_intervals.remove(interval)
                    else:
                        with gl.lock:
                            if gl.debug:
                                gl.logger.debug("machine at {} disconected".format(address))
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

                if address == gl.leader_ip:
                    gl.state = "ELECTOR"

            connection.close()


def testIntervalMyself():
    while True:
        election = False
        with gl.lock:
            if gl.state == "ELECTOR":
                election = True
        if election:
            possible_leaders = set()
            try:
                with gl.lock:
                    gl.connected_ips.sort()
                    gl.votes[getMyIP()] = gl.connected_ips[(gl.connected_ips.index(gl.leader_ip) + 1) % len(gl.connected_ips)]
                    print("=====================================================")
                    print("current leader:", gl.leader_ip)
                    print("connected:", gl.connected_ips)
                    print("votes:", gl.votes)
                    print("informed:", gl.informed_electors)

                    for ip in gl.connected_ips:
                        if ip != getMyIP() and ip not in gl.informed_electors:
                            raise Exception()
                        possible_leaders.add(gl.votes[ip])
                    if len(possible_leaders) == 1:
                        gl.leader_ip = possible_leaders.pop()
                        print("eleição acabou, novo lider:", gl.leader_ip)
                        am_leader = getMyIP() == gl.leader_ip
                        if am_leader:
                            gl.intervals = [(gl.start + i * gl.test_range, min(floor(sqrt(gl.p)) + 1, gl.start + (i+1) * gl.test_range)) for i in range(ceil((sqrt(gl.p) + 1 - gl.start) / gl.test_range))]
                            gl.calculated_intervals = list(gl.intervals)
                            gl.original_interval_count = len(gl.intervals)
                            timer = threading.Timer(30.0, beginElection)
                            timer.daemon = True
                            timer.start()
                        gl.votes = {}
                        gl.informed_electors = set()
                        gl.state = "LEADER" if am_leader else "FOLLOWER"
                    else:
                        print("mais uma rodada de eleição")
                        gl.votes = {}
                        gl.informed_electors = set()

            except:
                time.sleep(0.5)
            finally:
                print("=====================================================")
                time.sleep(1.0)
            continue

        willSleep = False
        with gl.lock:
            if gl.state != "LEADER":
                willSleep = True
        if willSleep:
            time.sleep(1)
            continue

        with gl.lock:
            done = gl.isComposite or gl.processed_count >= gl.original_interval_count
            if done:
                gl.done = done

        try:
            with gl.lock:
                interval = gl.intervals.pop(0)
        
            for d in range(interval[0], interval[1]):
                with gl.lock:
                    if gl.p % d == 0:
                        gl.isComposite = True
                        gl.foundBy = getMyIP()
            with gl.lock:
                gl.processed_count += 1
                gl.calculated_intervals.remove(interval)
                gl.start = gl.calculated_intervals[0][0]
        except:
            pass


def beginElection():
    with gl.lock:
        if gl.state == "LEADER":
            print("lider começou eleição")
            gl.state = "ELECTOR"
            timer = threading.Timer(30.0, beginElection)
            timer.daemon = True
            timer.start()


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

    with gl.lock:
        if gl.state == "LEADER":
            timer = threading.Timer(30.0, beginElection)
            timer.daemon = True
            timer.start()
