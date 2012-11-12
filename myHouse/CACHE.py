import pickle
from DB import DB

class CACHE:
    def __init__(self, tablePrefix):
        self.tablePrefix = tablePrefix
        self.db = DB("cache.sqlite")
        self.db.createCache("cache_"+self.tablePrefix)
    
    def get(self, id):
        row = self.db.selectCache("cache_"+self.tablePrefix, id)
        if(row):
            return pickle.loads(row[0])
        return None
        
    def set(self, id, data):
        if(self.get(id)):
            self.db.update("cache_"+self.tablePrefix, { "id":id, "data":pickle.dumps(data) })
        else:
            self.db.insert("cache_"+self.tablePrefix, { "id":id, "data":pickle.dumps(data) })
    
    def delete(self, id):
        return self.db.delete("cache_"+self.tablePrefix, id)    

        