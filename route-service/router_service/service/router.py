from socket_server import SocketServer
from socket_client import SocketClient
class Router:
    def __init__(self, router_name, interfaces):
        self.interfaces = interfaces
        self.router_name = router_name

    def create_router_instance(self):
        SocketClient().create_socket_client_instance(self.interfaces)
        SocketServer().create_socket_server_instance(self.router_name)
