import sys
import logging
import gvars as gl
from follower import *
from leader import *
from math import *
from network import *


def main():
    my_ip = getMyIP()

    with gl.lock:
        gl.connected_ips.append(my_ip)

    if "-n" in sys.argv:
        idx = sys.argv.index("-n")
        with gl.lock:
            gl.p = int(sys.argv[idx + 1])
            gl.state = "LEADER"
            gl.intervals = [(2 + i * gl.test_range, min(floor(sqrt(gl.p)) + 1, 2 + (i+1) * gl.test_range)) for i in range(ceil((sqrt(gl.p) - 1) / gl.test_range))]
            gl.calculated_intervals = list(gl.intervals)
            gl.original_interval_count = len(gl.intervals)
            gl.start = 2
            gl.leader_ip = my_ip 

    if "-d" in sys.argv:
        with gl.lock:
            gl.debug = True
            gl.logger = logging.getLogger("EP2")
            fh = logging.FileHandler("general.log")
            gl.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            gl.logger.addHandler(fh)

    startFollowerThread()
    startLeaderThread()

    while True:
        time.sleep(1)
        with gl.lock:
            if gl.done and (gl.state != "LEADER" or gl.broadcasted_count >= len(gl.connected_ips) - 1):
                print(gl.p, "is", "not prime" if gl.isComposite else "prime")
                break


if __name__ == "__main__":
    main()

