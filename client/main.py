#!/usr/bin/python

import socket, sys, json, time, select

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
                data = self.sock.receive()
                if data != []:
                    for row in data:
                        ping, message = self.sock.parse(row)
                        print ping, message

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
        while i < 5:
            data = self.receive()
            if data != []:
                for row in data:
                    ping, message = self.parse(row)
                    if message != "success":
                        print ping, message
                        i += 1
                    else:
                        return True
        return False

    def close(self):
        self.send("log", "off")
        i = 0
        while i < 5:
            data = self.receive()
            if data != []:
                for row in data:
                    ping, message = self.parse(row)
                    if message != "success":
                        print ping, message
                        i += 1
                    else:
                        i = 5
                        break
        self.sock.close()
        sys.exit()

    def receive(self):
        length = None
        buffer = ""
        messages = []
        while True:
            inputready, o, e = select.select([self.sock], [], [])
            for input in inputready:
                try:
                    data = input.recv(4096)
                except socket.error, msg:
                    print 'Receive failed. Error : ', msg
                    return []
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
                    length = None
            else:
                break
        return messages

    def parse(self, data):
        ping = 0
        message = ""
        data = json.loads(data)
        if self.debug:
            print "Receive", data
        if data["type"] == "message":
            message = data["content"]
        elif data["type"] == "state":
            message = "World state"
        elif data["type"] == "log":
            message = "success"
        ping = time.time() - data["timestamp"]
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