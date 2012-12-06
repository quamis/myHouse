# -*- coding: utf-8 -*-
import sqlite3
import random

class DB:
    def __init__(self, file):
        self.file = file
        self.connection = None
        self.cursor = None
        self.open()
        
    def open(self):
        self.connection = sqlite3.connect(self.file)
    
    def tableCreate(self, table, definition, uniqueindexes=[], indexes=[]):
        c = self.connection.cursor()
        sql = "CREATE TABLE IF NOT EXISTS " + table + " ("
        s=""
        for k, v in definition.items():
            sql+="%s %s %s" % (s, k, v)
            s=","
        sql+=")"
        c.execute(sql)
        
        for v in uniqueindexes:
            sql = 'CREATE UNIQUE INDEX IF NOT EXISTS "'+v+'" on ' + table + ' ('+v+' ASC)'
            c.execute(sql)
            
        for v in indexes:
            sql = 'CREATE INDEX IF NOT EXISTS "'+v+'" on ' + table + ' ('+v+' ASC)'
            c.execute(sql)
        
        self.connection.commit()
        c.close()
        
        # reopen connection, seems like there are some bugs and we cannot see the tables on the same connection
        self.connection.close()
        self.open()
        self.cursor = None
        
        
    def _getCursor(self):
        if self.cursor:
            return self.cursor
        
        self.cursor = self.connection.cursor()
        return self.cursor
    
    def close(self):
        self.connection.commit()
        if self.cursor:
            self.cursor.close()
        self.connection.commit()
        self.cursor = None
        
    def flushRandom(self, chance, doClose=True):
        if random.random()<chance:
            self.connection.commit()
            if self.cursor and doClose:
                self.cursor.close()
            self.connection.commit()
            self.cursor = None
            
    def itemDelete(self, table, id):
        c = self._getCursor()
        c.execute('DELETE FROM ' + table + ' WHERE id="'+id+'"')
        
    def itemExists(self, table, id):
        c = self._getCursor()
        c.execute('SELECT id FROM ' + table + ' WHERE id="'+id+'"')
        ret = c.fetchone()
        return bool(ret)

    def itemReadField(self, table, id, field):
        c = self._getCursor()
        c.execute('SELECT `%s` FROM `%s` WHERE id="%s"' % (field, table, id))
        ret = c.fetchone()
        return ret
        
    def itemUpdate(self, table, data):
        c = self._getCursor()
        sql = 'UPDATE ' + table + ' SET '
        
        s = ""
        for k, v in data.items():
            sql+= s+k+"=?"
            s = ","
        sql+=" WHERE id='" + data['id'] + "'"
        
        dataList = [];
        for k, v in data.items():
            dataList.append(v)
        
        c.execute(sql, (dataList))
        
        
    def itemInsert(self, table, data):
        c = self._getCursor()
        sql = 'INSERT INTO ' + table + ' ('
        
        s = ""
        for k, v in data.items():
            sql+= s+k
            s = ","
        sql+= ') VALUES ('
        
        s = ""
        for k, v in data.items():
            sql+= s+'?'
            s = ","
        sql+= ')'
        
        dataList = [];
        for k, v in data.items():
            dataList.append(v)
        
        c.execute(sql, (dataList))
		
    def execute(self, sql):
        c = self._getCursor()
        return c.execute(sql)
    
    def selectAll(self, sql):
        c = self._getCursor()
        c.execute(sql)
        ret = c.fetchall()
        return ret
    
    def selectStart(self, sql):
        c = self._getCursor()
        c.execute(sql)
        return c
    
    def selectEnd(self, c):
        pass
        
    

