import socket
import struct
import array
from varint import varintCodec
from pyrac.rac_packet import RacPacket
from  pyrac.rac_connection import RacConnection






class Param:
    type = 0
    value = bytes()




client_ip = 'localhost'
client_port = 1545

connection = RacConnection(client_ip, client_port)
connection.connect()
connection.recv_cluster_ojects()
connection.disconnect()