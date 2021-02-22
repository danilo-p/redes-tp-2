#!/usr/bin/env python3

import socket
import sys
import threading
import time
from messages import HelloMessage, ConnectionMessage, InfoFileMessage


class ClientDataThread(threading.Thread):

    def __init__(self, family, udp_port):
        threading.Thread.__init__(self)
        self.family = family
        self.udp_port = udp_port
        self.daemon = True

    def run(self):
        sock = socket.socket(self.family, socket.SOCK_DGRAM)
        sock.bind(('localhost', self.udp_port))
        try:
            full_message = ""
            while True:
                data = sock.recv(16)

                if not data:
                    print('no more data in ', self.udp_port)
                    break

                message = data.decode()
                full_message += message

                if '\n' in message:
                    break

            print('udp received "%s"' % full_message)
        finally:
            sock.close()


class ClientControlThread(threading.Thread):

    def __init__(self, connection, client_address, udp_port):
        threading.Thread.__init__(self)
        self.connection = connection
        self.client_address = client_address
        self.udp_port = udp_port
        self.daemon = True

    def run(self):
        try:
            print('connection from', self.client_address)

            data = self.connection.recv(HelloMessage.size())
            HelloMessage.deserialize(data)

            self.connection.sendall(
                ConnectionMessage(self.udp_port).serialize())

            data = self.connection.recv(InfoFileMessage.size())
            info_file_message = InfoFileMessage.deserialize(data)
            print(info_file_message.file_name)
            print(info_file_message.file_size)

            # full_message = ""
            # while True:
            #     data = self.connection.recv(16)

            #     if not data:
            #         print('no more data from', self.client_address)
            #         break

            #     message = data.decode()
            #     full_message += message

            #     if '\n' in message:
            #         break

            # print('received "%s"' % full_message)

            # self.connection.sendall((str(self.udp_port) + '\n').encode())

        finally:
            self.connection.close()


class ClientThread(threading.Thread):

    def __init__(self, family, connection, client_address, udp_port):
        threading.Thread.__init__(self)
        self.family = family
        self.connection = connection
        self.client_address = client_address
        self.udp_port = udp_port
        self.daemon = True

    def run(self):
        ClientControlThread(
            self.connection, self.client_address, self.udp_port).start()
        ClientDataThread(self.family, self.udp_port).start()


class ServerThread(threading.Thread):

    def __init__(self, family, port, counter):
        threading.Thread.__init__(self)
        self.family = family
        self.port = port
        self.counter = counter
        self.daemon = True

    def run(self):
        sock = socket.socket(self.family, socket.SOCK_STREAM)
        sock.bind(('localhost', self.port))
        sock.listen(1)
        while True:
            print('waiting for a connection')
            connection, client_address = sock.accept()
            ClientThread(self.family, connection, client_address,
                         self.port + self.counter.increment()).start()


class Counter:

    def __init__(self):
        self.lock = threading.Lock()
        self.value = 0

    def increment(self):
        self.lock.acquire()
        try:
            if self.value == 1000:
                self.value = 0
            self.value = self.value + 1
        finally:
            self.lock.release()
        return self.value


def main():
    if len(sys.argv) != 2:
        print("should receive just one parameter with the server port")
        return

    port = int(sys.argv[1])

    counter = Counter()

    ServerThread(socket.AF_INET, port, counter).start()

    ServerThread(socket.AF_INET6, port, counter).start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    print(sys.version)
    main()
