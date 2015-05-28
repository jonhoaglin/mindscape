#!/usr/bin/python

import socket, sys, json, time
from thread import *

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
    sys.exit();

try:
    sock.bind(("0.0.0.0", 5190))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

sock.listen(5)
print "listening"

def clientthread(conn, addr):
    initmessage = "Connected to server"
    data = {"timestamp":time.time(),"message":initmessage}
    data = json.dumps(data)
    conn.send(data)
    while True:
        try:
            data = conn.recv(4096)
        except socket.error , msg:
            print 'Receive failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            conn.close()
            break
        try:
            conn.sendall(data)
        except socket.error , msg:
            print 'Send failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            conn.close()
            break
    conn.close()

while True:
    conn, addr = sock.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    start_new_thread(clientthread ,(conn, addr))

sock.close()