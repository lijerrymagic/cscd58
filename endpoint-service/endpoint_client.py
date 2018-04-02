from socket import *
import json
import sys

class SocketClient:
    '''a class represents end system client'''
    def __init__(self, client_ip=None, server_ip=None, server_port=None):
        self.client_ip = client_ip
        self.server_ip = server_ip
        self.server_port = server_port

    def start_client(self):
        # send register msg
        register_socket = socket(AF_INET, SOCK_DGRAM)
        register_socket.settimeout(2)
        register_socket.sendto(self._init_register_data().encode(encoding='utf-8'), (self.server_ip, self.server_port))
        register_socket.close()
        while True:
            # send forwarding msg
            clientsocket = socket(AF_INET, SOCK_DGRAM)
            clientsocket.settimeout(2)
            clientsocket.connect((self.server_ip, self.server_port))

            target_ip = raw_input('Target IP: ')
            message = raw_input('Message: ')
            if not target_ip or not message:
                break
            clientsocket.sendto(self._init_formal_data(target_ip, message).encode(encoding='utf-8'), (self.server_ip, self.server_port))
            clientsocket.close()
    
    def _init_register_data(self):
        ''' data type 1 is the data used to broadcast to 255.255.255.255 to inform its existence'''
        data = {
            'nw_src': self.client_ip,
            'nw_dst': '255.255.255.255',
            'ttl': 0,
            'type': 1
        }
        return json.dumps(data)

    def _init_formal_data(self, target_ip, message):
        ''' data type 2 is the data used to communicate between end systems'''
        data = {
            'nw_src': self.client_ip,
            'nw_dst': target_ip,
            'ttl': 255,
            'message': message,
            'type': 2,
        }
        return json.dumps(data)