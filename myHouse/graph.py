#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, codecs
import datetime
import os, sys, importlib

from DB import DB
from CACHE import CACHE
import logging
import locale
import argparse
import offerStats

import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

class Graph(object):
    def __init__(self, args, cache):
        self.args = dict.copy(args)
        self.db = DB("../db/main.sqlite")
        self.stats = offerStats.Stats(self.db, { 'type': self.args['type'], 'subtype': self.args['subtype'], } )
        self.cache = cache
    
    def gatherData(self, args, step=1, maxInterval=-1):
        keys = {}
        offers = {}
        prices = {}

        if maxInterval==-1:
            self.stats.setargs(args)
            data = self.stats.raw()
            if 'timeSinceAppeared:max' in data:
                maxInterval = int(np.floor(data['timeSinceAppeared:max']))
        
        for day in range(0, maxInterval, step):
            args['dtadd_min'] = day+step
            args['dtadd_max'] = day
            
            ckey=str(int(time.time()/(60*60*24)))+str(hash(repr(sorted(args.items()))))
            data = self.cache.get(ckey)
            if data is None:
                logging.debug("Building stats for : %s" %( args ))
                self.stats.setargs(args)
                #self.stats.doimport()
                data = self.stats.raw()
                self.cache.set(ckey, data)
            
            for (k, __) in data['categories'].iteritems():
                if k not in keys:
                    keys[k] = True
                    
                if k not in offers:
                    offers[k] = []
                if k not in prices:
                    prices[k] = []
                
                if data['categories'][k]:
                    offers[k].append(data['categories'][k])
                else:
                    offers[k].append(0)
                    
                if data['price_per_category:std'][k]:
                    prices[k].append(data['price_per_category:median'][k])
                else:
                    prices[k].append(0)
                    
        self.cache.flushRandom(0.75)
        return (keys.keys(), offers, prices)
    
    def doInterpolate(self, data, lengthMultilpier=1):
        splines = { }
        data_len1 = len(data)

        splines['tck'] = interpolate.splrep(np.arange(0, data_len1), data, s=0)
        splines['x'] = np.arange(0, data_len1-1, 0.10/lengthMultilpier)
        splines['y'] = interpolate.splev(splines['x'], splines['tck'], der=0)
        splines['x'] = np.array(splines['x'])*lengthMultilpier
        
        #print "-> %d %d %d" % (len(splines['tck']), len(splines['x']), len(splines['y']))
        
        return splines

    def display(self):
        (keys1, offers1, prices1) = self.gatherData(dict.copy(self.args), 1, self.args['interval_max'])
        (keys7, offers7, prices7) = self.gatherData(dict.copy(self.args), 7, self.args['interval_max'])
        
        splines_offers1 = {}
        splines_prices1 = {}
        
        splines_offers7 = {}
        splines_prices7 = {}
        

        for k in keys1:
            splines_offers1[k] = self.doInterpolate(offers1[k])
            splines_prices1[k] = self.doInterpolate(prices1[k])
            
        for k in keys7:
            offers7[k] = np.array(offers7[k])/7
            
            splines_offers7[k] = self.doInterpolate(offers7[k], 7)
            splines_prices7[k] = self.doInterpolate(prices7[k], 7)
            
        self.cache.flushRandom(1)

        #print offers
        #print prices
        #exit()
        
        
        #plt.ion()
        idx = 0
        for k in keys1:
            idx+=1
            
            plt.figure(idx)
            
            plt.subplot(2, 1, 1)
            plt.fill_between( splines_offers1[k]['x'], splines_offers1[k]['y'], color="#6666cc", antialiased=True, alpha=0.25 )
            plt.plot( splines_offers1[k]['x'], splines_offers1[k]['y'], color="#8888cc", antialiased=True )
            plt.plot( range(0, len(offers1[k])), offers1[k], color="#4444cc", marker='x', linestyle='None', )
            plt.plot( splines_offers7[k]['x'], splines_offers7[k]['y'], color="#880000", antialiased=True, linewidth=2, linestyle="dashed" )
            
            plt.legend(['offers'])
            
            plt.xlabel('add day')
            plt.ylabel("%s offers" % ( k ))
            plt.title(k)
            plt.grid(True)
            
            plt.subplot(2, 1, 2)
            plt.fill_between( splines_prices1[k]['x'], splines_prices1[k]['y'], color="#66cc66", antialiased=True, alpha=0.25, linewidth=2 )
            plt.plot( splines_prices1[k]['x'], splines_prices1[k]['y'], color="#66cc66", antialiased=True, linewidth=2 )
            plt.plot( range(0, len(prices1[k])), prices1[k], color="#006600", marker='x', linestyle='None', )
            plt.plot( splines_prices7[k]['x'], splines_prices7[k]['y'], color="#880000", antialiased=True, linewidth=2, linestyle="dashed" )
            
            plt.legend(['prices'])
            
            plt.xlabel('add day')
            plt.ylabel("%s prices" % ( k ))
            plt.title(k)
            plt.grid(True)
            
            
        
        #plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=1)
        plt.show()
        
        
        #time.sleep(15)
        #plt.close('all')

    #def plot(self, data):
        
    
    
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

parser = argparse.ArgumentParser(description='Graph data')
parser.add_argument('-price_min', dest='price_min',         action='store',     type=float,     default=None,       help='TODO')
parser.add_argument('-price_max', dest='price_max',         action='store',     type=float,     default=None,       help='TODO')

parser.add_argument('-interval_max', dest='interval_max',   action='store',     type=str,     default="31",         help='TODO')
parser.add_argument('-category',  dest='category',          action='append',    type=str,     default=None,       help='TODO')
parser.add_argument('-source',    dest='source',            action='append',    type=str,     default=None,       help='TODO')

args = parser.parse_args()


cache = CACHE("graph")

a = {
    'type': 'default',
    'subtype': 'default',

    'interval_max': args.interval_max,
    'category': args.category,    
    'source':   args.source,
    'price_min':args.price_min, 
    'price_max':args.price_max,
}

if args.interval_max=="full":
    a['interval_max'] = -1
else:
    a['interval_max'] = int(args.interval_max)

obj = Graph(a, cache)

obj.display()
