#!/usr/bin/python

import socket, sys, json, time

class world(object):
    def __init__(self, debug=False):
        self.sock = world_sock(debug)
        if self.sock.open():
            while True:
                input = raw_input("World >> ")
                if input != "exit":
                    self.sock.send("message", input)
                else:
                    self.sock.close()
                ping, message = self.sock.parse()
                print int(ping), message

class world_sock(object):
    def __init__(self, debug=False):
        self.debug = debug
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            sys.exit()
        self.sock.bind((socket.gethostname(), 5191))
        self.sock.connect((socket.gethostname(), 5190))
        print "Connecting"

    def open(self):
        self.send("log", "on")
        i = 0
        ping, message = self.parse()
        while message != "success" or ping == 0:
            ping, message = self.parse()
            i += 1
            if i >= 5:
                return False
        return True

    def close(self):
        self.send("log", "off")
        ping, message = self.parse()
        while message != "success" or ping == 0:
            ping, message = self.parse()
        self.sock.close()
        sys.exit()

    def receive(self):
        try:
            length = None
            buffer = ""
            while True:
                data += conn.recv(4096)
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
                    message = buffer[:length]
                    return True, message
        except socket.error, msg:
            print 'Receive failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False, "error"

    def parse(self):
        try:
            data = json.loads(self.receive())
            if self.debug:
                print "Receive", data
            if data["type"] == "message":
                message = data["content"]
            elif data["type"] == "command":
                message = "player command"
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

world(True)