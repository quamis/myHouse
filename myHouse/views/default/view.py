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


class newView(views.base.view.baseView):
    def __init__(self, args):
        super(newView, self).__init__(args)
    
    def printFooter(self, stats):
        print "\n\nTotal: %d" % (stats['total'])
        views.base.view.baseView.printFooter(self, stats)
            
    def printItem(self, data):
        sys.stdout.write((
                "[% 9s]%s %s\n"
                "  %s\n"
                "  % 7s EUR, \tid: %s (add:%s, upd:%s)\n") % (
                data['category'], 
                "#[%s]"%(data['userStatus']) if data['userStatus'] else "",
                data['description'], 
                data['url'], 
                locale.format("%.*f", (0, data['price']), True),
                data['id'],
                datetime.datetime.fromtimestamp(data['addDate']).strftime('%Y-%m-%d'), 
                datetime.datetime.fromtimestamp(data['addDate']).strftime('%Y-%m-%d')  ))
            
        # make the list associative
        surf = collections.OrderedDict()
        surf['surface_total'] =         self.printRow_extraData('surface',     data, 'surface_total',         'supraf. tot: %dmp')
        surf['surface_built'] =         self.printRow_extraData('surface',     data, 'surface_built',         'constr: %dmp')
        surf['price_per_mp_built'] =    self.printRow_extraData('surface',     data, 'price_per_mp_built',    '%dEUR/mp', 'float')
        surf['price_per_mp_surface'] =  self.printRow_extraData('surface',     data, 'price_per_mp_surface',  '%dEUR/mp', 'float')
        surf['rooms'] =                 self.printRow_extraData('rooms',       data, 'rooms',                 '%d camere')
        
        if surf:
            sys.stdout.write("      %s\n" % (", ".join(filter(None, surf.values()))))
        
        
        hist = collections.OrderedDict()
        hist['location'] =              self.printRow_extraData('location', data, 'location',             'in %s', 'location')
        hist['year_built'] =            self.printRow_extraData('year',     data, 'year_built',           'constr in: %d', 'year')
        
        if hist:
            sys.stdout.write("      %s\n" % (", ".join(filter(None, hist.values()))))
        
        
        """
        if 'extracted' in data:
            pre = "UNSTRUCTURED DATA: "
            for k,v in data['extracted'].items():
                sys.stdout.write("%s" % (pre))
                sys.stdout.write("%s: %s, " % (k, v))
                pre = ""
        """
        
                    
        if 'contacts' in data:
            for k in data['contacts']:
                if k[0]=="phone":
                    sys.stdout.write("      %s: %s" % (k[0], re.sub("(.+)([0-9]{3})([0-9]{4})$", r'\1.\2.\3', k[1])))
                else:
                    sys.stdout.write("      %s: %s" % (k[0], k[1]))
                    
        sys.stdout.write("\n\n")