# -*- coding: utf-8 -*-

import stats.base.base as base
import time
import datetime
import numpy
import sys, locale 
 

class Stats(base.Stats):
    def precheck(self):
        if self.args['subtype']=='default':
            self.args['subtype'] = 'full'
            
        if self.args['subtype'] not in ('full', 'simple'):
            raise Exception("Invalid subtype '%s'" % (self.args['subtype']))
    
    def group(self, rows):
        stats = {}
        stats[None] = 0
        
        rows = self.db.selectAll(self.getSQL())
        for row in rows:
            row = self.getItem(row[0], ('data'))
            
            if row['year_built']:
                yr = row['year_built']
                if self.args['subtype'] == "simple":
                    yr = "+++"
                    
                if yr not in stats:
                    stats[yr] = 0
                stats[yr] += 1
            else:
                stats[None] += 1
            
        return stats

    def doprint(self, stats):
        fmt = "%04s: % 5s"
        print (fmt + " in year") % ("year", "offers")
                    
        for key in sorted(stats.keys()):
            print fmt % ("None" if key is None else key,
                locale.format("%.*f", (0, stats[key]), True))