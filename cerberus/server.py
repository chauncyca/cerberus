import datetime
import logging
import threading
try:
    import socketserver
except:
    import SocketServer

from . import perform_actions

DEBUG = False
ERROR_LOG = "error.log"
UNKNOWN_COUNT = 0
STATE = -1


class CerberusServer(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()

        response = "Data"

        try:
            global DEBUG
            if not DEBUG:
                response = process(self.data.decode())
        except:
            logging.exception("Failed to parse data: ", self.data)

        self.request.sendall(response.encode())


class TimerThread():
    def __init__(self, t, hFunction):
        self.t = t
        self.hFunction = hFunction
        self.thread = threading.Timer(self.t, self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = threading.Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


def process(message):
    output = None

    if message == "GET_IMAGE":
        output = perform_actions.get_picture()
    elif message == "GET_LOCK_STATE":
        global STATE
        output = STATE
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


def run():
    logging.basicConfig(filename=ERROR_LOG)

    global DEBUG
    if not DEBUG:
        timer = TimerThread(1, check_state())
        timer.start()

    host, port = "localhost", 55555

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
