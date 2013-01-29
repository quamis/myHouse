#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import json
import collections

class Import:
    def __init__(self, db, args):
        self.db = db
        self.args = args
        self.inputData = []
        
    def getItem(self, idStr, fields=('data', 'data_contacts', 'data_extracted')):
        data = {}
        data_contacts = {}
        data_extracted = {}
        if 'data' in fields:
            keys = ('id', 'internalStatus', 'userStatus', 'category', 'source', 'url', 'description', 'price', 'location', 'rooms', 'year_built', 'surface_total', 'surface_built', 'price_per_mp_total', 'price_per_mp_built', 'addDate', 'updateDate')
            values = self.db.selectAll("SELECT `"+"`, `".join(keys)+"` FROM `data` WHERE `id`='%s'" %( idStr ))[0]
            data = dict( zip(keys, values) )
            
        if 'data_contacts' in fields:
            data_contacts = self.db.selectAll("SELECT `key`, `value` FROM `data_contacts` WHERE `idOffer`='%s' ORDER BY `key` ASC, `value` ASC" %(idStr))
            data['contacts'] = data_contacts
            
        if 'data_extracted' in fields:
            dt = self.db.selectAll("SELECT `key`, `value` FROM `data_extracted` WHERE `idOffer`='%s' ORDER BY `key`" %(idStr))
            for d in dt:
                data_extracted[d[0]] = d[1]
            data['extracted'] = data_extracted
        
        return data


    def run(self):
        if self.args.jsonFile:
            js = json.loads(open(self.args.jsonFile).read())
            
            targetField = self.args.targetField
            
            for key, value in js.items():
                self.inputData.append({ 'id':key, targetField:value })
                
                
        
        for item in self.inputData:
            if self.db.itemExists("data", item['id']):
                self.db.itemUpdate("data", item)
                print "Item '%s' updated" % (item['id'])
            else:
                print "Item '%s' not found" % (item['id'])
                
        self.db.close()

    
parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-jsonFile',    dest='jsonFile',        action='store',     type=str, default=None,        help='TODO')
parser.add_argument('-targetField', dest='targetField',     action='store',     type=str, default=None,        help='TODO')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')
    
# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

db = DB("../db/main.sqlite")

importer = Import(db, args)
importer.run()

raise SystemExit
