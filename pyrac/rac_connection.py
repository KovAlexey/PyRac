import socket
import io
from pyrac.rac_packet import RacPacket, NegotiateMessage, PacketType, PacketMessage
from varint import varintCodec
import uuid


class ClusterObject:
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

        clusterObjects = []

        for i in range(count):
            clusterObject = ClusterObject(file)
            clusterObjects.append(clusterObject)
        return clusterObjects


class RacConnection:
    host = ''
    port = 1545
    _connected = False
    _socket = socket.socket()

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect(self):
        self._socket.connect((self.host, self.port))
        self._socket.send(NegotiateMessage.GetMessage())

        connect_message = RacPacket()
        connect_message.add_bytes(b'\x01\x16\x01')
        connect_message.add_string('connect.timeout')
        connect_message.add_integer(2000)

        self._socket.send(connect_message.get_data())
        next_packet_size = self.recv_sizepacket()

        answer = self._socket.recv(next_packet_size)

        cluster_list_message = RacPacket(PacketType.PACKET_TYPE_ENDPOINT_OPEN)
        cluster_list_message.add_string('v8.service.Admin.Cluster')
        cluster_list_message.add_string('10.0')
        cluster_list_message.end_this_packet()

        self.send_with_size(cluster_list_message)

        next_packet_size = self.recv_sizepacket()
        print(next_packet_size)
        print(self._socket.recv(next_packet_size))

    def recv_cluster_objects(self):
        packet = RacPacket(PacketType.PACKET_TYPE_MESSAGE)
        packet.add_header(PacketMessage.CLUSTER_LIST)

        self.send_with_size(packet)

        packet_size = self.recv_sizepacket()
        recv_len = 0
        data = b''
        while recv_len < packet_size:
            data += self._socket.recv(packet_size)
            recv_len = len(data)

        clusters = ClusterObject.CreateFromBytes(data)
        return clusters

    def check_cluster(self, clusterObject: ClusterObject):
        packet = RacPacket(PacketType.PACKET_TYPE_MESSAGE)
        packet.add_header(PacketMessage.CLUSTER_CHECK)
        packet.add_bytes(clusterObject.getGuid().bytes)
        packet.add_bytes(b'\x00\x00') # Этот запрос

        self.send_with_size(packet)

        packet_size = self.recv_sizepacket()
        recv_len = 0
        data = b''
        while recv_len < packet_size:
            data += self._socket.recv(packet_size)
            recv_len = len(data)

    def get_infobase_list(self, clusterObject: ClusterObject):
        packet = RacPacket(PacketType.PACKET_TYPE_MESSAGE)
        packet.add_header(PacketMessage.GET_INFOBASE_LIST_SUMMARY)
        packet.add_bytes(clusterObject.getGuid().bytes)

        self.send_with_size(packet)

        packet_size = self.recv_sizepacket()
        recv_len = 0
        data = b''
        while recv_len < packet_size:
            data += self._socket.recv(packet_size)
            recv_len = len(data)

    def recv_sizepacket(self):
        # start byte
        self._socket.recv(1)
        return self.recv_varint()

    def recv_varint(self):
        # buffer = b''
        buffer = 0
        shift = 0
        while True:
            bytes_recv = self._socket.recv(1)
            value = bytes_recv[0] & 0b01111111
            buffer |= (value << shift)
            shift += 7
            if not bytes_recv[0] & 0b10000000:
                break
        return buffer

    def disconnect(self):
        self._socket.close()

    def send(self, data: RacPacket):
        self._socket.send(data.get_data())

    def send_with_size(self, data: RacPacket):
        size_packet = data.form_size_packet(data.getpackettype())
        self._socket.send(size_packet.get_data())
        self._socket.send(data.get_data())
