# -*- coding: utf-8 -*-

import stats.base.base as base
import time
import datetime
import numpy
import sys, locale 
 

class Stats(base.Stats):
    def precheck(self):
        if self.args.subtype=='default':
            self.args.subtype = 'day'
            
        if self.args.subtype not in ('day', 'week', 'month'):
            raise Exception("Invalid subtype '%s'" % (self.args.subtype))
    
    def group(self, rows):
        stats = {}
        stats['addDate'] = {}
        stats['updateDate'] = {}
        
        if self.args.subtype == "week":
            stats['addDate:week'] = {}
            stats['updateDate:week'] = {}
            
        if self.args.subtype == "month":
            stats['addDate:month'] = {}
            stats['updateDate:month'] = {}
        
        rows = self.db.selectAll(self.getSQL())
        for row in rows:
            row = self.getItem(row[0], ('data'))
            addDate = datetime.datetime.fromtimestamp(row['addDate']).strftime('%Y-%m-%d')
            updateDate = datetime.datetime.fromtimestamp(row['updateDate']).strftime('%Y-%m-%d')
            
            stats['addDate'] = self._incDict(stats['addDate'], addDate)
            stats['updateDate'] = self._incDict(stats['updateDate'], updateDate)
            
            if self.args.subtype == "week":
                addDate = datetime.datetime.fromtimestamp(row['addDate']).strftime('%Y-%U')
                updateDate = datetime.datetime.fromtimestamp(row['updateDate']).strftime('%Y-%U')
                
                stats['addDate:week'] = self._incDict(stats['addDate:week'], addDate)
                stats['updateDate:week'] = self._incDict(stats['updateDate:week'], updateDate)
                
            if self.args.subtype == "month":
                addDate = datetime.datetime.fromtimestamp(row['addDate']).strftime('%Y-%m')
                updateDate = datetime.datetime.fromtimestamp(row['updateDate']).strftime('%Y-%m')
                
                stats['addDate:month'] = self._incDict(stats['addDate:month'], addDate)
                stats['updateDate:month'] = self._incDict(stats['updateDate:month'], updateDate)
            
        return stats

    def doprint(self, stats):
        if self.args.subtype == "day":
            allKeys = list(set(stats['addDate'].keys() + stats['updateDate'].keys()))
            fmt = "%-12s: % 9s % 9s"
            print (fmt + " offers") % ("date", "added", "updated")
                        
            for key in sorted(allKeys):
                print fmt % (key,
                    locale.format("%.*f", (0, stats['addDate'][key]), True)     if key in stats['addDate']         else 0,
                    locale.format("%.*f", (0, stats['updateDate'][key]), True)     if key in stats['updateDate']     else 0,)
                
        elif self.args.subtype == "week":
            allKeys = list(set(stats['addDate:week'].keys() + stats['updateDate:week'].keys()))
            fmt = "%-12s: % 9s % 9s"
            print (fmt + " offers") % ("date", "added", "updated")
                        
            for key in sorted(allKeys):
                print fmt % (key,
                    locale.format("%.*f", (0, stats['addDate:week'][key]), True)         if key in stats['addDate:week']     else 0,
                    locale.format("%.*f", (0, stats['updateDate:week'][key]), True)     if key in stats['updateDate:week']     else 0,)
                
        elif self.args.subtype == "month":
            allKeys = list(set(stats['addDate:month'].keys() + stats['updateDate:month'].keys()))
            fmt = "%-12s: % 9s % 9s"
            print (fmt + " offers") % ("date", "added", "updated")
                        
            for key in sorted(allKeys):
                print fmt % (key,
                    locale.format("%.*f", (0, stats['addDate:month'][key]), True)         if key in stats['addDate:month']     else 0,
                    locale.format("%.*f", (0, stats['updateDate:month'][key]), True)     if key in stats['updateDate:month'] else 0,)
        