import threading
from protocol import *
import gvars as gl


def handleClient(connection, client_address, event):
    print("connected to new client:", client_address)
    done = False
    try:
        while True:
            data = connection.recv(4096)

            if len(data):
                print("received", data, "from", client_address)

                decoded = data.decode("utf-8")

                if "CHUNK" in decoded:
                    answerChunk(connection, decoded)
                elif "HELLO" in decoded:
                    answerHello(connection)
                elif "OBEY" in decoded:
                    with gl.lock:
                        args = decoded.split(" ")
                        gl.p = int(args[1])
                        gl.leader_ip = args[2]
                    answerHello(connection)
                elif "PING" in decoded:
                    answerPing(connection)
                elif "DONE" in decoded:
                    args = decoded.split(" ")
                    isPrime = args[1]
                    foundBy = args[2]
                    if gl.debug:
                        if isPrime is "True":
                            gl.logger.debug("{} is prime".format(gl.p))
                        else:
                            gl.logger.debug("{} is composite, informed by {}".format(gl.p, foundBy))
                    answerFinished(connection, decoded)
                    done = True
                    break
                elif "VOTE" in decoded:
                    args = decoded.split(" ")
                    receivedVote = args[1]
                    with gl.lock:
                        gl.votes[client_address] = receivedVote
                        if gl.executionMode == "COMPUTING":
                            gl.executionMode = "VOTING"
                            event.set()
                    answerVote(connection)
            else:
                break
    finally:
        connection.close()
        if done:
            import sys
            sys.exit(0)


def listen(event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', gl.PORT)
    sock.bind(server_address)
    sock.listen(1)
    while True:
        connection, client_address = sock.accept()
        connectionThread = threading.Thread(target=handleClient, args=[connection, client_address, event])
        connectionThread.daemon = True
        connectionThread.start()


def electionThread():
    event.wait()
    #started election
    agreement = False
    while not agreement:
        with gl.lock:
            gl.votes[getMyIP()] = getMyVoteIP() 
            for connectedIp in gl.connected_ips:
                try:
                    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_address = (connectedIp, gl.PORT)
                    connection.connect(server_address)
                    vote(connection, getMyVoteIP())
                    data = connection.recv(4096)
                    message = data.decode("utf-8")
                    if "VOTE" in message:
                        receivedVote = message.split(" ")[-1]
                        votes[connectedIp] = receivedVote
                    else:
                        raise Exception()
                except:
                    raise
                    pass
                finally: 
                    connection.close()
        agreement = all(vote == votes[getMyIP()] for vote in votes.values())
        if not agreement:
            votes.clear()
        #TODO o que fazer quando achou um lider no caso dos followers

def startFollowerThread():
    event = threading.Event()
    thread = threading.Thread(target=listen, args=[event])
    thread.daemon = True
    thread.start()
