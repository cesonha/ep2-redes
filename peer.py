import socket
import sys
import time
from thread import *
 
HOST = ""   # Symbolic name meaning all available interfaces
PORT = 5013 # Server socket port
leader = True
if (len(sys.argv) > 1):
    leader = False
    PORT = 5014

peers = {}
numbers = {}
ELECTION_INTERVAL = 3000
sendMsg = False
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Socket created")
 
#Bind server socket to local host and port
try:
    serverSocket.bind((HOST, PORT))
except socket.error as msg:
    print("Bind failed. Error Code : {} Message {}".format(msg[0], msg[1]))
    sys.exit()
print("Socket bind complete")
 
#Start listening on socket
serverSocket.listen(10)
print("Socket now listening")
 
# listen and  create communication threads
def listenerThread():
    while True:
        #wait to accept a connection - blocking call
        conn, addr = serverSocket.accept()

        print 'Connected with ' + addr[0] + ':' + str(addr[1])
         
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(communicationThread ,(conn,))
    serverSocket.close()

# thread to handle peers that started the communication
def communicationThread(conn):
    #infinite loop so that function do not terminate and thread do not end.
    while True:
        #Receiving from client        
        data = conn.recv(1024)
        if not data: 
            break
        if ("any" in data):
            conn.sendall("any")
        else:
            print("recebi: " + data)
            conn.sendall("OK " + data)
    #came out of loop
    print("terminou comm")
    conn.close()

# thread to actively start communication with any of the peers
def clientThread(clientSocket, message, messageParams):
    clientSocket.send(message)
    global sendMsg
    while True:
        #Receiving from client
        data = clientSocket.recv(1024)
        if not data: 
            break
        # print("recebi " + data)
        if (sendMsg):
            clientSocket.sendall("Vai toma")
            print("mandei vai toma")
            sendMsg = False
        clientSocket.sendall("any")
        if ("OK" in data):
            break
    #came out of loop
    print("terminou comm")
    clientSocket.close()

# main processing thread
def computingThread():
    global sendMsg
    while True:
        time.sleep(5)
        sendMsg = True
        if (leader == False):
            connectTo("127.0.0.1")
        print("computingThread - processando")

 
def connectTo(ip):
    clientSocket.connect((ip, 5013))
    message = "Teste"
    messageParams = "test" 
    start_new_thread(clientThread, (clientSocket, message, messageParams))


start_new_thread(computingThread, ())

if (leader): 
    start_new_thread(listenerThread, ())
else :
    clientSocket.bind((HOST, 2187))

while True:
    True == True
