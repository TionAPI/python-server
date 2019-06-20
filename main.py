from http.server import HTTPServer
from pprint import pprint
import json
import sys

from apiServer import tionAPIserver

PORT = 8000
ADDRESS = "127.0.0.1"

server_address = (ADDRESS, PORT)

handler = tionAPIserver
httpd = HTTPServer(server_address, tionAPIserver)
httpd.serve_forever()

