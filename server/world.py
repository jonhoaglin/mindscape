#!/usr/bin/python

import socket, os, sys, json, time, select
if __name__ == '__main__' and __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common

class world(object):
    def __init__(self, debug=False):
        self.sock = world_sock([socket.gethostname(), 5191], [socket.gethostname(), 5190], debug)
        if self.sock.open():
            while True:
                input = raw_input("World >> ")
                data = self.sock.receive(self.sock.sock)
                if data != []:
                    for row in data:
                        ping, message = self.sock.parse(row)
                        print ping, message
                if input != "exit":
                    self.sock.send(self.sock.sock, "message", input)
                else:
                    self.sock.close()

class world_sock(common.common_sock):
    def parse(self, data):
        ping = 0
        message = ""
        data = json.loads(data)
        if self.debug:
            print "Receive", data
        if data["type"] == "message":
            message += data["content"]
        elif data["type"] == "command":
            message += "player command"
        elif data["type"] == "log":
            message += "success"
        ping = time.time() - data["timestamp"]
        return ping, message

world(True)