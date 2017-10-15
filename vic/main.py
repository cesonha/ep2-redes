from connections import *
from distributing import *
import sys
import time


def main():
    startListening()
    findAvailableMachines()
    startHeartbeat()
    broadcastArrival()

    if len(sys.argv) == 2:
        startLeaderThread(int(sys.argv[1]))

    if len(sys.argv) < 2:
        while True:
            time.sleep(1)

if __name__ == '__main__':
    main()
