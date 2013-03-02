#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, codecs
import datetime
import os, sys, importlib

from DB import DB
import logging
import locale
import argparse
import numpy 


class Stats(object):
    def __init__(self, db, args):
        self.db = db
        self.args = args
        self.stats = None
        self.doimport()
    
    def doimport(self):
        if self.stats is None:
            module = importlib.import_module("stats." + self.args['type'] + ".base")
            self.stats = module.Stats(self.db, self.args)
            self.stats.precheck()
      
    def raw(self):
        return self.stats.group( self.stats.gather() )
        
    def doprint(self):
        self.stats.doprint( self.raw() )
        
        sys.stdout.write("\n")

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter gatherer results.')
    parser.add_argument('-source', dest='source', action='append', type=str, default=None, help='TODO')
    parser.add_argument('-category', dest='category', action='append', type=str, default=None, help='TODO')
    parser.add_argument('-status', dest='status', action='store', type=str, default=None, help='TODO')
    parser.add_argument('-dtadd_min', dest='dtadd_min', action='store', type=float, default=None, help='TODO')
    parser.add_argument('-dtadd_max', dest='dtadd_max', action='store', type=float, default=None, help='TODO')
    parser.add_argument('-dtupd_min', dest='dtupd_min', action='store', type=float, default=None, help='TODO')
    parser.add_argument('-dtupd_max', dest='dtupd_max', action='store', type=float, default=None, help='TODO')
    parser.add_argument('-price_min', dest='price_min', action='store', type=float, default=None, help='TODO')
    parser.add_argument('-price_max', dest='price_max', action='store', type=float, default=None, help='TODO')
    
    parser.add_argument('--type', dest='type', action='store', type=str, default="default", help='TODO')
    parser.add_argument('--subtype', dest='subtype', action='store', type=str, default="default", help='TODO')
    args = parser.parse_args()
    
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    locale.setlocale(locale.LC_NUMERIC, '')
    
    # change the output encoding to utf8
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)
    
    db = DB("../db/main.sqlite")
    
    stats = Stats(db, vars(args))
    stats.doprint()
