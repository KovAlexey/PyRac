import uuid
import io
from varint import varintCodec
from pyrac.rac_packet import PacketMessage


class RacInfobaseObject:
    __uuid = None
    __date_offset = 0
    __dmbs = ''
    __db_name = ''
    __db_password = ''
    __db_server_name = ''
    __db_user = ''
    __denie_from = 0
    __denied_message = ''
    __denied_parameter = ''
    __denied_to = 0
    __descr = ''
    __locale = ''
    __name = ''
    __permission_code = ''
    __scheduled_jobs_denied = False
    __security_level = 0
    __sessions_denied = False
    __license_distribution = 0
    __external_connection_string = ''
    __external_session_manager_required = False
    __securirty_profile = ''
    __safe_mode_securirty_profile = ''
    __reserve_working_processes = False

    def getuuid(self):
        return self.__uuid

    def update_from_full(self, bytes_io_in):
        self.__uuid = uuid.UUID(bytes=bytes_io_in.read(16))  # GUID
        self.__date_offset = int.from_bytes(bytes_io_in.read(4), 'big')
        len_str = varintCodec.DecodeFromStream(bytes_io_in)
        self.__dbms = bytes_io_in.read(len_str).decode()
        len_str = varintCodec.DecodeFromStream(bytes_io_in)
        self.__db_name = bytes_io_in.read(len_str).decode()
        len_str = varintCodec.DecodeFromStream(bytes_io_in)
        self.__db_password = bytes_io_in.read(len_str).decode()
        len_str = varintCodec.DecodeFromStream(bytes_io_in)
        self.__db_server_name = bytes_io_in.read(len_str).decode()
        len_str = varintCodec.DecodeFromStream(bytes_io_in)
        self.__db_user = bytes_io_in.read(len_str).decode()

    # TODO: вариант метода для коллекции с поиском по гуиду
    def update_from_summary(self, bytes_io_in):
        self.__uuid = uuid.UUID(bytes=bytes_io_in.read(16))  # GUID
        lenght = varintCodec.DecodeFromStream(bytes_io_in)
        self.__name = bytes_io_in.read(lenght).decode()
        lenght = varintCodec.DecodeFromStream(bytes_io_in)
        self.__descr = bytes_io_in.read(lenght).decode()

    @staticmethod
    def CreateFromBytes(bytes):
        file = io.BytesIO(bytes)
        start_bytes = file.read(4)
        packet_type = file.read(1)

        if packet_type == PacketMessage.INFOBASE_FOR_INFOBASE_SUMMARY_ANSWER:
            count = 1
        else:
            count = varintCodec.DecodeFromStream(file)
        databases = []
        for i in range(count):
            db_object = RacInfobaseObject()
            if packet_type in PacketMessage.INFOBASE_LIST_SUMMARY_ANSWER:
                db_object.update_from_summary(file)
            else:
                db_object.update_from_full(file)
            databases.append(db_object)
        return databases

