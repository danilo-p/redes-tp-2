import struct


def serialize_message(struct_format, values):
    packer = struct.Struct(struct_format)
    return packer.pack(*values)


def deserialize_message(struct_format, data):
    unpacker = struct.Struct(struct_format)
    return unpacker.unpack(data)


def get_format_size(struct_format):
    return struct.Struct(struct_format).size


class HelloMessage:
    MESSAGE_TYPE = 1
    FORMAT = 'H'

    @staticmethod
    def deserialize(data):
        values = deserialize_message(HelloMessage.FORMAT, data)
        if values[0] != HelloMessage.MESSAGE_TYPE:
            raise Exception("Wrong type for HELLO message")

    @staticmethod
    def size():
        return get_format_size(HelloMessage.FORMAT)

    @staticmethod
    def serialize():
        return serialize_message(HelloMessage.FORMAT, (HelloMessage.MESSAGE_TYPE,))


class ConnectionMessage:
    MESSAGE_TYPE = 2
    FORMAT = 'HH'

    def __init__(self, udp_port):
        self.udp_port = udp_port

    @staticmethod
    def deserialize(data):
        values = deserialize_message(ConnectionMessage.FORMAT, data)
        if values[0] != ConnectionMessage.MESSAGE_TYPE:
            raise Exception("Wrong type for CONNECTION message")
        return ConnectionMessage(values[1])

    @staticmethod
    def size():
        return get_format_size(ConnectionMessage.FORMAT)

    def serialize(self):
        return serialize_message(ConnectionMessage.FORMAT, (ConnectionMessage.MESSAGE_TYPE, self.udp_port))
