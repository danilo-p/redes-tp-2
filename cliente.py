#!/usr/bin/python

import socket
import sys
import time


def main():
    if len(sys.argv) != 4:
        print("should receive just three parameteres with the server address, server port, and file name")
        return

    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    file_name = sys.argv[3]

    sock = None
    if ':' in server_address:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((server_address, server_port))

    time.sleep(10)

    try:
        sock.sendall((file_name + '\n').encode())

        full_message = ""
        while True:
            data = sock.recv(16)

            if not data:
                print('no more data from server')
                break

            message = data.decode()
            full_message += message

            if '\n' in message:
                break

        print('received "%s"' % full_message)
    finally:
        print('closing socket')
        sock.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
