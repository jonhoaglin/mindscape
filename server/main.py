#!/usr/bin/python

import socket, os, sys, json, time, select
if __name__ == '__main__' and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common
from thread import *

class server_sock(common.common_sock):
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
            data = self.receive(conn)
            if data != []:
                for row in data:
                    self.route(conn, row)
        self.players.remove(conn)
        conn.close()

    def world_thread(self, conn, addr):
        while True:
            data = self.receive(conn)
            if data != []:
                for row in data:
                    self.route(conn, row)
        self.world = ""
        conn.close()

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

server=server_sock(["0.0.0.0", 5190], [socket.gethostname(), 5192], True, False, 5191)
server.mainloop()