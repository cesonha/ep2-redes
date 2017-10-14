from connections import *
from distributing import *
import sys


def main():
    startListening()
    findAvailableMachines()
    startHeartbeat()
    broadcastArrival()

    if len(sys.argv) == 2:
        startLeaderThread(int(sys.argv[1]))


if __name__ == '__main__':
    main()
