import threading
from protocol import *
import gvars as gl


def handleClient(connection, client_address):
    print("connected to new client:", client_address)
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
                elif "VOTE" in decoded:
                    args = decoded.split(" ")
                    receivedVote = args[1]
                    with gl.lock:
                        gl.votes[client_address] = receivedVote
                        if gl.executionMode == "COMPUTING":
                            gl.executionMode = "VOTING"
                    answerVote(connection)
            else:
                break
    finally:
        connection.close()


def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', gl.PORT)
    sock.bind(server_address)
    sock.listen(1)
    while True:
        connection, client_address = sock.accept()
        connectionThread = threading.Thread(target=handleClient, args=[connection, client_address])
        connectionThread.daemon = True
        connectionThread.start()


def startFollowerThread():
    thread = threading.Thread(target=listen)
    thread.daemon = True
    thread.start()

