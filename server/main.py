#!/usr/bin/python

import socket, sys, json, time
from thread import *

class server_sock(object):
    def __init__(self, debug=False):
        self.debug = debug
        self.world = ""
        self.players = []
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg:
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            sys.exit();
        try:
            self.sock.bind(("0.0.0.0", 5190))
        except socket.error, msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

        self.sock.listen(5)
        print "Server Listening..."
        self.mainloop()

    def mainloop(self):
        while True:
            conn, addr = self.sock.accept()
            if addr[1] == 5191:
                print 'Connected with World on ' + addr[0] + ':' + str(addr[1])
                self.world = conn
                start_new_thread(self.world_thread ,(conn, addr))
            elif addr[1] == 5192 and self.world != "":
                print 'Connected with Player at ' + addr[0] + ':' + str(addr[1])
                self.players.append(conn)
                start_new_thread(self.player_thread ,(conn, addr))

    def player_thread(self, conn, addr):
        while True:
            check, data = self.receive(conn)
            if check:
                for row in data:
                    if not self.route(conn, row):
                        break
            else:
                break
        self.players.remove(conn)
        conn.close()

    def world_thread(self, conn, addr):
        while True:
            check, data = self.receive(conn)
            if check:
                for row in data:
                    if not self.route(conn, row):
                        break
            else:
                break
        self.world = ""
        conn.close()

    def send(self, conn, type, content):
        try:
            data = {"timestamp":time.time(), "type":type, "content":content}
            data = json.dumps(data)
            data = str(len(data))+data
            if self.debug:
                print "Send", data
            conn.sendall(data)
            return True
        except socket.error, msg:
            print 'Send failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False

    def receive(self, conn):
        try:
            length = None
            buffer = ""
            messages = []
            while True:
                data = conn.recv(4096)
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

    def route(self, conn, data):
        data = json.loads(data)
        if self.debug:
            print "Receive", data
        if data["type"] == "message":
            #echo message to all clients
            self.send(self.world, "message", data["content"])
            for player in self.players:
                self.send(player, "message", data["content"])
            return True
        elif data["type"] == "log":
            if data["content"] == "on":
                #send success log
                self.send(conn, "log", "success")
                return True
            elif data["content"] == "off":
                #send success log
                self.send(conn, "log", "success")
                #end connection
                return False
        elif data["type"] == "command":
            #send to world_sock
            self.send(self.world, "command", data["content"])
            return True
        elif data["type"] == "state":
            #send to all players
            for player in self.players:
                self.send(player, "message", data["content"])
            return True
        else:
            return False

server_sock(True)