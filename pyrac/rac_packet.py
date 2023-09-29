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
    PACKET_TYPE_MESSAGE = b'\x0E'


class PacketMessage:
    CLUSTER_LIST = b'\x0b'  # Возвращает список кластеров

    # Возможно проверка существования кластера? Возвращает 0,если он существует. И ошибку, если нет.
    # В любом случае RAC отправляет его каждый раз, перед тем как получить список информационных баз кластера
    # И только в случае успеха отправляет уже получение списка
    # Аргументы: GUID кластера и возможно что-то значащие \x00\x00
    CLUSTER_CHECK = b'\x09'  # ???

    # Получить список информационных баз
    # Аргументы: ГУИД кластера
    GET_INFOBASE_LIST_SUMMARY = b'\x2A'



class RacPacket:
    _data = b''
    _type = b''

    def __init__(self, _type=b''):
        self._type = _type

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
        new_packet.add_bytes(self._type)
        new_packet.add_varint(len(self._data))

        return new_packet

    def add_header(self, message_byte):
        self._data = b'\x01\x00\x00\x01'
        self.add_bytes(message_byte)

    def getpackettype(self):
        return self._type
