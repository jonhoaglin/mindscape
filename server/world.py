#!/usr/bin/python

import socket, os, sys, json, time, select
if __name__ == '__main__' and __package__ is None:
	sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common, csv

class world(object):
	def __init__(self, server_sock, debug=False):
		self.server_sock = server_sock
		self.sock = world_sock([socket.gethostname(), 5191], [socket.gethostname(), 5190], debug)
		self.database = world_database(self.server_sock.players, debug)
		if self.sock.open(""):
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

class world_database(object):
	def __init__(self, playerlist, debug=False):
		self.debug = debug
		for conn, player in playerlist.iteritems():
			if(os.path.isfile("/players/"+player)):
				print "Player file found, loading..."
				with open("/players/"+player) as csvfile:
					reader = csv.reader(csvfile, delimiter=",")
					for row in reader:
						print ",".join(row)
			else:
				print "Player file not found, creating..."
				with open("/players/"+player, "wb") as csvfile:
					writer = csv.writer(csvfile, delimiter=",")
					writer.writerow(1,1)



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