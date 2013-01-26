import views.base.view

import os, sys, time, codecs, importlib
import re
from datetime import date, timedelta

from DB import DB
from CACHE import CACHE
import logging
import locale
import argparse
import datetime
import csv
import collections
import json


class newView(views.base.view.baseView):
    def __init__(self, args):
        super(newView, self).__init__(args)
        self.items = []
    
    def printFooter(self, stats):
        print json.dumps(self.items)
        #print json.dumps(self.items, indent=4, separators=(',', ': '))
        
    
    def printItem(self, data):
        output = collections.OrderedDict()
        output['data'] = collections.OrderedDict()
        output['data']['price'] =       self.format_number(data['price'])
        output['data']['description'] = data['description']
        output['data']['category'] =    data['category']
        output['data']['id'] =          data['id']
        output['data']['userStatus'] =  data['userStatus']
        output['data']['href'] =        data['url']
        output['data']['addDate'] =     self.format_timestamp(data['addDate'])
        output['data']['updateDate'] =  self.format_timestamp(data['updateDate'])
        
        output['location'] =               self.printRow_extraData('location', data, 'location',            'in %s',        'location')
        output['year_built'] =             self.printRow_extraData('year',     data, 'year_built',          'constr in: %d','year')
        output['surface_total'] =          self.printRow_extraData('surface',  data, 'surface_total',       'supraf. tot: %dmp')
        output['surface_built'] =          self.printRow_extraData('surface',  data, 'surface_built',       'constr: %dmp')
        output['price_per_mp_built'] =     self.printRow_extraData('surface',  data, 'price_per_mp_built',  '%dEUR/mp',     'float')
        output['price_per_mp_surface'] =   self.printRow_extraData('surface',  data, 'price_per_mp_surface','%dEUR/mp',     'float')
        output['rooms'] =                  self.printRow_extraData('rooms',    data, 'rooms',               '%d camere')
        
        output['unstructured'] = collections.OrderedDict()
        if 'extracted' in data:
            for k in data['extracted']:
                if k[0] not in output['data01'].keys():
                    output['unstructured'][k[0]] = k[1]
                    
        output['contacts'] = collections.OrderedDict()
        output['contacts']['phone'] = []
        output['contacts']['misc'] = []
        if 'contacts' in data and data['contacts']:
            for k in data['contacts']:
                if k[0]=="phone":
                    output['contacts']['phone'].append(re.sub("(.+)([0-9]{3})([0-9]{4})$", r'\1.\2.\3', k[1]))
                else:
                    output['contacts']['misc'].append(k[1])
                    
        self.items.append(output)
