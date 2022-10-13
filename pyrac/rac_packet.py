import struct
from varint import varintCodec


class NegotiateMessage:
    magic = 475223888
    protocol = 256
    version = 256

    @staticmethod
    def GetMessage() -> bytes:
        value = (NegotiateMessage.magic, NegotiateMessage.protocol, NegotiateMessage.version)
        return struct.pack(">ihh", *value)


class PacketType:
    NEGOTIATE = b'\x00'
    CONNECT = b'x01'
    CONNECT_ACK = b'\x02'
    PACKET_TYPE_ENDPOINT_OPEN = b'\x0B'


class RacPacket:
    _data = b''

    def __init__(self, _type=b''):
        self._data = _type

    def add_integer(self, integer):
        intbuff = struct.pack('>i', integer)
        self.add_varint(len(intbuff))
        self._data += intbuff

    def add_varint(self, integer):
        value = varintCodec.Encode(integer)
        self._data += value

    def add_string(self, string):
        length = len(string)

        temp_string = bytes(string, encoding='ANSI')
        buffer_length = len(temp_string)
        format_string = f'>{buffer_length}s'

        buffer = struct.pack(format_string, temp_string)
        self._data += varintCodec.Encode(buffer_length) + buffer

    def get_data(self):
        return self._data

    def add_bytes(self, added_bytes):
        self._data += added_bytes

    def end_this_packet(self):
        self._data += b'\x80'

    def form_size_packet(self, packet_type):
        new_packet = RacPacket()
        new_packet.add_bytes(packet_type)
        new_packet.add_varint(len(self._data))

        return new_packet
