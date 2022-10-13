import socket
from pyrac.rac_packet import RacPacket, NegotiateMessage, PacketType


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

        cluster_list_message = RacPacket()
        cluster_list_message.add_string('v8.service.Admin.Cluster')
        cluster_list_message.add_string('10.0')
        cluster_list_message.end_this_packet()

        self.send_with_size(cluster_list_message)

        next_packet_size = self.recv_sizepacket()
        print(next_packet_size)
        print(self._socket.recv(next_packet_size))

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
        size_packet = data.form_size_packet(PacketType.PACKET_TYPE_ENDPOINT_OPEN)
        self._socket.send(size_packet.get_data())
        self._socket.send(data.get_data())
