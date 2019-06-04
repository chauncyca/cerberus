import socketserver
import json
import logging
import datetime

ERROR_LOG = "error.log"


class CerberusServer(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()

        message = self.data.decode()

        response = dict()

        try:
            decoded_msg = json.load(message)
            print(decoded_msg)


        except json.JSONDecodeError:
            logging.warning("Received invalid input: ", message)
        except:
            logging.exception("Failed to parse data: ", self.data)

        self.request.sendall(json.dump(response))

    def process(self, message):
        output = dict()

        

        return output

def run():
    logging.basicConfig(filename=ERROR_LOG)

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
            logging.exception("Unresolved exception, Juno Server failure.")
        server.server_close()
        stop_msg = "Server Stops at %s" % str(datetime.datetime.now())
        logging.warning(stop_msg)

if __name__ == "__main__":
    run()
