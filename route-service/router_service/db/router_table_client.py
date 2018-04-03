#encoding:utf-8
import os
import json
import time
from tinydb import TinyDB, where
class RouterTableClient:
    '''a class to store the forwarding table for each router'''
    def __init__(self, router_name):
        self.router_db = TinyDB(router_name + '.data')
        self.router_name = router_name

    def get_forwarding_table(self):
        '''retrieve the forwarding table for this router '''
        return self._process_read_router_table_db()

    def get_router_table_by_name(self, router_name):
        '''retrieve the forwarding table with the given name'''
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
                    # if the data received have smaller ttl, then the table needs to be updated
                    if data['ttl'] < forwarding_item['ttl']:
                        need_update = True
                        forwarding_item['ttl'] = data['ttl']
                        forwarding_item['next_hop'] = data['next_hop']
            # if no item in the table, add a new one
            if has_item is False:
                router_table_db['item'].append(data)
                need_update = True

            if need_update:
                self.update_router_db_from_tinydb(router_table_db['item'])
        # if no routers in the table, add a new one with current router name
        if has_routers is False:
            add_router_item = {
                'name': router_name,
                'item': [data]
            }
            self.add_router_db_from_tinydb(add_router_item)

    def get_router_db_from_tinydb(self):
        '''retrieve data from db file'''
        db_data = self.router_db.all()
        if len(db_data) > 0:
            return db_data[0]
        else:
            return {}

    def update_router_db_from_tinydb(self, prams):
        '''update the current router db'''
        self.router_db.update({'item': prams}, where('name') == self.router_name)

    def add_router_db_from_tinydb(self, prams):
        print "****router_db.insert", prams
        self.router_db.insert(prams)

