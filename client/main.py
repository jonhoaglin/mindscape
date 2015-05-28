#!/usr/bin/python

import socket, sys, json, time

class player(object):
    def __init__(self, debug=False):
        self.sock = player_sock(debug)
        if self.sock.open():
            while True:
                input = raw_input(">>")
                if input != "exit":
                    self.sock.send("message", input)
                else:
                    self.sock.close()
                ping, message = self.sock.receive()
                print int(ping), message

class player_sock(object):
    def __init__(self, debug=False):
        self.debug = debug
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            sys.exit()
        self.sock.connect((socket.gethostname(), 5190))
        print "Connecting"

    def open(self):
        self.send("log", "on")
        i = 0
        ping, message = self.receive()
        while message != "success" or ping == 0:
            ping, message = self.receive()
            i += 1
            if i >= 5:
                return False
        return True

    def close(self):
        self.send("log", "off")
        ping, message = self.receive()
        while message != "success" or ping == 0:
            ping, message = self.receive()
        self.sock.close()
        sys.exit()

    def receive(self):
        try:
            data = json.loads(self.sock.recv(4096))
            if self.debug:
                print "Receive", data
            if data["type"] == "message":
                message = data["content"]
            elif data["type"] == "state":
                message = "World state"
            elif data["type"] == "log":
                message = "success"
            ping = time.time() - data["timestamp"]
        except socket.error , msg:
            message = 'Receive failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            ping = 0
        return ping, message

    def send(self, type, data):
        data = {"timestamp":time.time(), "type":type, "content":data}
        if self.debug:
            print "Send", data
        data = json.dumps(data)
        try:
            self.sock.sendall(data)
            return True
        except socket.error , msg:
            print 'Send failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False

player(False)