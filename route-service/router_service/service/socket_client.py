from socket import *
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import time
import os
import json
from router_service.db.router_table_client import RouterTableClient
class SocketClient:

    def __init__(self, client_name=None, interfaces=None):
        self.server_port = 5000
        self.client_name = client_name
        self.interfaces = interfaces
        self.scheduler = None
        self.client_socket = None
        if self.client_name:
            self.router_table_client = RouterTableClient(client_name)

    def create_socket_client_instance(self, interfaces):
        self.interfaces = interfaces
        self.scheduler = BlockingScheduler()
        self.client_socket = self.create_socket_client()
        self.scheduler.add_job(self.update_routers, 'cron', second='*/10', hour='*')
        print 'Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C')
        try:
            self.scheduler.start()
        except KeyboardInterrupt, SystemExit:
            self.destroy_socket_client(self.client_socket)
            self.scheduler.shutdown()

    def create_socket_client(self):
        client_socket = socket(AF_INET, SOCK_DGRAM)
        client_socket.settimeout(2)
        return client_socket

    def destroy_socket_client(self, client_socket):
        client_socket.close()

    def update_routers(self):
        request_context = self._process_message_context()
        for interface in self.interfaces:
            print "---------client send_data", json.dumps(request_context)
            self.process_send_message(self.client_socket, interface['nw_dst'], json.dumps(request_context))
            print "---------client waiting receive"
            try:
                receive_data, receive_address = self.client_socket.recvfrom(1024)
            except:
                receive_data = None
            print "---------cleint receive_data", receive_data
            if receive_data is None or receive_data == "None" or receive_data == "":
                print "No router information to update"
            else:
                receive_data = json.loads(receive_data)

                for item in receive_data['item']:
                    router_item = {
                        'nw_dst': item['nw_dst'],
                        'next_hop': interface['nw_dst'],
                        'ttl': item['ttl'] + 1
                    }
                    print "Update router information: " + json.dumps(router_item)
                    self.router_table_client.update_router_table_by_name(self.client_name, router_item)

    def _process_message_context(self):
        message_context = {
            'ttl': 1,
            'type': 3
        }
        return message_context

    def process_send_message(self, client_socket, server_ip, data):
        print "Router client send to :" + server_ip + data
        client_socket.sendto(data.encode(encoding='utf-8'), (server_ip, self.server_port))
