#!/usr/bin/python

import sys
import getopt
from socket import *
from endpoint_client import SocketClient
from endpoint_server import EndPointServer
from topology import Topology
import json

def Usage():
    print 'endpoint_system.py usage'
    print '-h, --help: print help message'
    print '--server: run endpoint server'
    print '--client: run endpoint client'


def start_server(port):
    ADDR = ('', port)
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(ADDR)
    print "end system waiting for message : "
    while True:
        receive_data, receive_address = server_socket.recvfrom(1024)
        receive_data = json.loads(receive_data)
        receive_data.pop('type')
        print "end system receive data : " + json.dumps(receive_data)

def start_client(client_name, port):
    topo = Topology()
    server_ip = topo.get_host_neighbor(client_name)['ip']
    client_ip = topo.get_node_info(client_name)['ip']
    client = SocketClient(client_ip=client_ip, server_ip=server_ip, server_port=port)
    client.start_client()


if __name__ == '__main__':
    if sys.argv.__len__() is 1:
        Usage()
        sys.exit()
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hsc', ['help', 'server', 'client='])
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit()
    for o, a in opts:
        if o in ('-h', '--help'):
            Usage()
            sys.exit(1)
        if o in '--server':
            start_server(10608)
        if o in '--client':
            start_client(a, 10608)
