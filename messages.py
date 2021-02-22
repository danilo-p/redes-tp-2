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


class HelloMessage:
    MESSAGE_TYPE = 1

    @staticmethod
    def deserialize(data):
        message_type = MessageTypeHelper.deserialize(data)
        if message_type != HelloMessage.MESSAGE_TYPE:
            raise Exception("Wrong type for HELLO message")

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
            raise Exception("Wrong type for CONNECTION message")

        return ConnectionMessage(udp_port)

    @staticmethod
    def size():
        return MessageTypeHelper.SIZE + UdpPortHelper.SIZE

    def serialize(self):
        return MessageTypeHelper.serialize(ConnectionMessage.MESSAGE_TYPE) + UdpPortHelper.serialize(self.udp_port)
