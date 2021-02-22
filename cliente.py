#!/usr/bin/env python3

import socket
import sys
import re
import os
from messages import HelloMessage, ConnectionMessage, InfoFileMessage, OkMessage, FimMessage, FileMessage, AckMessage


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

    f = open(file_name, "rb")
    file_content = f.read()
    f.close()

    file_size = os.path.getsize(file_name)

    family = None
    if ':' in server_address:
        family = socket.AF_INET6
    else:
        family = socket.AF_INET
    sock = socket.socket(family, socket.SOCK_STREAM)

    sock.connect((server_address, server_port))

    udp_sock = None
    try:
        sock.sendall(HelloMessage.serialize())

        data = sock.recv(ConnectionMessage.size())
        connection_message = ConnectionMessage.deserialize(data)
        udp_port = connection_message.udp_port

        sock.sendall(InfoFileMessage(file_name, file_size).serialize())

        data = sock.recv(OkMessage.size())
        OkMessage.deserialize(data)

        udp_sock = socket.socket(family, socket.SOCK_DGRAM)
        udp_sock.sendto(FileMessage(1, len(file_content), file_content).serialize(),
                        (server_address, udp_port))

        data = sock.recv(AckMessage.size())
        AckMessage.deserialize(data)

        data = sock.recv(FimMessage.size())
        FimMessage.deserialize(data)

        print('success')
    finally:
        sock.close()
        if udp_sock:
            udp_sock.close()


if __name__ == "__main__":
    print(sys.version)
    main()
