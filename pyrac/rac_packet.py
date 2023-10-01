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
    REQUEST_FAILED = b'\xFF' # судя по всему в случае ошибок, заголовком является FF
    CLUSTER_LIST = b'\x0b'  # Возвращает список кластеров

    # Авторизация
    # Аргументы:
    # GUID кластера
    # Пользователь - 0x00, если нет
    # Пароль - 0x00, если нет
    CLUSTER_AUTHENTICATION_QUERY = b'\x09'

    # Получить список информационных баз
    # Аргументы: ГУИД кластера
    INFOBASE_LIST_SUMMARY_QUERY = b'\x2A'
    # Короткий список информационных баз
    # Аргументы
    # Количество ИБ
    # (Гуид - гуид, Имя - строка, Описание - строка)
    INFOBASE_LIST_SUMMARY_ANSWER = b'\x2B'

    # То же, что INFOBASE_LIST_SUMMARY_QUERY
    # Но для конкретной базы
    # Аргументы (ГУИД - гуид кластера, ГУИД - гуид ИБ)
    INFOBASE_FOR_INFOBASE_SUMMARY_QUERY = b'\x2E'

    # Краткое описание информационной базы
    # То же, что INFOBASE_LIST_SUMMARY_ANSWER, но для конкретной базы без укзаания количества
    INFOBASE_FOR_INFOBASE_SUMMARY_ANSWER = b'\x2F'

    # судя по всему еще авторизация, но непонятно где
    # но без этой авторизации часть информации по ИБ доступна не будет
    # А INFOBASE_FULL_INFO_REQUEST выдаст исключение по правам
    # Аргументы:
    #   uuid кластера
    #   Логин (ничего, если нет)
    #   Пароль (ничего, если нет)
    # Возвращается:
    #   0x00 0x01 0x00 0x00 в случае успеха
    #   В случае отказа - нужно разобрать как получать ошибки из RAS
    INFOBASE_AUTORIZATION_REQUEST = b'\x0A'

    # Полное описание информационной базы
    # 3 аргумента по порядку
    # UUID базы, логин (ничего, если нет) от ИБ, пароль от ИБ (ничего, если не требуется)
    # Или это все таки авторизация в ИБ? RAC сначала выполняет это действие и в случае успеха уже запрашивает инфу о БД
    INFOBASE_FULL_INFO_REQUEST = b'\x30'
    INFOBASE_FULL_INFO_ANSWER = b'\x31'


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

        temp_string = bytes(string, encoding='utf-8')
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
