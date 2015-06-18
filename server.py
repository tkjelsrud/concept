import http.server
import socketserver
import pprint
import json
from json import JSONEncoder
import sys

from concept import *

PORT = 8000

class MyEncoder(JSONEncoder):
	def default(self, o):
		return o.__dict__   

class Memory:
	spaces = [Space()]

class Handler(http.server.SimpleHTTPRequestHandler):
	def __init__(self, request, client_address, server):
		#self.request = request
		#self.client = client_address
		#self.server = server
		self.responded = False
		http.server.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)
		
		
	def respond(self, content):
		self.send_response(200)
		self.send_header("Content-type", "application/json")
		self.end_headers()
		self.wfile.write(bytes(content, 'UTF-8'))
		
		self.responded = True
	
	def do_GET(self):	
		try:
			if(self.path.startswith("/service/")):
				ar = self.path.split("?")
				pt = ar[0].split("/")
				
				if(len(pt) == 4 and pt[2] == "space"):
					# Space related functions 
					sId = int(pt[3])
					if sId >= 0 and sId < len(Memory.spaces):
						print(str(Memory.spaces[sId].__dict__))
						self.respond(MyEncoder().encode(Memory.spaces[sId]))
				
				if(len(pt) == 6 and pt[2] == "space" and pt[4] == "concept"):	
					sId = int(pt[3])
					cId = int(pt[5])
					if sId >= 0 and sId < len(Memory.spaces):
						c = Memory.spaces[sId].getConceptById(cId)
						if c:
							self.respond(MyEncoder().encode(c))
			
			if not self.responded:
				# Default response
				http.server.SimpleHTTPRequestHandler.do_GET(self)
		
		except:
			print("Unexpected error:" + str(sys.exc_info()[0]))
			raise

httpd = socketserver.TCPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()