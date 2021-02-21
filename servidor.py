#!/usr/bin/python

import socket
import sys
import threading
import time


class ClientThread(threading.Thread):

    def __init__(self, connection, client_address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.client_address = client_address
        self.daemon = True

    def run(self):
        try:
            print('connection from', self.client_address)

            full_message = ""
            while True:
                data = self.connection.recv(16)

                if not data:
                    print('no more data from', self.client_address)
                    break

                message = data.decode()
                full_message += message

                if '\n' in message:
                    break

            print('received "%s"' % full_message)

            self.connection.sendall(full_message.encode())

        finally:
            self.connection.close()


class ServerThread(threading.Thread):

    def __init__(self, family, port):
        threading.Thread.__init__(self)
        self.family = family
        self.port = port
        self.daemon = True

    def run(self):
        sock = socket.socket(self.family, socket.SOCK_STREAM)
        sock.bind(('localhost', self.port))
        sock.listen(1)
        while True:
            print('waiting for a connection')
            connection, client_address = sock.accept()
            ClientThread(connection, client_address).start()


def main():
    if len(sys.argv) != 2:
        print("should receive just one parameter with the server port")
        return

    port = int(sys.argv[1])

    ServerThread(socket.AF_INET, port).start()

    ServerThread(socket.AF_INET6, port).start()

    import time
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
