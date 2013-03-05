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
        self.args = args
        self.db = DB("../db/main.sqlite")
        self.stats = offerStats.Stats(self.db, self.args)
        self.cache = cache
    
    def display(self):
        args = self.args
        
        keys = {}
        offers = {}
        prices = {}
        splines_offers = {}
        splines_prices = {}
        
        for day in range(1, 30, 1):
            args['dtadd_min'] = day
            args['dtadd_max'] = day-1
            
            ckey=str(int(time.time()/(60*60*24)))+str(hash(repr(sorted(args.items()))))
            data = self.cache.get(ckey)
            if data is None:
                self.stats.setargs(args)
                data = self.stats.raw()
                self.cache.set(ckey, data)
                self.cache.flushRandom(1)
            
            for (k, __) in data['categories'].iteritems():
            #for (k, d) in data['price_per_category:std'].iteritems():
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
                    prices[k].append(data['price_per_category:std'][k])
                else:
                    prices[k].append(0)

        for (k, __) in keys.iteritems():
            splines_offers[k] = { }
            splines_offers[k]['tck'] = interpolate.splrep(np.arange(1,30), offers[k], s=0)
            splines_offers[k]['x'] = np.arange(1, 29, 0.15)
            splines_offers[k]['y'] = interpolate.splev(splines_offers[k]['x'], splines_offers[k]['tck'], der=0)
            
        for (k, __) in keys.iteritems():
            splines_prices[k] = { }
            splines_prices[k]['tck'] = interpolate.splrep(np.arange(1,30), prices[k], s=0)
            splines_prices[k]['x'] = np.arange(1, 29, 0.15)
            splines_prices[k]['y'] = interpolate.splev(splines_prices[k]['x'], splines_prices[k]['tck'], der=0)
            
        #print stats['apt-2-cam']
        #print splines_prices['apt-2-cam']['x']
        #print splines_prices['apt-2-cam']['y']
        #print offers
        #exit()
        
        
        plt.figure(1)                # the first figure
        # The subplot() command specifies numrows, numcols, fignum where fignum ranges from 1 to numrows*numcols.
        
        idx = 0
        for (k, __) in keys.iteritems():
            idx+=1
            plt.subplot(len(offers), 1, idx)             # the first subplot in the first figure
            plt.xlabel('add day')
            plt.ylabel('offers')
            plt.title(k)
            plt.grid(True)
            
            print k
            print offers[k]
            
            plt.fill_between( splines_offers[k]['x'], splines_offers[k]['y'], color="#6666cc", antialiased=True, alpha=0.25 )
            plt.fill_between( splines_prices[k]['x'], splines_prices[k]['y'], color="#66cc66", antialiased=True, alpha=0.25, linewidth=2 )
            
            plt.plot( splines_offers[k]['x'], splines_offers[k]['y'], color="#6666cc", antialiased=True )
            plt.plot( splines_prices[k]['x'], splines_prices[k]['y'], color="#66cc66", antialiased=True, linewidth=2 )
            
            plt.plot( range(1, 30), offers[k], color="#6666cc", marker='x', linestyle='None', )
            plt.plot( range(1, 30), prices[k], color="#66cc66", marker='x', linestyle='None', )
            
            plt.legend(['offers', 'prices'])
        
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=1)
        plt.show()


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

cache = CACHE("graph")
obj = Graph({
    'type': 'default',
    'subtype': 'default',
    'category': ['apt-2-cam'],
}, cache)

obj.display()
