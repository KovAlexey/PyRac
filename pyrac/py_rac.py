from pyrac.rac_connection import RacConnection
import json






class Param:
    type = 0
    value = bytes()




client_ip = 'localhost'
client_port = 1545

logpass = dict()
with open('logpass.txt') as f:
    logpass = json.loads(f.read())

connection = RacConnection(client_ip, client_port)
connection.connect()
clusters = connection.recv_cluster_objects()
connection.authentication(clusters[0])
db_list = connection.get_infobase_summary_list(clusters[0])
summary_for_base = connection.get_infobase_summary_for_infobase(clusters[0], db_list[0])
connection.authentication_to_ib(clusters[0], logpass["login"], logpass["pwd"])
data = connection.get_infobase_full_info(clusters[0], db_list[0])
connection.disconnect()