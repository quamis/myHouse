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
            
    def printItem(self, data, data_contacts, data_extracted):
        sys.stdout.write((
                "[% 9s]%s %s\n"
                "  %s\n"
                "  % 7s EUR, \tid: %s (add:%s, upd:%s)\n") % (
                data[0], 
                "#[%s]"%(data[6]) if data[6]!=None and data[6]!="" else "",
                data[2], 
                data[3], 
                locale.format("%.*f", (0, data[4]), True),
                data[5],
                datetime.datetime.fromtimestamp(data[7]).strftime('%Y-%m-%d'), 
                datetime.datetime.fromtimestamp(data[8]).strftime('%Y-%m-%d')  ))
            
        if data_extracted:
            extr = {}
            # make the list associative
            for k in data_extracted:
                extr[k[0]] = k[1]
            
            surf = collections.OrderedDict()
            surf['surface_total'] =         self.printRow_extraData('surface',     extr, 'surface_total',         'supraf. tot: %dmp')
            surf['surface_built'] =         self.printRow_extraData('surface',     extr, 'surface_built',         'constr: %dmp')
            surf['price_per_mp_built'] =     self.printRow_extraData('surface',     extr, 'price_per_mp_built', '%dEUR/mp', 'float')
            surf['price_per_mp_surface'] =     self.printRow_extraData('surface',     extr, 'price_per_mp_surface','%dEUR/mp', 'float')
            surf['rooms'] =                 self.printRow_extraData('rooms',     extr, 'rooms',                 '%d camere')
            
            if surf:
                sys.stdout.write("      %s\n" % (", ".join(filter(None, surf.values()))))
            
            
            hist = collections.OrderedDict()
            hist['location'] =                         self.printRow_extraData('location', extr, 'location',             'in %s', 'location')
            hist['year_built'] =                     self.printRow_extraData('year',     extr, 'year_built',         'constr in: %d', 'year')
            
            if hist:
                sys.stdout.write("      %s\n" % (", ".join(filter(None, hist.values()))))
            
            
            pre = "UNSTRUCTURED DATA: "
            for k in data_extracted:
                if k[0] not in surf.keys() and k[0] not in hist.keys():
                    sys.stdout.write("%s" % (pre))
                    sys.stdout.write("%s: %s, " % (k[0], k[1]))
                    pre = ""
                    
        if data_contacts:
            for k in data_contacts:
                if k[0]=="phone":
                    sys.stdout.write("      %s: %s" % (k[0], re.sub("(.+)([0-9]{3})([0-9]{4})$", r'\1.\2.\3', k[1])))
                else:
                    sys.stdout.write("      %s: %s" % (k[0], k[1]))
                    
        sys.stdout.write("\n\n")