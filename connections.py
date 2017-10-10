import socket

def getMyIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 80))
    return sock.getsockname()[0]


def getLanPrefix(myIP):
    return myIP[0:myIP.rfind('.')]

def heartbeat(scheduler, connections, logger, port=5999):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for idx, connection in zip(range(0, len(connections)), connections):
        try:
            server_address = (connection, port)
            sock.connect(server_address)
        except ConnectionRefusedError:
            logger.debug("A maquina no endereco {} saiu da rede".format(connection))
            del connections[idx]
        finally:
            sock.close()
    scheduler.enter(10, 1, heartbeat, (scheduler, connections, logger, port,))         



