from http.server import BaseHTTPRequestHandler
from pprint import pprint
import json
import sys
import os
import time

from tionDevices import *

class tionAPIserver(BaseHTTPRequestHandler):
  allowed_devices = []
  cache_valid = 600 # seconds
  cache_expire = 0
  cache_response = {}

  @classmethod
  def _is_cache_valid(cls, ts) -> bool:
    return (not cls.cache_expire < ts)

  @classmethod
  def _invalidate_cache(cls):
    cls.cache_expire = 0

  @classmethod
  def _get_cache(cls) -> dict:
    return cls.cache_response

  @classmethod
  def _set_cache(cls, response, ts):
    cls.cache_expire = ts + cls.cache_valid
    cls.cache_response = dict(response)
    cls.cache_response["code"] = 304
    cls.cache_response["last_update"] = ts

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
    self.send_header('Content-type', 'application/json')
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
      device = getattr(sys.modules[__name__], device_name)()
    else:
      raise AttributeError
    return device
  
  def _send_bad_request(self, message: str):
    self._send_response(400, {"message": "request is {}".format(self.path)}, message)

  def _get_device_from_request(self, path:str) -> str:

    s = path.split("?")
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

    self.log_message(path)
    self.log_message("Process device {0} with mac {1}".format(device_name, device_mac) )

    return device_mac, device

  def _try_several_times(self, times: int, function, *args):
    i = 0
    done = False
    exception = None
    while i < times:
      i = i + 1
      try:
        result = function(*args)
        done = True
        break
      except Exception as e:
        exception = e
    if not done:
      raise exception

    return result

  def do_GET(self):
    now = time.time();
    if (self._is_cache_valid(now)):
      try:
        device_mac, device = self._get_device_from_request(self.path)
        response = self._try_several_times(3, device.get, device_mac)
      except Exception as e:
        self._invalidate_cache() #drop cache
        self._send_response(400, {}, str(e))
      else:
        self._set_cache(response, now)
        self._send_response(response["code"], response)
      finally:
        device._btle.disconnect()
    else:
      response = self._get_cache()
      self._send_response(response["code"], response)

  def do_POST(self):
    content_len = int(self.headers.get('content-length', 0))
    post_body = self.rfile.read(content_len).decode()
    device_mac, device = self._get_device_from_request(self.path)

    i = 0
    done = False
    exception = None
    self.log_message(post_body)
    self._invalidate_cache() #drop cache
    try:
      self._try_several_times(3, device.set, device_mac, json.loads(post_body))
    except Exception as e:
      self._send_response(400, {}, str(e))
    else:
      self._send_response(200, {"message": "Data {} were sent to device {}".format(post_body, device_mac)})
    finally:
      device._btle.disconnect()

  def do_PUT(self):
    self.do_POST()
