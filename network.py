import threading
import socket
import gvars as gl

def getMyIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('8.8.8.8', 80))
    return sock.getsockname()[0]


def getLanPrefix(myIP):
    return myIP[0:myIP.rfind('.')]


def getMyVoteIP():
	myIP = getMyIP()
	lanPrefix = getLanPrefix(myIP)
	connectedIPs = [int(ip.split(".")[-1]) for ip in gl.connected_ips if ip != gl.leader_ip]
	voteSuffix = max(connectedIPs)
	print(connectedIPs)
	return (lanPrefix + "." + str(voteSuffix))