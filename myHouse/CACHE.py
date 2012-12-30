# -*- coding: utf-8 -*-
import pickle
from DB import DB
import zlib
import time

class CACHE:
    def __init__(self, tablePrefix):
        self.tablePrefix = tablePrefix
        self.db = DB("../db/cache-"+self.tablePrefix+".sqlite")
        self.db.tableCreate(self.tablePrefix, { 
            "id":             "VARCHAR(256)",
            "data":           "BLOB",
            "addDate":        "INT",
        }, ["id"])
        
    def get(self, id):
        row = self.db.itemReadField(self.tablePrefix, id, "data")
        if(row):
            return pickle.loads(zlib.decompress(row[0]))
        return None
        
    def set(self, id, data):
        if(self.db.itemExists(self.tablePrefix, id)):
            self.db.itemUpdate(self.tablePrefix, { "id":id, "addDate":time.time(), "data":buffer(zlib.compress(pickle.dumps(data, pickle.HIGHEST_PROTOCOL))) })
        else:
            self.db.itemInsert(self.tablePrefix, { "id":id, "addDate":time.time(), "data":buffer(zlib.compress(pickle.dumps(data, pickle.HIGHEST_PROTOCOL))) })
            
        self.db.flushRandom(0.01)
    
    def close(self):
        self.db.close()
    
    def flushRandom(self, chance=0.01):    
        self.db.flushRandom(chance)