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
        self.tables_cache = []
        self.tables_data = []
        
    def cleanCache(self):
        maxUpdatedTime = time.mktime((date.today()-timedelta(days=2)).timetuple())

        for table in self.tables_cache:
            count1 = self.cache.db.selectAll("SELECT COUNT(*) FROM `%s`" % (table))[0][0]
            self.cache.db.execute("DELETE FROM `%s` WHERE `addDate`<%d OR `addDate` IS NULL" % (table, maxUpdatedTime))
            
            self.cache.db.execute("DELETE FROM `%s` WHERE ( `id` NOT LIKE 'page-%%' AND `id` NOT LIKE '%s__http://%%' )" % (table, time.strftime("%Y%m%d")))
            
            count2 = self.cache.db.selectAll("SELECT COUNT(*) FROM `%s`" % (table))[0][0]
            
            print "%s: %s -> %s" % (table, count1, count2)
        
        if self.args.vacuum:
            self.cache.db.execute("VACUUM")
            
    def cleanDataTable(self):
        maxUpdatedTime = time.mktime((date.today()-timedelta(days=2)).timetuple())

        for table in self.tables_data:
            count1 = self.db.selectAll("SELECT COUNT(*) FROM `%s`" % (table))[0][0]
            self.db.execute("DELETE FROM `%s` WHERE `updateDate`<%d OR `updateDate` IS NULL" % (table, maxUpdatedTime))
            
            count2 = self.db.selectAll("SELECT COUNT(*) FROM `%s`" % (table))[0][0]
            
            print "%s: %s -> %s" % (table, count1, count2)
        
        if self.args.vacuum:
            self.db.execute("VACUUM")
            
    def run(self):
        self.cleanCache()
        self.cleanDataTable()
        
        self.cache.db.close()
        self.db.close()
        pass