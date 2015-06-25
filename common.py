#!/usr/bin/python

import socket, sys, json, time, select

class common_sock(object):
    def __init__(self, localip, remoteip, debug=False, client=True, worldport=5191):
        self.debug = debug
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            sys.exit()
        try:
            self.sock.bind((localip[0], localip[1]))
        except socket.error, msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        if client:
            try:
                self.sock.connect((remoteip[0], remoteip[1]))
            except socket.error, msg:
                print 'Connect failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                sys.exit()
            print "Client Connected"
        else:
            self.sock.listen(5)
            print "Server Listening..."
            self.world = ""
            self.players = {}

    def open(self, username):
        self.send(self.sock, "logon", username)
        i = 0
        while i < 5:
            data = self.receive(self.sock)
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
        self.send(self.sock, "logoff", "off")
        i = 0
        while i < 5:
            data = self.receive(self.sock)
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

    def receive(self, conn):
        length = None
        buffer = ""
        messages = []
        while True:
            inputready, o, e = select.select([conn], [], [], 0)
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

    def send(self, conn, type, data):
        data = {"timestamp":time.time(), "type":type, "content":data}
        data = json.dumps(data)
        data = str(len(data))+data
        if self.debug:
            print "Send", data
        try:
            conn.sendall(data)
            return True
        except socket.error , msg:
            print 'Send failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False