import http.server
import logging
import threading


class HealthcheckHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.__logger = logging.getLogger(self.__class__.__name__)
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("OK".encode())

    def log_message(self, format, *args):
        self.__logger.debug("Healthcheck from %s %s" %
                            (self.address_string(), format % args))


def _create_healthcheck_Server(port):
    logger = logging.getLogger(__name__)
    logger.debug("Starting healthcheck server on port {}.".format(port))
    server = http.server.HTTPServer(('', port), HealthcheckHTTPRequestHandler)
    server.serve_forever()


def run_healthcheck_thread(port):
    hc_thread = threading.Thread(
        target=_create_healthcheck_Server, args=(port,), daemon=True)
    hc_thread.start()
