#!/usr/bin/python

import socket
import sys
import threading


class ClientThread(threading.Thread):

    def __init__(self, connection, client_address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.client_address = client_address

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


def main():
    if len(sys.argv) != 2:
        print("should receive just one parameter with the server port")
        return

    port = int(sys.argv[1])

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind(('localhost', port))

    sock.listen(1)

    while True:
        print('waiting for a connection')
        connection, client_address = sock.accept()
        ClientThread(connection, client_address).start()


if __name__ == "__main__":
    # execute only if run as a script
    main()
