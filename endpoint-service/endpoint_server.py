#encoding:utf-8
from SocketServer import (TCPServer as TCP,StreamRequestHandler as SRH)
from time import ctime


class EndPointServer(SRH):

    def handle(self):
        # print '...connected from:', self.client_address
        # self.wfile.write('[%s] %s' % (ctime(), self.rfile.readline()))
        print ctime() + "----" + self.rfile.readline()