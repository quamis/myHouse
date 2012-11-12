import sqlite3

class DB:
    def __init__(self, file):
        self.file = file
        self.connection = None
        self.open()
        
    def open(self):
        self.connection = sqlite3.connect(self.file)
        
    def create(self, table, definition, indexes):
        c = self.connection.cursor()
        sql = "CREATE TABLE IF NOT EXISTS " + table + " ("
        s=""
        for k, v in definition.items():
            sql+="%s %s %s" % (s, k, v)
            s=","
        sql+=")"
        c.execute(sql)
        
        for v in indexes:
            sql = 'CREATE UNIQUE INDEX IF NOT EXISTS "'+v+'" on ' + table + ' ('+v+' ASC)'
            c.execute(sql)
        
        self.connection.commit()
        c.close()
        self.connection.close()
        self.open()
        
    def createCache(self, section):
        c = self.connection.cursor()
        sql = 'CREATE TABLE IF NOT EXISTS ' + section + ' (\
            id VARCHAR(64), \
            data BLOB, \
            addDate VARCHAR(20) \
        )'
        c.execute(sql)
        sql = 'CREATE UNIQUE INDEX IF NOT EXISTS "id" on ' + section + ' (id ASC)'
        c.execute(sql)
        self.connection.commit()
        c.close()
        self.connection.close()
        self.open()
    
    
    def update(self, table, data):
        c = self.connection.cursor()
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
        self.connection.commit()
        c.close()
        
    def insert(self, table, data):
        c = self.connection.cursor()
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
        self.connection.commit()
        c.close()
    
    def select(self, table, id):
        c = self.connection.cursor()
        c.execute('SELECT * FROM ' + table + ' WHERE id="'+id+'"')
        ret = c.fetchone()
        self.connection.commit()
        c.close()
        return ret

    def delete(self, table, id):
        c = self.connection.cursor()
        c.execute('DELETE FROM ' + table + ' WHERE id="'+id+'"')
        ret = c.fetchone()
        self.connection.commit()
        c.close()
        return ret


    def selectCache(self, table, id):
        c = self.connection.cursor()
        c.execute('SELECT data FROM ' + table + ' WHERE id="'+id+'"')
        ret = c.fetchone()
        self.connection.commit()
        c.close()
        return ret

    def recordExists(self, table, id):
        c = self.connection.cursor()
        c.execute('SELECT id FROM ' + table + ' WHERE id="'+id+'"')
        ret = c.fetchone()
        self.connection.commit()
        c.close()
        return bool(ret)
