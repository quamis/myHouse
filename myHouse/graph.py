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
    
    def gatherData(self, args, step=1):
        keys = {}
        offers = {}
        prices = {}
        
        for day in range(1, 30, step):
            args['dtadd_min'] = day
            args['dtadd_max'] = day-step
            
            ckey=str(int(time.time()/(60*60*24)))+str(hash(repr(sorted(args.items()))))
            data = self.cache.get(ckey)
            if data is None:
                self.stats.setargs(args)
                data = self.stats.raw()
                self.cache.set(ckey, data)
            
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
        args = self.args
        
        (keys1, offers1, prices1) = self.gatherData(args, 1)
        (keys7, offers7, prices7) = self.gatherData(args, 7)
        
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
            plt.plot( splines_offers1[k]['x'], splines_offers1[k]['y'], color="#6666cc", antialiased=True )
            plt.plot( range(0, len(offers1[k])), offers1[k], color="#2222cc", marker='x', linestyle='None', )
            plt.plot( splines_offers7[k]['x'], splines_offers7[k]['y'], color="#880000", antialiased=True, linewidth=2, linestyle="dotted" )
            
            plt.legend(['offers'])
            
            plt.xlabel('add day')
            plt.ylabel("%s offers" % ( k ))
            plt.title(k)
            plt.grid(True)
            
            plt.subplot(2, 1, 2)
            plt.fill_between( splines_prices1[k]['x'], splines_prices1[k]['y'], color="#66cc66", antialiased=True, alpha=0.25, linewidth=2 )
            plt.plot( splines_prices1[k]['x'], splines_prices1[k]['y'], color="#66cc66", antialiased=True, linewidth=2 )
            plt.plot( range(0, len(prices1[k])), prices1[k], color="#228822", marker='x', linestyle='None', )
            plt.plot( splines_prices7[k]['x'], splines_prices7[k]['y'], color="#880000", antialiased=True, linewidth=2, linestyle="dotted" )
            
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

cache = CACHE("graph")
obj = Graph({
    'type': 'default',
    'subtype': 'default',
    'category': ['case-vile'],
    #'category': ['case-vile', 'apt-3-cam'],
}, cache)

obj.display()
