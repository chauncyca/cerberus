import datetime
import logging
import socketserver
import threading
import time

from . import perform_actions

ERROR_LOG = "error.log"
UNKNOWN_COUNT = 0
STATE = -1


class CerberusServer(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()

        response = dict()

        try:
            response = process(self.data.decode())
        except:
            logging.exception("Failed to parse data: ", self.data)

        self.request.sendall(response)


def process(message):
    output = bin()

    if message == "GET_IMAGE":
        output = perform_actions.get_picture().encode()
    elif message == "GET_LOCK_STATE":
        output = STATE.encode()
    return output


def check_state():
    state = perform_actions.get_lock_state()

    global STATE
    global UNKNOWN_COUNT
    if state >= 0:
        STATE = state
        UNKNOWN_COUNT = 0
    elif UNKNOWN_COUNT < 3:
        UNKNOWN_COUNT = UNKNOWN_COUNT + 1
    else:
        STATE = state
        if UNKNOWN_COUNT % 60:
            logging.warning("State has remained unknown for %s seconds" % UNKNOWN_COUNT)
        UNKNOWN_COUNT = UNKNOWN_COUNT + 1

    threading.Timer(1, check_state()).start()


def run():
    logging.basicConfig(filename=ERROR_LOG)

    check_state()

    host, port = "localhost", 5555

    # Create the server, binding to localhost on port 5555
    with socketserver.TCPServer((host, port), CerberusServer) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        try:
            server.serve_forever()
            # If we intentionally disable the server, do nothing.
        except KeyboardInterrupt:
            pass
        # If the server crashes suddenly, log it.
        except:
            logging.exception("Unresolved exception, Cerberus Server failure.")
        server.server_close()
        stop_msg = "Server Stops at %s" % str(datetime.datetime.now())
        logging.warning(stop_msg)


if __name__ == "__main__":
    run()
