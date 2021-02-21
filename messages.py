import struct


def serialize_message(struct_format, values):
    packer = struct.Struct(struct_format)
    return packer.pack(*values)


def deserialize_message(struct_format, data):
    unpacker = struct.Struct(struct_format)
    return unpacker.unpack(data)


def get_message_size(struct_format):
    return struct.Struct(struct_format).size


class HelloMessage:
    FORMAT = 'I'

    @staticmethod
    def deserialize(data):
        return deserialize_message(HelloMessage.FORMAT, data)

    @staticmethod
    def size():
        return get_message_size(HelloMessage.FORMAT)

    @staticmethod
    def serialize():
        return serialize_message(HelloMessage.FORMAT, (1,))
