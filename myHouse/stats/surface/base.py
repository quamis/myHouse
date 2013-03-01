# -*- coding: utf-8 -*-

import stats.base.base as base
import time
import datetime
import numpy
import sys, locale 
 

class Stats(base.Stats):
    def precheck(self):
        if self.args['subtype']=='default':
            self.args['subtype'] = 'total'
            
        if self.args['subtype'] not in ('total', 'built'):
            raise Exception("Invalid subtype '%s'" % (self.args['subtype']))
    
    def group(self, rows):
        stats = {}
        stats[None] = 0
        
        rows = self.db.selectAll(self.getSQL())
        for row in rows:
            row = self.getItem(row[0], ('data'))
            
            surf = None
            if self.args['subtype'] == "total":
                if row['surface_total']:
                    surf = row['surface_total']
                    
            if self.args['subtype'] == "built":
                if row['surface_built']:
                    surf = row['surface_built']
            
            # round the surface to 10mp increments
            if surf:
                if "apt-2-cam" in self.args['category']:
                    surf = self.roundInInterval(float(surf), ((20, 5), (150, 10), (500, 50)))
                elif "apt-3-cam" in self.args['category'] or "apt-4-cam" in self.args['category']:
                    surf = self.roundInInterval(float(surf), ((20, 5), (250, 10), (500, 50)))
                else:
                    surf = self.roundInInterval(float(surf), ((30, 10), (750, 50), (2500, 100), (10000, 500), (100000, 10000), (10000000, 100000)))
                    
            
            if surf not in stats:
                stats[surf] = 0
            stats[surf] += 1

        return stats

    def doprint(self, stats):
        fmt = "%+10s: % 8s"
        print (fmt) % ("surface(mp)", "offers")
        
        def sort_fcn(x):
            if x:
                return float(x)
            
            return x
        
        for key in sorted(stats.keys(), key=sort_fcn):
            print fmt % ("None" if key is None else locale.format("%.*f", (0, key), True),
                locale.format("%.*f", (0, stats[key]), True))