#!/usr/bin/python

import socket, sys, json, time
from thread import *

class server_sock(object):
    def __init__(self, debug=False):
        self.debug = debug
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
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
            self.players.append(conn)
            start_new_thread(self.player_thread ,(conn, addr))

    def player_thread(self, conn, addr):
        while True:
            check, data = self.receive(conn)
            if check:
                if not self.route(conn, data):
                    break
            else:
                break
        self.players.remove(conn)
        conn.close()

    def send(self, conn, type, content):
        try:
            data = {"timestamp":time.time(), "type":type, "content":content}
            if self.debug:
                print "Send", data
            data = json.dumps(data)
            conn.sendall(data)
            return True
        except socket.error, msg:
            print 'Send failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False

    def receive(self, conn):
        try:
            data = conn.recv(4096)
            return True, data
        except socket.error, msg:
            print 'Receive failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False, "error"

    def route(self, conn, data):
        data = json.loads(data)
        if self.debug:
            print "Receive", data
        if data["type"] == "message":
            #echo message to all clients
            #self.send(world, "message", data["content"])
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
            print data["content"]
            return True
        elif data["type"] == "state":
            #send to all players
            for player in self.players:
                self.send(player, "message", data["content"])
            return True
        else:
            return False

server_sock(True)