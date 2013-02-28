#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, time, codecs
import datetime

from DB import DB
import logging
import locale
import argparse
import numpy 

class Stats:
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
        if self.args.category:
            sql += "/*category*/ AND( 0 "
            for k in self.args.category:
                sql += " OR `category`='%s'" % (k)
            sql += ")"
            
        if self.args.source:
            sql += "/*source*/ AND( 0 "
            for k in self.args.source:
                sql += " OR `source`='%s'" % (k)
            sql += ")"
            
        if self.args.status:
            sql += "/*userStatus*/ AND (`userStatus`='%s')" % (self.args.status)
            
        if(self.args.ageu):
            dt = datetime.date.today()-datetime.timedelta(days=self.args.ageu)
            sql+=" AND `updateDate`>%d" % (time.mktime(dt.timetuple()))
        if(self.args.agea):
            dt = datetime.date.today()-datetime.timedelta(days=self.args.agea)
            sql+=" AND `addDate`>%d" % (time.mktime(dt.timetuple()))
        
        if(self.args.dtadd_min):
            dt = datetime.date.today()-datetime.timedelta(days=self.args.dtadd_min)
            sql+=" AND `addDate`>%d" % (time.mktime(dt.timetuple()))
        if(self.args.dtadd_max):
            dt = datetime.date.today()-datetime.timedelta(days=self.args.dtadd_max)
            sql+=" AND `addDate`<%d" % (time.mktime(dt.timetuple()))
        
        if(self.args.dtupd_min):
            dt = datetime.date.today()-datetime.timedelta(days=self.args.dtupd_min)
            sql+=" AND `updateDate`>%d" % (time.mktime(dt.timetuple()))
        if(self.args.dtupd_max):
            dt = datetime.date.today()-datetime.timedelta(days=self.args.dtupd_max)
            sql+=" AND `updateDate`<%d" % (time.mktime(dt.timetuple()))
         
        sql += " ORDER BY `price` ASC, `location` ASC"
        return sql
    
    def roundInInterval(self, value, interval):
        for v in interval:
            if value < v[0]:
                value = int(round(value / v[1]) * v[1])
                return value
                
        return None
    
    def _incDict(self, dict, key):
        if key not in dict:
            dict[key] = 0
        dict[key] += 1
        return dict
    
    def extractGeneralData(self):
        timestamp = time.time()
        
        stats = {}
        stats['source'] = {}
        stats['categories'] = {}
        stats['statuses'] = {}
        
        prices = {}
        alivePeriods = []
        timeSinceAppeared = []
        timeSinceDisappeared = []
        
        rows = self.db.selectAll(self.getSQL())
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
        
    def printGeneralData(self, stats):
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

    def extractDateData(self):
        stats = {}
        stats['addDate'] = {}
        stats['updateDate'] = {}
        
        if self.args.byAddDate == "week":
            stats['addDate:week'] = {}
            stats['updateDate:week'] = {}
            
        if self.args.byAddDate == "month":
            stats['addDate:month'] = {}
            stats['updateDate:month'] = {}
        
        rows = self.db.selectAll(self.getSQL())
        for row in rows:
            row = self.getItem(row[0], ('data'))
            addDate = datetime.datetime.fromtimestamp(row['addDate']).strftime('%Y-%m-%d')
            updateDate = datetime.datetime.fromtimestamp(row['updateDate']).strftime('%Y-%m-%d')
            
            stats['addDate'] = self._incDict(stats['addDate'], addDate)
            stats['updateDate'] = self._incDict(stats['updateDate'], updateDate)
            
            if self.args.byAddDate == "week":
                addDate = datetime.datetime.fromtimestamp(row['addDate']).strftime('%Y-%U')
                updateDate = datetime.datetime.fromtimestamp(row['updateDate']).strftime('%Y-%U')
                
                stats['addDate:week'] = self._incDict(stats['addDate:week'], addDate)
                stats['updateDate:week'] = self._incDict(stats['updateDate:week'], updateDate)
                
            if self.args.byAddDate == "month":
                addDate = datetime.datetime.fromtimestamp(row['addDate']).strftime('%Y-%m')
                updateDate = datetime.datetime.fromtimestamp(row['updateDate']).strftime('%Y-%m')
                
                stats['addDate:month'] = self._incDict(stats['addDate:month'], addDate)
                stats['updateDate:month'] = self._incDict(stats['updateDate:month'], updateDate)
            
        return stats
        
    def printDateData(self, stats):
        if self.args.byAddDate == "day":
            allKeys = list(set(stats['addDate'].keys() + stats['updateDate'].keys()))
            fmt = "%-12s: % 9s % 9s"
            print (fmt + " offers") % ("date", "added", "updated")
                        
            for key in sorted(allKeys):
                print fmt % (key,
                    locale.format("%.*f", (0, stats['addDate'][key]), True)     if key in stats['addDate']         else 0,
                    locale.format("%.*f", (0, stats['updateDate'][key]), True)     if key in stats['updateDate']     else 0,)
                
        elif self.args.byAddDate == "week":
            allKeys = list(set(stats['addDate:week'].keys() + stats['updateDate:week'].keys()))
            fmt = "%-12s: % 9s % 9s"
            print (fmt + " offers") % ("date", "added", "updated")
                        
            for key in sorted(allKeys):
                print fmt % (key,
                    locale.format("%.*f", (0, stats['addDate:week'][key]), True)         if key in stats['addDate:week']     else 0,
                    locale.format("%.*f", (0, stats['updateDate:week'][key]), True)     if key in stats['updateDate:week']     else 0,)
                
        elif self.args.byAddDate == "month":
            allKeys = list(set(stats['addDate:month'].keys() + stats['updateDate:month'].keys()))
            fmt = "%-12s: % 9s % 9s"
            print (fmt + " offers") % ("date", "added", "updated")
                        
            for key in sorted(allKeys):
                print fmt % (key,
                    locale.format("%.*f", (0, stats['addDate:month'][key]), True)         if key in stats['addDate:month']     else 0,
                    locale.format("%.*f", (0, stats['updateDate:month'][key]), True)     if key in stats['updateDate:month'] else 0,)
        
        
    
    def extractBuildDateData(self):
        stats = {}
        stats[None] = 0
        
        rows = self.db.selectAll(self.getSQL())
        for row in rows:
            row = self.getItem(row[0], ('data'))
            
            if row['year_built']:
                yr = row['year_built']
                if self.args.byBuildDate == "simple":
                    yr = "+++"
                    
                if yr not in stats:
                    stats[yr] = 0
                stats[yr] += 1
            else:
                stats[None] += 1
            
        return stats
        
    def printBuildDateData(self, stats):
        fmt = "%04s: % 3s"
        print (fmt + " in year") % ("year", "offers")
                    
        for key in sorted(stats.keys()):
            print fmt % ("None" if key is None else key,
                locale.format("%.*f", (0, stats[key]), True))
        
        
    def extractLocationData(self):
        stats = {}
        stats[None] = 0
        
        rows = self.db.selectAll(self.getSQL())
        for row in rows:
            row = self.getItem(row[0], ('data'))
            
            if row['location']:
                loc = row['location']
                if self.args.byLocation == "simple":
                    loc = "+++"
                    
                if loc not in stats:
                    stats[loc] = 0
                stats[loc] += 1
            else:
                stats[None] += 1

        return stats
        
    def printLocationData(self, stats):
        fmt = "%-40s: % 3s"
        print (fmt + " in this location") % ("location", "offers")
                    
        for key in sorted(stats.keys()):
            print fmt % ("None" if key is None else key,
                locale.format("%.*f", (0, stats[key]), True))
            
            
    def extractSurfaceData(self):
        stats = {}
        stats[None] = 0
        
        rows = self.db.selectAll(self.getSQL())
        for row in rows:
            row = self.getItem(row[0], ('data'))
            
            surf = None
            if args.bySurface == "total":
                if row['surface_total']:
                    surf = row['surface_total']
                    
            if args.bySurface == "built":
                if row['surface_built']:
                    surf = row['surface_built']
            
            # round the surface to 10mp increments
            if surf:
                if "apt-2-cam" in args.category:
                    surf = self.roundInInterval(float(surf), ((20, 5), (150, 10), (500, 50)))
                elif "apt-3-cam" in args.category or "apt-4-cam" in args.category:
                    surf = self.roundInInterval(float(surf), ((20, 5), (250, 10), (500, 50)))
                else:
                    surf = self.roundInInterval(float(surf), ((30, 10), (750, 50), (2500, 100), (10000, 500), (100000, 10000), (10000000, 100000)))
                    
            
            if surf not in stats:
                stats[surf] = 0
            stats[surf] += 1

        return stats
        
    def printSurfaceData(self, stats):
        fmt = "%-40s: % 8s"
        print (fmt) % ("surface(mp)", "offers")
        
        def sort_fcn(x):
            if x:
                return float(x)
            
            return x
        
        for key in sorted(stats.keys(), key=sort_fcn):
            print fmt % ("None" if key is None else key,
                locale.format("%.*f", (0, stats[key]), True))
        
            
parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-source', dest='source', action='append', type=str, default=None, help='TODO')
parser.add_argument('-category', dest='category', action='append', type=str, default=None, help='TODO')
parser.add_argument('-status', dest='status', action='store', type=str, default=None, help='TODO')
parser.add_argument('-ageu', dest='ageu', action='store', type=float, default=None, help='max age in days')
parser.add_argument('-agea', dest='agea', action='store', type=float, default=None, help='max age when added in days')
parser.add_argument('-dtadd_min', dest='dtadd_min', action='store', type=float, default=None, help='TODO')
parser.add_argument('-dtadd_max', dest='dtadd_max', action='store', type=float, default=None, help='TODO')
parser.add_argument('-dtupd_min', dest='dtupd_min', action='store', type=float, default=None, help='TODO')
parser.add_argument('-dtupd_max', dest='dtupd_max', action='store', type=float, default=None, help='TODO')



parser.add_argument('-byAddDate', dest='byAddDate', action='store', type=str, default=None, help='TODO')
parser.add_argument('-byBuildDate', dest='byBuildDate', action='store', type=str, default=None, help='TODO')
parser.add_argument('-byLocation', dest='byLocation', action='store', type=str, default=None, help='TODO')
parser.add_argument('-bySurface', dest='bySurface', action='store', type=str, default=None, help='TODO')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

db = DB("../db/main.sqlite")
stats = Stats(db, args)

if args.byAddDate:
    stats.printDateData(stats.extractDateData())
elif args.byBuildDate:
    stats.printBuildDateData(stats.extractBuildDateData())
elif args.byLocation:
    stats.printLocationData(stats.extractLocationData())
elif args.bySurface:
    stats.printSurfaceData(stats.extractSurfaceData())
else:
    stats.printGeneralData(stats.extractGeneralData())
    
sys.stdout.write("\n")
raise SystemExit
