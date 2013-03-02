#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, codecs
import datetime
import os, sys, importlib

from DB import DB
import logging
import locale
import argparse
import offerStats

import numpy as np
import matplotlib.pyplot as plt

class Graph(object):
    def __init__(self, args):
        self.args = args
        self.db = DB("../db/main.sqlite")
        self.stats = offerStats.Stats(self.db, self.args)
    
    def display(self):
        args = self.args
        
        stats = {}
        for day in xrange(1, 30, 1):
            args['dtadd_min'] = day
            args['dtadd_max'] = day-1
            data = self.stats.raw()
            
            #for (k, d) in data['categories'].iteritems():
            for (k, d) in data['price_per_category:std'].iteritems():
                if k not in stats:
                    stats[k] = []
                
                if d:
                    stats[k].append(d)
                else:
                    stats[k].append(0)
        
        #print stats
        #exit()
        
        
        plt.figure(1)                # the first figure
        # The subplot() command specifies numrows, numcols, fignum where fignum ranges from 1 to numrows*numcols.
        
        idx = 0
        for (k, d) in stats.iteritems():
            idx+=1
            plt.subplot(len(stats), 1, idx)             # the first subplot in the first figure
            plt.xlabel('add day')
            plt.ylabel('offers')
            plt.title(k)
            plt.grid(True)
            plt.plot(d)
        
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=1)
        plt.show()


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

obj = Graph({
    'type': 'default',
    'subtype': 'default',
    # 'category': ['case-vile'],
})

obj.display()
