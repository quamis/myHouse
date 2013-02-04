# -*- coding: utf-8 -*-

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
        output['price'] =       self.format_number(data['price'])
        output['description'] = data['description']
        output['category'] =    data['category']
        output['id'] =          data['id']
        output['userStatus'] =  data['userStatus']
        output['suggestedStatus'] =  data['suggestedStatus']
        output['url'] =         data['url']
        output['addDate'] =     self.format_timestamp(data['addDate'])
        output['updateDate'] =  self.format_timestamp(data['updateDate'])
        
        output['location'] =               self.printRow_extraData('location', data, 'location',            'in %s',        'location')
        output['year_built'] =             self.printRow_extraData('year',     data, 'year_built',          'constr in: %d','year')
        output['surface_total'] =          self.printRow_extraData('surface',  data, 'surface_total',       'supraf. tot: %dmp')
        output['surface_built'] =          self.printRow_extraData('surface',  data, 'surface_built',       'constr: %dmp')
        output['price_per_mp_built'] =     self.printRow_extraData('surface',  data, 'price_per_mp_built',  '%dEUR/mp',     'float')
        output['price_per_mp_surface'] =   self.printRow_extraData('surface',  data, 'price_per_mp_surface','%dEUR/mp',     'float')
        output['rooms'] =                  self.printRow_extraData('rooms',    data, 'rooms',               '%d camere')
        
        output['extracted'] = collections.OrderedDict()
        if 'extracted' in data:
            output['extracted'] = data['extracted']
        
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
