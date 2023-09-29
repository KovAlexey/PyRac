import socket

from pyrac.rac_cluster_object import RacClusterObject
from pyrac.rac_packet import RacPacket, NegotiateMessage, PacketType, PacketMessage


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

        data = self.recv_with_size()
        clusters = RacClusterObject.CreateFromBytes(data)
        return clusters

    def authentication(self, clusterObject: RacClusterObject, login="", password=""):
        packet = RacPacket(PacketType.PACKET_TYPE_MESSAGE)
        packet.add_header(PacketMessage.CLUSTER_AUTHENTICATION)
        packet.add_bytes(clusterObject.getGuid().bytes)

        if len(login) > 0:
            packet.add_string(login)
        else:
            packet.add_bytes(b'\x00')  # Пустой логин

        if len(password) > 0:
            packet.add_string(password)
        else:
            packet.add_bytes(b'\x00')  # Пустой пароль

        self.send_with_size(packet)

        packet_size = self.recv_sizepacket()
        recv_len = 0
        data = b''
        while recv_len < packet_size:
            data += self._socket.recv(packet_size)
            recv_len = len(data)

    def get_infobase_list(self, clusterObject: RacClusterObject):
        packet = RacPacket(PacketType.PACKET_TYPE_MESSAGE)
        packet.add_header(PacketMessage.GET_INFOBASE_LIST_SUMMARY)
        packet.add_bytes(clusterObject.getGuid().bytes)

        self.send_with_size(packet)

        data = self.recv_with_size()


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

    def recv_with_size(self):
        packet_size = self.recv_sizepacket()
        recv_len = 0
        data = b''
        while recv_len < packet_size:
            data += self._socket.recv(packet_size)
            recv_len = len(data)

        return data
