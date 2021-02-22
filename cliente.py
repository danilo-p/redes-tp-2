#!/usr/bin/env python3

import socket
import sys
import re
import os
import threading
from messages import HelloMessage, ConnectionMessage, InfoFileMessage, \
    OkMessage, FimMessage, FileMessage, AckMessage

CHUNK_SIZE_BYTES = 1000
TCP_SOCKET_TIMEOUT = 5
SLIDING_WINDOW_SIZE = 10


class ChunkSenderThread(threading.Thread):

    def __init__(self, udp_sock, server_address, udp_port, sliding_window, file_content, file_size):
        threading.Thread.__init__(self)
        self.udp_sock = udp_sock
        self.server_address = server_address
        self.udp_port = udp_port
        self.sliding_window = sliding_window
        self.file_content = file_content
        self.file_size = file_size
        self.daemon = True

    def run(self):
        while self.sliding_window.any_remaining_chunk():
            try:
                next_n_seq = self.sliding_window.next_chunk_n_seq()
                if next_n_seq == -1:
                    continue

                print(f'sending chunk {next_n_seq}')

                next_chunk_index = next_n_seq * CHUNK_SIZE_BYTES
                chunk_end = min(next_chunk_index +
                                CHUNK_SIZE_BYTES, self.file_size)
                chunk_size = chunk_end - next_chunk_index
                chunk_payload = self.file_content[next_chunk_index:chunk_end]
                self.udp_sock.sendto(FileMessage(next_n_seq, chunk_size, chunk_payload).serialize(),
                                     (self.server_address, self.udp_port))

                self.sliding_window.increment_last_chunk_sent()
            except Exception as e:
                print("unknown error when sending chunk")
                print(e)
                pass


class AckReceiverThread(threading.Thread):

    def __init__(self, sock, sliding_window):
        threading.Thread.__init__(self)
        self.sock = sock
        self.sliding_window = sliding_window
        self.daemon = True

    def run(self):
        while self.sliding_window.any_remaining_ack():
            try:
                data = self.sock.recv(AckMessage.size())
                ack_message = AckMessage.deserialize(data)

                if ack_message.n_seq == self.sliding_window.last_ack_recvd + 1:
                    print(f'chunk acknowledged {ack_message.n_seq}')
                    self.sliding_window.increment_last_ack_recvd()
                    continue

                print(f'discarding ack {ack_message.n_seq}')
                self.sliding_window.reset_last_chunk_sent()
            except Exception as e:
                print("unknown error when receiving ack")
                print(e)
                pass


class SlidingWindow:

    def __init__(self, size):
        self.last_ack_recvd = -1
        self.last_ack_recvd_lock = threading.Lock()
        self.last_chunk_sent = -1
        self.last_chunk_sent_lock = threading.Lock()
        self.size = size

    def increment_last_ack_recvd(self):
        self.last_ack_recvd_lock.acquire()
        try:
            self.last_ack_recvd += 1
        finally:
            self.last_ack_recvd_lock.release()

    def increment_last_chunk_sent(self):
        self.last_chunk_sent_lock.acquire()
        try:
            self.last_chunk_sent += 1
        finally:
            self.last_chunk_sent_lock.release()

    def reset_last_chunk_sent(self):
        self.last_chunk_sent_lock.acquire()
        self.last_ack_recvd_lock.acquire()
        try:
            if self.last_chunk_sent != -1:
                self.last_chunk_sent = self.last_ack_recvd + 1
        finally:
            self.last_ack_recvd_lock.release()
            self.last_chunk_sent_lock.release()

    def any_remaining_chunk(self):
        self.last_chunk_sent_lock.acquire()
        result = False
        try:
            result = self.last_chunk_sent < self.size
        finally:
            self.last_chunk_sent_lock.release()
        return result

    def next_chunk_n_seq(self):
        self.last_chunk_sent_lock.acquire()
        self.last_ack_recvd_lock.acquire()
        result = -1
        try:
            if self.last_chunk_sent == -1 \
                or (self.last_chunk_sent < self.size
                    and self.last_chunk_sent - self.last_ack_recvd < SLIDING_WINDOW_SIZE):
                result = self.last_chunk_sent + 1
        finally:
            self.last_ack_recvd_lock.release()
            self.last_chunk_sent_lock.release()
        return result

    def any_remaining_ack(self):
        self.last_ack_recvd_lock.acquire()
        result = False
        try:
            result = self.last_ack_recvd < self.size
        finally:
            self.last_ack_recvd_lock.release()
        return result


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

    sock.settimeout(TCP_SOCKET_TIMEOUT)

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

        size = int(file_size / CHUNK_SIZE_BYTES)
        sliding_window = SlidingWindow(size)

        cst = ChunkSenderThread(
            udp_sock, server_address, udp_port, sliding_window, file_content, file_size)
        art = AckReceiverThread(sock, sliding_window)

        print('starting transfer')

        cst.start()
        art.start()

        cst.join()
        art.join()

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
