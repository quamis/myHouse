import time
import sys
from datetime import date, timedelta
import difflib
import random


class Cleanup(object):
    def __init__(self, source, db, cache, args):
        self.args = args
        self.source = source
        self.db = db
        self.cache = cache
        self.tables = []
        
    def cleanCache(self):
        maxUpdatedTime = time.mktime((date.today()-timedelta(days=2)).timetuple())

        for table in self.tables:
            count1 = self.cache.db.selectAll("SELECT COUNT(*) FROM `%s`" % (table))[0][0]
            self.cache.db.execute("DELETE FROM `%s` WHERE `addDate`<%d OR `addDate` IS NULL" % (table, maxUpdatedTime))
            
            self.cache.db.execute("DELETE FROM `%s` WHERE ( `id` NOT LIKE 'page-%%' AND `id` NOT LIKE '%s%%-%%' )" % (table, time.strftime("%Y%m%d")))
            
            count2 = self.cache.db.selectAll("SELECT COUNT(*) FROM `%s`" % (table))[0][0]
            
            print "%s: %s -> %s" % (table, count1, count2)
        
        self.vacuum()
            
    def vacuum(self):
        if random.random()<0.20:
            self.cache.db.execute("VACUUM")

    def run(self):
        self.cleanCache()
        
        self.cache.db.close()
        pass