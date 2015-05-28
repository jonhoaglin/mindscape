#!/usr/bin/python

import socket, sys

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
    sys.exit();
sock.connect((socket.gethostname(), 5190))
print "connected"

data = ""
while data != "exit":
    try:
        print sock.recv(4096)
    except socket.error , msg:
        print 'Receive failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    data = raw_input(">>")
    try:
        sock.sendall(str(data))
    except socket.error , msg:
        print 'Send failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
sock.close()