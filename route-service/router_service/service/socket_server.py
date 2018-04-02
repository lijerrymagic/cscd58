#encoding:utf-8
from socket import *
from time import ctime
from router_service.db.router_table_client import RouterTableClient
from router_service.service.socket_client import SocketClient
from topology import Topology
import json

class SocketServer:
    def __init__(self):
        self.server_port = 5000
        self.server_name = None
        self.router_socket_server = None
        self.router_table_db_client = None
        self.topology = Topology()

    def create_socket_server_instance(self, server_name):
        print "**************create_socket_server***************"
        self.router_table_db_client = RouterTableClient(server_name)
        self.server_name = server_name
        self.create_socket_server()



    def create_socket_server(self):
        server_addr = ("", self.server_port)
        server_socket = socket(AF_INET, SOCK_DGRAM)
        #server_socket.settimeout(2)
        server_socket.bind(server_addr)
        self.router_socket_server = server_socket
        print 'Router socket are waiting for connecting ......'
        while True:
            receive_data, receive_address = server_socket.recvfrom(1024)
            print 'Connected by ', receive_address
            print "Router server receive data : " + receive_data
            if receive_data:
                self.router_message_listener(json.loads(receive_data), receive_address)
        self.router_socket_server.close()

    def router_message_listener(self, message, receive_address):

        if message is not None and 'type' in message:
            message_type = message['type']
            if message_type == 1:
                self._process_hand_host_online_message(message)
            elif message_type == 2:
                self._process_send_forwarding_message(message)
            elif message_type == 3:
                self._process_send_router_info_message(receive_address)

    def _process_send_router_info_message(self, receive_address):
        router_info = self.router_table_db_client.get_router_table_by_name(self.server_name)
        if router_info:
            router_info = json.dumps(router_info)
        else:
            router_info = "None"
        print "router server send:", router_info
        self.router_socket_server.sendto(router_info, receive_address)

    def _process_hand_host_online_message(self, message):
        router_item = {
            'nw_dst': message['nw_src'],
            'next_hop': None,
            #'related_router': self.server_name,
            'ttl': 1,
            #'message': '参考RIP协议路由表项'
        }
        self.router_table_db_client.update_router_table_by_name(self.server_name, router_item)

    def _process_send_forwarding_message(self, message):
        #查看自己的路由表项，ttl最小的，转发
        router_table = self.router_table_db_client.get_router_table_by_name(self.server_name)
        if 'item' not in router_table:
            return
        for item in router_table['item']:
            if item['nw_dst'] == message['nw_dst'] and message['ttl'] > 1:
                #name = self.topology.get_host_name_by_interface(item['next_hop'])
                socket_client = SocketClient()
                socket_client_instance = socket_client.create_socket_client()
                message['ttl'] = message['ttl'] - 1
                addr = item['next_hop']
                if not addr:
                    addr = message['nw_dst']
                socket_client.process_send_message(socket_client_instance, addr, json.dumps(message))