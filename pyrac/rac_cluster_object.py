import io
import uuid

from varint import varintCodec



class RacClusterObject:
    __guid = b''
    __host = ''
    __port = 0
    __name = ''
    __expiration_timeout = 0
    __lifetime_limit = 0
    __restart_interval = 0
    __memory_size = 0
    __max_memory_limit = 0
    __terminate_problem_process = 0
    __secure_connection = 0
    __fault_tolerance_level = 0
    __load_balancing_mode = 0
    __errors_count_threshold = 0
    __kill_problem_processes = False
    __kill_by_memory_with_dump = True

    def getGuid(self):
        return self.__guid

    def __init__(self, file):
        self.__guid = uuid.UUID(bytes=file.read(16))  # GUID
        self.__terminate_problem_process = int.from_bytes(file.read(4), 'big')  # terminate problem process
        lenght = varintCodec.DecodeFromStream(file)
        self.__host = file.read(lenght).decode()
        self.__restart_interval = int.from_bytes(file.read(4), 'big')  # restart interval
        self.__port = int.from_bytes(file.read(2), 'big')  # port
        self.__memory_size = int.from_bytes(file.read(4), 'big')  # memory size
        self.__max_memory_limit = int.from_bytes(file.read(4), 'big')  # max memory limit
        lenght = varintCodec.DecodeFromStream(file)
        self.__name = file.read(lenght).decode()
        self.__secure_connection = int.from_bytes(file.read(4), 'big')
        self.__fault_tolerance_level = int.from_bytes(file.read(4), 'big')
        self.__load_balancing_mode = int.from_bytes(file.read(4), 'big')
        self.__errors_count_threshold = int.from_bytes(file.read(4), 'big')
        self.__kill_problem_processes = bool.from_bytes(file.read(1), 'big')
        self.__kill_by_memory_with_dump = bool.from_bytes(file.read(1), 'big')

    @staticmethod
    def CreateFromBytes(bytes):
        file = io.BytesIO(bytes)
        start_bytes = file.read(4)
        packet_type = file.read(1)
        count = varintCodec.DecodeFromStream(file)

        cluster_objects = []

        for i in range(count):
            cluster_object = RacClusterObject(file)
            cluster_objects.append(cluster_object)
        return cluster_objects
