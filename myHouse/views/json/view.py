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
        
    
    def printItem(self, data, data_contacts, data_extracted):
        output = collections.OrderedDict()
        extr = {}            
        if data_extracted:
            # make the list associative
            for k in data_extracted:
                extr[k[0]] = k[1]
                
        output['data01'] = collections.OrderedDict()
        output['data01']['location'] =               self.printRow_extraData('location', extr, 'location',             'in %s', 'location')
        output['data01']['year_built'] =             self.printRow_extraData('year',     extr, 'year_built',         'constr in: %d', 'year')
        output['data01']['surface_total'] =          self.printRow_extraData('surface',     extr, 'surface_total',         'supraf. tot: %dmp')
        output['data01']['surface_built'] =          self.printRow_extraData('surface',     extr, 'surface_built',         'constr: %dmp')
        output['data01']['price_per_mp_built'] =     self.printRow_extraData('surface',     extr, 'price_per_mp_built', '%dEUR/mp', 'float')
        output['data01']['price_per_mp_surface'] =   self.printRow_extraData('surface',     extr, 'price_per_mp_surface','%dEUR/mp', 'float')
        output['data01']['rooms'] =                  self.printRow_extraData('rooms',     extr, 'rooms',                 '%d camere')

        output['data'] = collections.OrderedDict()
        output['data']['price'] = self.format_number(data[4])
        output['data']['text'] = unicode(data[2])
        output['data']['category'] = unicode(data[0])
        output['data']['id'] = unicode(data[5])
        output['data']['status'] = unicode(data[6])
        output['data']['href'] = unicode(data[3])
        output['data']['addDate'] = self.format_timestamp(data[7])
        output['data']['updateDate'] = self.format_timestamp(data[8])
        
        output['unstructured'] = collections.OrderedDict()
        for k in data_extracted:
            if k[0] not in output['data01'].keys():
                output['unstructured'][k[0]] = k[1]
                    
        output['contacts'] = collections.OrderedDict()
        output['contacts']['phone'] = []
        output['contacts']['misc'] = []
        if data_contacts:
            for k in data_contacts:
                if k[0]=="phone":
                    output['contacts']['phone'].append(re.sub("(.+)([0-9]{3})([0-9]{4})$", r'\1.\2.\3', k[1]))
                else:
                    output['contacts']['misc'].append(k[1])
                    
        self.items.append(output)
