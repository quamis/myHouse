# -*- coding: utf-8 -*-

import time, codecs
import datetime
import os, sys, importlib

from DB import DB
import logging
import locale
import numpy 

class Stats(object):
    def __init__(self, db, args):
        self.db = db
        self.args = args
    
    def getItem(self, idStr, fields=('data', 'data_contacts', 'data_extracted')):
        data = {}
        data_contacts = {}
        data_extracted = {}
        if 'data' in fields:
            keys = ('id', 'internalStatus', 'userStatus', 'category', 'source', 'url', 'description', 'price', 'location', 'rooms', 'year_built', 'surface_total', 'surface_built', 'price_per_mp_total', 'price_per_mp_built', 'addDate', 'updateDate')
            values = self.db.selectAll("SELECT `" + "`, `".join(keys) + "` FROM `data` WHERE `id`='%s'" % (idStr))[0]
            data = dict(zip(keys, values))
            
        if 'data_contacts' in fields:
            data_contacts = self.db.selectAll("SELECT `key`, `value` FROM `data_contacts` WHERE `idOffer`='%s' ORDER BY `key` ASC, `value` ASC" % (idStr))
            data['contacts'] = data_contacts
            
        if 'data_extracted' in fields:
            dt = self.db.selectAll("SELECT `key`, `value` FROM `data_extracted` WHERE `idOffer`='%s' ORDER BY `key`" % (idStr))
            for d in dt:
                data_extracted[d[0]] = d[1]
            data['extracted'] = data_extracted
        
        return data
    
    def getSQL(self):
        sql = "SELECT `id` FROM `data` WHERE 1"
        
        if 'category' in self.args and self.args['category']:
            sql += "/*category*/ AND( 0 "
            for k in self.args['category']:
                sql += " OR `category`='%s'" % (k)
            sql += ")"
            
        if 'source' in self.args and self.args['source']:
            sql += "/*source*/ AND( 0 "
            for k in self.args['source']:
                sql += " OR `source`='%s'" % (k)
            sql += ")"
            
        if 'status' in self.args and self.args['status']:
            sql += "/*userStatus*/ AND (`userStatus`='%s')" % (self.args['status'])
            
        if 'dtadd_min' in self.args and (self.args['dtadd_min']):
            dt = datetime.date.today() - datetime.timedelta(days=self.args['dtadd_min'])
            sql += " AND `addDate`>%d" % (time.mktime(dt.timetuple()))
        if 'dtadd_max' in self.args and self.args['dtadd_max']:
            dt = datetime.date.today() - datetime.timedelta(days=self.args['dtadd_max'])
            sql += " AND `addDate`<%d" % (time.mktime(dt.timetuple()))
        
        if 'dtupd_min' in self.args and self.args['dtupd_min']:
            dt = datetime.date.today() - datetime.timedelta(days=self.args['dtupd_min'])
            sql += " AND `updateDate`>%d" % (time.mktime(dt.timetuple()))
        if 'dtupd_max' in self.args and self.args['dtupd_max']:
            dt = datetime.date.today() - datetime.timedelta(days=self.args['dtupd_max'])
            sql += " AND `updateDate`<%d" % (time.mktime(dt.timetuple()))
            
        if 'price_min' in self.args and self.args['price_min']:
            sql += " AND `price`>%d" % (self.args['price_min'])
        if 'price_max' in self.args and self.args['price_max']:
            sql += " AND `price`<=%d" % (self.args['price_max'])
         
        #sql += " ORDER BY `price` ASC, `location` ASC"
        #print sql
        
        return sql
    
    def roundInInterval(self, value, interval):
        for v in interval:
            if value < v[0]:
                value = int(round(value / v[1]) * v[1])
                return value
                
        return None
    
    def _incDict(self, data, key):
        if key not in data:
            data[key] = 0
        data[key] += 1
        return data

    def precheck(self):
        pass
        

    def gather(self):
        return self.db.selectAll(self.getSQL())
    
    def group(self, rows):
        return rows
        
    def doprint(self, stats):
        print stats
            