#!/usr/bin/python

import socket
import sys
import re


def is_file_name_valid(file_name):
    # [\x00-\x2D\x2F-\x7F] matches any ascii char except for "." (2E)
    return re.search(r"^([\x00-\x2D\x2F-\x7F]){0,11}\.[\x00-\x2D\x2F-\x7F]{3}$", file_name)


def main():
    if len(sys.argv) != 4:
        print("should receive just three parameteres with the server address, server port, and file name")
        return

    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    file_name = sys.argv[3]

    if not is_file_name_valid(file_name):
        print("invalid file name")
        return

    family = None
    if ':' in server_address:
        family = socket.AF_INET6
    else:
        family = socket.AF_INET
    sock = socket.socket(family, socket.SOCK_STREAM)

    sock.connect((server_address, server_port))

    f = open(file_name, "r")
    content = f.readline() + '\n'
    f.close()

    udp_port = 0
    try:
        f = open(file_name, "r")
        sock.sendall(content.encode())
        f.close()

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

        udp_port = int(full_message[0:-1])
    finally:
        print('closing socket')
        sock.close()

    sock = socket.socket(family, socket.SOCK_DGRAM)
    try:
        sock.sendto(content.encode(), (server_address, udp_port))
    finally:
        print('closing socket udp')
        sock.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
