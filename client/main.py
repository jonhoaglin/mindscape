#!/usr/bin/python

import socket, sys, json, time

class client_receive(object):
    def __init__(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            sys.exit();
        self.sock.connect((socket.gethostname(), 5190))
        print "Connecting"
        self.control = ""
        self.mainloop()

    def mainloop(self):
        while self.control != "exit":
            message = self.receive()
            print message
            input = raw_input(">>")
            if input == "exit":
                self.control = "exit"
            else:
                self.send(input)
        self.sock.close()

    def receive(self):
        try:
            message = json.loads(self.sock.recv(4096))
        except socket.error , msg:
            print 'Receive failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        ping = time.time() - message["timestamp"]
        return ping, message["message"]

    def send(self, data):
        data = {"timestamp":time.time(),"message":data}
        data = json.dumps(data)
        try:
            self.sock.sendall(data)
        except socket.error , msg:
            print 'Send failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]

client_receive()