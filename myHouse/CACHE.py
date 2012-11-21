# -*- coding: utf-8 -*-
import pickle
from DB import DB

class CACHE:
    def __init__(self, tablePrefix):
        self.tablePrefix = tablePrefix
        self.db = DB("cache.sqlite")
        self.db.tableCreate(self.tablePrefix, { 
            "id":             "VARCHAR(128)",
            "data":           "BLOB",
            "addDate":        "INT",
        }, ["id"])
        
    def get(self, id):
        row = self.db.itemReadField(self.tablePrefix, id, "data")
        if(row):
            return pickle.loads(row[0])
        return None
        
    def set(self, id, data):
        if(self.db.itemExists(self.tablePrefix, id)):
            self.db.itemUpdate(self.tablePrefix, { "id":id, "data":buffer(pickle.dumps(data, pickle.HIGHEST_PROTOCOL)) })
        else:
            self.db.itemInsert(self.tablePrefix, { "id":id, "data":buffer(pickle.dumps(data, pickle.HIGHEST_PROTOCOL)) })
            
        self.db.flushRandom(0.001)
    
    def close(self):
        self.db.close()
        