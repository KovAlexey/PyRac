import socket
import struct
import array
from varint import varintCodec
from pyrac.rac_packet import RacPacket
from  pyrac.rac_connection import RacConnection






class Param:
    type = 0
    value = bytes()




client_ip = 'r3d3'
client_port = 1545

connection = RacConnection(client_ip, client_port)
connection.connect()
connection.disconnect()