from http.server import BaseHTTPRequestHandler
from pprint import pprint
import json
import sys
import os

from tionDevices import *

class tionAPIserver(BaseHTTPRequestHandler):
  allowed_devices = []
  def __init__(self, request, client_addr, server):
    self.allowed_devices = self._get_allowed_devices()
    BaseHTTPRequestHandler.__init__(self, request, client_addr, server)

  def _get_allowed_devices(self):
    result = []
    for c in tion.__subclasses__():
      result.append(c.__name__)
    return result


  def _set_headers(self, code):
    self.send_response(code)
    self.send_header('Content-type', 'text/html')
    self.end_headers()

  def _send_response(self, code, message: dict, error = ""):
    self._set_headers(200)

    response = {
      "code": code,
      "error": error,
    }
    response = {**response, **message}
    response = json.dumps(response)
    self.log_message("Response is: " + response)
    self.wfile.write((response+"\n").encode())

  def _create_device(self, device_name: str):
    if device_name in self.allowed_devices:
      device = getattr(sys.modules[__name__], device_name)
    else:
      raise AttributeError
    return device
  
  def _send_bad_request(self, message: str):
    self._send_response(400, {"message": "request is {}".format(self.path)}, message)

  def do_GET(self):
    s = self.path.split("?")
    r = s[0].split("/")
    try:
    
      device_name = r[1]
      device_mac = r[2]
    except IndexError as e:      
      self._send_bad_request("Use requests like '/model/mac_addres'")
      return
    
    if len(s) > 1:
      p = s[1].split("&")
    
    try:
      device = self._create_device(device_name)
    except AttributeError as e:
      self._send_response(422,{}, "Device {} is not supported".format(device_name))
      return

    self.log_message(self.path)
    self.log_message("Process device {0} with mac {1}".format(device_name, device_mac) )
    self._send_response(200, device.get())

  def do_POST(self):
    '''Reads post request body'''
    content_len = int(self.headers.get('content-length', 0))
    post_body = self.rfile.read(content_len).decode()
    self._send_response(200, {"message": "WIP: received post request: {}".format(post_body)})

  def do_PUT(self):
    self.do_POST()
