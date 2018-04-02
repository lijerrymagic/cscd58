#!/usr/bin/python

import sys
import getopt
import re
import os
from topology import Topology
from router_service.service.socket_client import SocketClient
from router_service.service.socket_server import SocketServer
from router_service.service.net import Network
def Usage():
    print 'RouterSocketClient.py usage:'
    print '-h,--help: print help message.'
    print '-t,--topo: create topology'
    print '-i,--info: show router info'
    print '-c,--client: create client'
    print '-s,--server: create server'

def main(argv):
    client_name = None
    server_name = None
    if argv is None:
        Usage()
        return
    try:
        opts, args = getopt.getopt(argv[1:], 'hit', ['client=', 'server='])
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit(2)
    for o, a in opts:
        if o in ('-h', '--help'):
            print "******"
            Usage()
            sys.exit(1)
        if o in ('-i', '--info'):
            Usage()
            sys.exit(1)
        if o in ('-t', '--topo'):
            Network()
            sys.exit(1)
        elif o in ('--server',):
            server_name = a
        elif o in ('--client',):
            client_name = a
        elif o in ('-c', '--client'):
            server_name = a
        else:
            print 'unhandled option'
            sys.exit(3)

    #get server ip list from config
    if client_name is not None:
        router_client_infos = Topology().get_server_interfaces(client_name)
        if router_client_infos is None:
            arg_error('server ip is None')
            sys.exit(3)
        else:
            print "*****router_client_infos:",router_client_infos
            SocketClient(client_name).create_socket_client_instance(router_client_infos)
    elif server_name is not None:
        SocketServer().create_socket_server_instance(server_name)

    sys.exit(0)

def arg_error(argv):
    print '%s is valid' %argv

def output(argv):
    print argv
if __name__ == '__main__':
    main(sys.argv)