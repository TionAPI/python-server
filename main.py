from http.server import HTTPServer
from pprint import pprint
import json
import sys
import signal

from apiServer import TionApiServer

PORT = 8000
ADDRESS = "127.0.0.1"

server_address = (ADDRESS, PORT)

handler = TionApiServer


class limitedHttpServer(HTTPServer):
    def _signal_handler(self, signum, frame):
        raise Exception("Timed out!")

    def serve_forever(self):
        """Handle one request at a time until doomsday."""
        while 1:
            signal.signal(signal.SIGALRM, self._signal_handler)
            signal.alarm(4)
            try:
                self.handle_request()
            except Exception as e:
                print("Got exceptin {}".format(str(e)))
            finally:
                signal.alarm(0)


httpd = HTTPServer(server_address, TionApiServer)
httpd.serve_forever()
