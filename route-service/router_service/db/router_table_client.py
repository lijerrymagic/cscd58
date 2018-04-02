#encoding:utf-8
import os
import json
import time
from tinydb import TinyDB, where
class RouterTableClient:
    '''a class to store the forwarding table for each router'''
    def __init__(self, router_name):
        #self.dbfile = "/home/" + router_name + ".txt"
        self.router_db = TinyDB(router_name + '.data')
        self.router_name = router_name
        #self.create_db_file()

    def get_forwarding_table(self):
        '''retrieve the forwarding table for this router '''
        return self._process_read_router_table_db()

    def get_router_table_by_name(self, router_name):
        db_data = self._process_read_router_table_db()
        print "****db:", db_data
        return db_data

    def update_router_table_by_name(self, router_name, router_items):
        self._process_write_router_table_db(router_name, router_items)

    def _process_read_router_table_db(self):
        return self.get_router_db_from_tinydb()

    def _process_write_router_table_db(self, router_name, data):
        has_routers = False
        router_table_db = self._process_read_router_table_db()

        print "**********get router from db to update:", router_table_db

        if 'name' in router_table_db and router_table_db['name'] == router_name:
            has_routers = True
            has_item = False
            need_update = False
            for forwarding_item in router_table_db['item']:

                if forwarding_item['nw_dst'] == data['nw_dst']:
                    has_item = True
                    if data['ttl'] < forwarding_item['ttl']:
                        need_update = True
                        forwarding_item['ttl'] = data['ttl']
                        forwarding_item['next_hop'] = data['next_hop']

            if has_item is False:
                router_table_db['item'].append(data)
                need_update = True

            if need_update:
                self.update_router_db_from_tinydb(router_table_db['item'])

        if has_routers is False:
            add_router_item = {
                'name': router_name,
                'item': [data]
            }
            self.add_router_db_from_tinydb(add_router_item)

    def create_db_file(self):
        if not os.path.exists(self.dbfile):
            db_file = open(self.dbfile, 'w')
            db_file.close()
            print self.dbfile + " created."
        else:
            print self.dbfile + " already existed."
        return

    def read_db_file(self):
        with open(self.dbfile, 'r') as db_file:
            db_data = db_file.read()
        if db_data:
            db_data = json.loads(db_data)
        else:
            db_data = None
        db_file.close()
        return db_data

    def write_db_file(self, data):
        with open(self.dbfile, 'w') as db_file:
            db_file.write(json.dumps(data))
        db_file.close()

    def get_router_db_from_tinydb(self):
        db_data = self.router_db.all()
        if len(db_data) > 0:
            return db_data[0]
        else:
            return {}

    def update_router_db_from_tinydb(self, prams):
        self.router_db.update({'item': prams}, where('name') == self.router_name)

    def add_router_db_from_tinydb(self, prams):
        print "****router_db.insert", prams
        self.router_db.insert(prams)

