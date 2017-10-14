from connections import *


def main():
    socket.setdefaulttimeout(0.5)
    startListening()
    findAvailableMachines()
    startHeartbeat()
    broadcastArrival()


if __name__ == '__main__':
    main()
