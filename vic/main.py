from connections import *


def main():
    socket.setdefaulttimeout(10.0)
    startListening()
    findAvailableMachines()
    startHeartbeat()
    broadcastArrival()


if __name__ == '__main__':
    main()
