from connections import *
import time


def main():
    startListening()
    findAvailableMachines()
    startHeartbeat()
    broadcastArrival()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
