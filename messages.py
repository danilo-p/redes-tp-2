BYTEORDER = "big"


class MessageTypeHelper:
    SIZE = 2

    @staticmethod
    def serialize(message_type):
        return message_type.to_bytes(MessageTypeHelper.SIZE, byteorder=BYTEORDER)

    @staticmethod
    def deserialize(data):
        return int.from_bytes(data, byteorder=BYTEORDER)


class UdpPortHelper:
    SIZE = 4

    @staticmethod
    def serialize(udp_port):
        return udp_port.to_bytes(UdpPortHelper.SIZE, byteorder=BYTEORDER)

    @staticmethod
    def deserialize(data):
        return int.from_bytes(data, byteorder=BYTEORDER)


class FileNameHelper:
    MAX_FILE_NAME_SIZE = 15
    SIZE = 15
    PADDING_CHAR = '.'

    @staticmethod
    def serialize(file_name):
        file_name_len = len(file_name)
        if file_name_len < FileNameHelper.MAX_FILE_NAME_SIZE:
            padding = FileNameHelper.PADDING_CHAR * \
                (FileNameHelper.MAX_FILE_NAME_SIZE - file_name_len)
            file_name = padding + file_name
        return file_name.encode()

    @staticmethod
    def deserialize(data):
        file_name = data.decode()
        while file_name[0] == FileNameHelper.PADDING_CHAR:
            file_name = file_name[1:]
        return file_name


class FileSizeHelper:
    SIZE = 8

    @staticmethod
    def serialize(file_size):
        return file_size.to_bytes(FileSizeHelper.SIZE, byteorder=BYTEORDER)

    @staticmethod
    def deserialize(data):
        return int.from_bytes(data, byteorder=BYTEORDER)


class NSeqHelper:
    SIZE = 4

    @staticmethod
    def serialize(file_size):
        return file_size.to_bytes(NSeqHelper.SIZE, byteorder=BYTEORDER)

    @staticmethod
    def deserialize(data):
        return int.from_bytes(data, byteorder=BYTEORDER)


class PayloadSizeHelper:
    SIZE = 2

    @staticmethod
    def serialize(file_size):
        return file_size.to_bytes(PayloadSizeHelper.SIZE, byteorder=BYTEORDER)

    @staticmethod
    def deserialize(data):
        return int.from_bytes(data, byteorder=BYTEORDER)


class HelloMessage:
    MESSAGE_TYPE = 1

    @staticmethod
    def deserialize(data):
        message_type = MessageTypeHelper.deserialize(data)
        if message_type != HelloMessage.MESSAGE_TYPE:
            raise Exception("wrong type for HELLO message")

    @staticmethod
    def size():
        return MessageTypeHelper.SIZE

    @staticmethod
    def serialize():
        return MessageTypeHelper.serialize(HelloMessage.MESSAGE_TYPE)


class ConnectionMessage:
    MESSAGE_TYPE = 2

    def __init__(self, udp_port):
        self.udp_port = udp_port

    @staticmethod
    def deserialize(data):
        message_type_bytes = data[0:MessageTypeHelper.SIZE]
        message_type = MessageTypeHelper.deserialize(message_type_bytes)

        udp_port_bytes = data[MessageTypeHelper.SIZE:(
            MessageTypeHelper.SIZE + UdpPortHelper.SIZE)]
        udp_port = UdpPortHelper.deserialize(udp_port_bytes)

        if message_type != ConnectionMessage.MESSAGE_TYPE:
            raise Exception("wrong type for CONNECTION message")

        return ConnectionMessage(udp_port)

    @staticmethod
    def size():
        return MessageTypeHelper.SIZE + UdpPortHelper.SIZE

    def serialize(self):
        return MessageTypeHelper.serialize(ConnectionMessage.MESSAGE_TYPE) + UdpPortHelper.serialize(self.udp_port)


