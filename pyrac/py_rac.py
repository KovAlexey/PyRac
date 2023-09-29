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
clusters = connection.recv_cluster_objects()
connection.authentication(clusters[0])
connection.get_infobase_list(clusters[0])
connection.disconnect()