#encoding:utf-8
class Topology:
    '''A topology class contains all hardcoding network configuration'''
    def __init__(self):
        self.topo = {
            'node': [
                {
                    'name': 'h1',
                    'type': 'host',
                    'ip': '10.0.0.1'
                },
                {
                    'name': 'h2',
                    'type': 'host',
                    'ip': '20.0.0.1',

                },
                {
                    'name': 'r1',
                    'type': 'router',
                    'interface': [
                        {
                            'id': 1,
                            "name": 'r1-h1',
                            'ip': '10.0.0.2'
                        },
                        {
                            'id': 2,
                            "name": 'r1-h2',
                            'ip': '20.0.0.2'
                        }
                    ]
                }
            ],
            'link': [
                {
                    'src_node': 'h1',
                    'dst_node': 'r1',
                    'src_itf': '',
                    'dst_itf': 1,
                },
                {
                    'src_node': 'h2',
                    'dst_node': 'r1',
                    'src_itf': '',
                    'dst_itf': 2
                }
            ]
        }

    def get_topology(self):
        return self.topo
    
    def get_server_interfaces(self, src_node_name):

        links = self.topo['link']
        interface_list = []
        for link in links:
            if src_node_name == link['src_node'] and link['src_itf'] and link['dst_itf']:
                nw_src = self.get_node_ip(link['src_node'], link['src_itf'])
                nw_dst = self.get_node_ip(link['dst_node'], link['dst_itf'])
                if nw_src and nw_dst:
                    interface_list.append({
                        'nw_src': nw_src,
                        'nw_dst': nw_dst
                    })

            elif src_node_name == link['dst_node'] and link['src_itf'] and link['dst_itf']:
                nw_src = self.get_node_ip(link['dst_node'], link['dst_itf'])
                nw_dst = self.get_node_ip(link['src_node'], link['src_itf'])
                if nw_src and nw_dst:
                    interface_list.append({
                        'nw_src': nw_src,
                        'nw_dst': nw_dst
                    })
        return interface_list

    def get_node_info(self, node_name):
        '''get the node whole information'''
        nodes = self.topo['node']
        for node in nodes:
            if node['name'] == node_name:
                return node
        return None

    def get_node_ip(self, node_name, interface_id):
        ''' get the host ip address'''
        node = self.get_node_info(node_name)
        if node is None:
            return None
        for interface in node['interface']:
            if interface['id'] == interface_id:
                return interface['ip']
        return None

    def get_host_neighbor(self, node_name):
        """ get the router which is attached by `node_name` """
        links = self.topo['link']
        for link in links:
            if node_name == link['src_node']:
                dst_node = self.get_node_info(link['dst_node'])
                interfaces = dst_node['interface']
                for intf in interfaces:
                    if node_name in intf['name']:
                        return {
                            'name': dst_node['name'],
                            'ip': intf['ip']
                        }