class InfoFileMessage:
    MESSAGE_TYPE = 3

    def __init__(self, file_name, file_size):
        self.file_name = file_name
        self.file_size = file_size

    @staticmethod
    def deserialize(data):
        message_type_bytes = data[0:MessageTypeHelper.SIZE]
        message_type = MessageTypeHelper.deserialize(message_type_bytes)

        file_name_offset = (MessageTypeHelper.SIZE + FileNameHelper.SIZE)
        file_name_bytes = data[MessageTypeHelper.SIZE:file_name_offset]
        file_name = FileNameHelper.deserialize(file_name_bytes)

        file_size_bytes = data[file_name_offset:(
            file_name_offset + FileSizeHelper.SIZE)]
        file_size = FileSizeHelper.deserialize(file_size_bytes)

        if message_type != ConnectionMessage.MESSAGE_TYPE:
            raise Exception("wrong type for INFO FILE message")

        return InfoFileMessage(file_name, file_size)

    @staticmethod
    def size():
        return MessageTypeHelper.SIZE + FileNameHelper.SIZE + FileSizeHelper.SIZE

    def serialize(self):
        return MessageTypeHelper.serialize(ConnectionMessage.MESSAGE_TYPE) \
            + FileNameHelper.serialize(self.file_name) \
            + FileSizeHelper.serialize(self.file_size)


class OkMessage:
    MESSAGE_TYPE = 4

    @staticmethod
    def deserialize(data):
        message_type = MessageTypeHelper.deserialize(data)
        if message_type != OkMessage.MESSAGE_TYPE:
            raise Exception("wrong type for OK message")

    @staticmethod
    def size():
        return MessageTypeHelper.SIZE

    @staticmethod
    def serialize():
        return MessageTypeHelper.serialize(OkMessage.MESSAGE_TYPE)


class FimMessage:
    MESSAGE_TYPE = 5

    @staticmethod
    def deserialize(data):
        message_type = MessageTypeHelper.deserialize(data)
        if message_type != FimMessage.MESSAGE_TYPE:
            raise Exception("wrong type for FIM message")

    @staticmethod
    def size():
        return MessageTypeHelper.SIZE

    @staticmethod
    def serialize():
        return MessageTypeHelper.serialize(FimMessage.MESSAGE_TYPE)


class FileMessage:
    MESSAGE_TYPE = 6

    def __init__(self, n_seq, payload_size, payload):
        self.n_seq = n_seq
        self.payload_size = payload_size
        self.payload = payload

    @staticmethod
    def deserialize(data, msg_peek=False):
        message_type_bytes = data[0:MessageTypeHelper.SIZE]
        message_type = MessageTypeHelper.deserialize(message_type_bytes)

        if message_type != ConnectionMessage.MESSAGE_TYPE:
            raise Exception("wrong type for FILE message")

        n_seq_offset = (MessageTypeHelper.SIZE + NSeqHelper.SIZE)
        n_seq_bytes = data[MessageTypeHelper.SIZE:n_seq_offset]
        n_seq = NSeqHelper.deserialize(n_seq_bytes)

        payload_size_offset = (n_seq_offset + PayloadSizeHelper.SIZE)
        payload_size_bytes = data[n_seq_offset:payload_size_offset]
        payload_size = PayloadSizeHelper.deserialize(payload_size_bytes)

        payload = None
        if not msg_peek:
            payload = data[payload_size_offset:]

            if payload_size != len(payload):
                raise Exception("wrong payload size")

        return FileMessage(n_seq, payload_size, payload)

    @staticmethod
    def size(payload_size=0):
        return MessageTypeHelper.SIZE + NSeqHelper.SIZE + PayloadSizeHelper.SIZE + payload_size

    def serialize(self):
        return MessageTypeHelper.serialize(ConnectionMessage.MESSAGE_TYPE) \
            + NSeqHelper.serialize(self.n_seq) \
            + PayloadSizeHelper.serialize(self.payload_size) \
            + self.payload


class AckMessage:
    MESSAGE_TYPE = 7

    def __init__(self, n_seq):
        self.n_seq = n_seq

    @staticmethod
    def deserialize(data):
        message_type_bytes = data[0:MessageTypeHelper.SIZE]
        message_type = MessageTypeHelper.deserialize(message_type_bytes)

        if message_type != AckMessage.MESSAGE_TYPE:
            raise Exception("wrong type for ACK message")

        n_seq_bytes = data[MessageTypeHelper.SIZE:(
            MessageTypeHelper.SIZE + NSeqHelper.SIZE)]
        n_seq = NSeqHelper.deserialize(n_seq_bytes)

        return AckMessage(n_seq)

    @staticmethod
    def size():
        return MessageTypeHelper.SIZE + NSeqHelper.SIZE

    def serialize(self):
        return MessageTypeHelper.serialize(AckMessage.MESSAGE_TYPE) + NSeqHelper.serialize(self.n_seq)
