import logging
import md5
import time

class Processor(object):
    def __init__(self, source, maindb, db, cache):
        self.source = source
        self.db = db
        self.maindb = maindb
        self.cache = cache

        #email, phones        
        self.maindb.create("data", { 
            "id":           "VARCHAR(64)",
            "category":     "VARCHAR(64)",
            "source":       "VARCHAR(16)",  # anunturi_ro
            "url":          "VARCHAR(256)",
            "price":        "INT",
            "description":  "TEXT",
            "addDate":      "INT",
            "updateDate":   "INT",
        }, ["id"])
        
        self.maindb.create("data_contacts", { 
            "idOffer":      "VARCHAR(64)",
            "key":          "VARCHAR(16)",  # email, telephone, address
            "value":        "VARCHAR(256)",
        }, [], ["id"])
        
        self.maindb.create("data_extracted", { 
            "idOffer":      "VARCHAR(64)",
            "key":          "VARCHAR(16)",
            "value":        "VARCHAR(256)",
        }, [], ["id"])

    def selectStart(self):
        pass
    
    def selectEnd(self):
        pass
    
    def _processRow(self, row):
        pass

    def run(self):
        rows = self.selectStart();
        timestamp = time.time()
        
        for row in rows:
            newRow = self._processRow(row)
            
            if(not self.maindb.recordExists("data", newRow['id'])):
                if 'contacts' in newRow:
                    for c in newRow['contacts']:
                        self.maindb.insert("data_contacts", { "idOffer":newRow['id'], "key": c['key'], "value": c['value'] })
                        
                if 'extracted' in newRow:
                    for c in newRow['extracted']:
                        self.maindb.insert("data_extracted", { "idOffer":newRow['id'], "key": c['key'], "value": c['value'] })
                        
                self.maindb.insert("data", {
                      "source":     self.source, 
                      "id":         newRow['id'],
                      "category":   newRow['category'], 
                      "url":        newRow['url'], 
                      "price":      newRow['price'],
                      "description":newRow['description'],
                      "addDate":    timestamp,
                      "updateDate": timestamp,
                      })
            
        self.selectEnd(rows);
