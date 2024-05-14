import http.server
import logging
import threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class HealthcheckHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("OK".encode())

    def log_message(self, format, *args):
        logger.debug("Healthcheck from %s %s" %
                     (self.address_string(), format % args))


def _create_healthcheck_Server(port):
    logger.debug("Starting healthcheck server on port {}.".format(port))
    server = http.server.HTTPServer(('', port), HealthcheckHTTPRequestHandler)
    server.serve_forever()


def run_healthcheck_thread(port):
    hc_thread = threading.Thread(
        target=_create_healthcheck_Server, args=(int(port),), daemon=True)
    hc_thread.start()
