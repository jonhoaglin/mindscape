#!/usr/bin/python

import socket, sys, json, time

class player(object):
    def __init__(self, debug=False):
        self.sock = player_sock(debug)
        if self.sock.open():
            while True:
                input = raw_input("Player >> ")
                if input != "exit":
                    self.sock.send("message", input)
                else:
                    self.sock.close()
                check, data = self.sock.receive()
                if check:
                    self.sock.parse(data)
                else:
                    break

class player_sock(object):
    def __init__(self, debug=False):
        self.debug = debug
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            sys.exit()
        try:
            self.sock.bind((socket.gethostname(), 5192))
        except socket.error, msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        try:
            self.sock.connect((socket.gethostname(), 5190))
        except socket.error, msg:
            print 'Connect failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        print "Connected"

    def open(self):
        self.send("log", "on")
        i = 0
        check, data = self.receive()
        ping, message = self.parse(data)
        while message != "success" or ping == 0:
            check, data = self.receive()
            ping, message = self.parse(data)
            i += 1
            if i >= 5:
                return False
        return True

    def close(self):
        self.send("log", "off")
        i = 0
        check, data = self.receive()
        ping, message = self.parse(data)
        while message != "success" or ping == 0:
            check, data = self.receive()
            ping, message = self.parse(data)
            i += 1
            if i >= 5:
                break
        self.sock.close()
        sys.exit()

    def receive(self):
        try:
            length = None
            buffer = ""
            messages = []
            while True:
                data = self.sock.recv(4096)
                if not data:
                    break
                buffer += data
                while True:
                    if length is None:
                        if '{' not in buffer:
                            break
                        length_str, ignored, buffer = buffer.partition('{')
                        length = int(length_str)
                    if len(buffer)+1 < length:
                        break
                    messages.append("{"+buffer[:length-1])
                    buffer = buffer[length-1:]
            return True, messages
        except socket.error, msg:
            print 'Receive failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False, "error"

    def parse(self, dataset):
        ping = 0
        message = ""
        for row in dataset:
            data = json.loads(row)
            if self.debug:
                print "Receive", data
            if data["type"] == "message":
                message = data["content"]
            elif data["type"] == "state":
                message = "World state"
            elif data["type"] == "log":
                message = "success"
            ping = time.time() - data["timestamp"]
            print ping, message
        return ping, message

    def send(self, type, data):
        data = {"timestamp":time.time(), "type":type, "content":data}
        data = json.dumps(data)
        data = str(len(data))+data
        if self.debug:
            print "Send", data
        try:
            self.sock.sendall(data)
            return True
        except socket.error , msg:
            print 'Send failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False

player(False)