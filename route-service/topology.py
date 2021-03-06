#encoding:utf-8
class Topology:
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
                            "name": 'r1-r2',
                            'ip': '30.0.0.1'
                        },
                        {
                            'id': 3,
                            "name": 'r1-r3',
                            'ip': '40.0.0.1'
                        }
                    ]
                },
                {
                    'name': 'r2',
                    'type': 'router',
                    'interface': [
                        {
                            'id': 1,
                            "name": 'r2-h2',
                            'ip': '20.0.0.2'
                        },
                        {
                            'id': 2,
                            "name": 'r2-r1',
                            'ip': '30.0.0.2'
                        },
                        {
                            'id': 3,
                            "name": 'r2-r3',
                            'ip': '50.0.0.1'
                        }
                    ]
                },
                {
                    'name': 'r3',
                    'type': 'router',
                    'interface': [
                        {
                            'id': 1,
                            "name": 'r3-r1',
                            'ip': '40.0.0.2'
                        },
                        {
                            'id': 2,
                            "name": 'r3-r2',
                            'ip': '50.0.0.2'
                        }
                    ]
                },
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
                    'dst_node': 'r2',
                    'src_itf': '',
                    'dst_itf': 1
                },
                {
                    'src_node': 'r1',
                    'dst_node': 'r2',
                    'src_itf': 2,
                    'dst_itf': 2
                },
                {
                    'src_node': 'r1',
                    'dst_node': 'r3',
                    'src_itf': 3,
                    'dst_itf': 1
                },
                {
                    'src_node': 'r2',
                    'dst_node': 'r3',
                    'src_itf': 3,
                    'dst_itf': 2
                },
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
        nodes = self.topo['node']
        for node in nodes:
            if node['name'] == node_name:
                return node
        return None

    def get_node_ip(self, node_name, interface_id):
        node = self.get_node_info(node_name)
        if node is None:
            return None
        for interface in node['interface']:
            if interface['id'] == interface_id:
                return interface['ip']
        return None

    def get_host_name_by_interface(self, addr):
        for node in self.topo['node']:
            if node['type'] == 'host' and addr == node['ip']:
                return node['name']
            elif node['type'] == 'router':
                for interface in node['interface']:
                    if interface['ip'] == addr:
                        return node['name']
        return None
