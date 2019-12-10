#!/usr/bin/python
#from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from http.server import BaseHTTPRequestHandler,HTTPServer

#This class will handles any incoming request from
#the browser 
response = "Hello World !".encode()
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the GET requests
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		# Send the html message
		self.wfile.write(response)
		return


class healthCheck():

	def __init__(self,port):
		self.port = port

	def start_HC(self):
		try:
			#Create a web server and define the handler to manage the
			#incoming request
			server = HTTPServer(('', self.port), myHandler)
			print ('Started httpserver on port ' + str(self.port))
			#Wait forever for incoming htto requests
			server.serve_forever()

		except KeyboardInterrupt:
			server.socket.close()



if __name__ == '__main__':
	hc = healthCheck(8888)
	hc.start_HC()
