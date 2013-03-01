# -*- coding: utf-8 -*-

import stats.base.base as base
import time
import numpy
import sys, locale 
 

class Stats(base.Stats):
    def group(self, rows):
        timestamp = time.time()
        
        stats = {}
        stats['source'] = {}
        stats['categories'] = {}
        stats['statuses'] = {}
        
        prices = {}
        alivePeriods = []
        timeSinceAppeared = []
        timeSinceDisappeared = []
        
        for row in rows:
            row = self.getItem(row[0], ('data'))
            if row['category'] not in stats['categories']:
                stats['categories'][row['category']] = 0
            stats['categories'][row['category']] += 1     

            if row['source'] not in stats['source']:
                stats['source'][row['source']] = 0                
            stats['source'][row['source']] += 1
            
            if row['internalStatus'] not in stats['statuses']:
                stats['statuses'][row['internalStatus']] = 0
            stats['statuses'][row['internalStatus']] += 1
            
            if row['category'] not in prices:
                prices[row['category']] = []
                
            if row['price']:
                prices[row['category']].append(int(row['price']))
            
            alivePeriods.append(int(row['updateDate']) - int(row['addDate']))
            timeSinceAppeared.append(timestamp - int(row['addDate']))
            timeSinceDisappeared.append(timestamp - int(row['updateDate']))

        stats['price_per_category:mean'] = {}
        stats['price_per_category:median'] = {}
        stats['price_per_category:std'] = {}
        stats['price_per_category:var'] = {}
        
        for categ in prices:
            stats['price_per_category:median'][categ] = numpy.median(prices[categ])
            stats['price_per_category:mean'][categ] = numpy.mean(prices[categ])
            stats['price_per_category:std'][categ] = numpy.std(prices[categ])
            stats['price_per_category:var'][categ] = numpy.var(prices[categ])
        
        if alivePeriods:
            stats['alivePeriod'] = numpy.mean(alivePeriods) / (60 * 60 * 24)
        
        if timeSinceAppeared:
            stats['timeSinceAppeared'] = numpy.mean(timeSinceAppeared) / (60 * 60 * 24)
            
        if timeSinceDisappeared:
            stats['timeSinceDisappeared'] = numpy.mean(timeSinceDisappeared) / (60 * 60 * 24)
        
        self.db.selectEnd(rows)
        return stats

    def doprint(self, stats):
        sys.stdout.write("\n\n Sources: ")
        s = ""
        for src in sorted(stats['source'].iterkeys()):
            sys.stdout.write("%s %s(%s)" % (s, src, locale.format("%.*f", (0, stats['source'][src]), True)))
            s = ","
            
        sys.stdout.write("\n\n Categories: ")
        for src in sorted(stats['categories'].iterkeys()):
            sys.stdout.write("\n\t%s: \t% 5s \tmedia % 7s EUR (% 7s EUR)" % (src,
                locale.format("%.*f", (0, stats['categories'][src]), True),
                locale.format("%.*f", (0, stats['price_per_category:mean'][src]), True),
                locale.format("%.*f", (0, stats['price_per_category:median'][src]), True)))
            
            
        sys.stdout.write("\n\n Statuses: ")
        prio = ("todo", "None")
        unprio = ("old", "deleted", "duplicate")
        
        st = { }
        for src in stats['statuses']:
            val = stats['statuses'][src]
            if  src == '':
                src = "None"
                
            if  src is None:
                src = "None"
                
            st[src] = val
        stats['statuses'] = st
        
        for src in prio:
            if src in stats['statuses']:
                sys.stdout.write("\n\t%- 9s: % 9s" % (src, locale.format("%.*f", (0, stats['statuses'][src]), True)))

        for src in stats['statuses']:
            if src not in prio and src not in unprio:
                sys.stdout.write("\n\t%- 9s: % 9s" % (src, locale.format("%.*f", (0, stats['statuses'][src]), True)))
        
        for src in unprio:
            if src in stats['statuses']:
                sys.stdout.write("\n\t%- 9s: % 9s" % (src, locale.format("%.*f", (0, stats['statuses'][src]), True)))
        
        sys.stdout.write("\n\n Times: %d days alive, appeared %d days ago, dissapeared %d days ago" % (stats['alivePeriod'], stats['timeSinceAppeared'], stats['timeSinceDisappeared']))
