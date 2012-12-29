import time
import sys
from datetime import date, timedelta
import difflib


class Cleanup(object):
    def __init__(self, source, db, cache, args):
        self.args = args
        self.source = source
        self.db = db
        self.cache = cache
        self.tables = []
        
    def cleanCache(self):
        dt = date.today()-timedelta(days=3)
        maxUpdatedTime = time.mktime(dt.timetuple())

        for table in self.tables:
            count1 = self.cache.db.selectAll("SELECT COUNT(*) FROM `%s`" % (table))[0][0]
            self.cache.db.execute("DELETE FROM `%s` WHERE `addDate`<%d OR `addDate` IS NULL" % (table, maxUpdatedTime))
            count2 = self.cache.db.selectAll("SELECT COUNT(*) FROM `%s`" % (table))[0][0]
            
            print "%s: %s -> %s" % (table, count1, count2)
            
        #self.cache.db.execute("VACUUM")

    def run(self):
        self.cleanCache()
        pass