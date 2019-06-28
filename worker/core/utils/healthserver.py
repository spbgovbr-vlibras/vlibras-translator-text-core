import logging
import socketserver

class HealthTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.send("200".encode())

def start_server():
    logger = logging.getLogger(__name__)

    try:
        address = ("127.0.0.1", 8000)
        logger.info("Starting health server on {0}:{1}".format(*address))
        with socketserver.TCPServer(address, HealthTCPHandler) as server:
            server.serve_forever()

    except OSError:
        logger.exception("An error occurred on the health server")
