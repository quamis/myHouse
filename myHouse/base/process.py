import logging
import md5
import time
import sys

class Processor(object):
    def __init__(self, source, maindb, db, cache, args):
        self.args = args
        self.source = source
        self.db = db
        self.maindb = maindb
        self.cache = cache

        #email, phones        
        self.maindb.tableCreate("data", { 
            "id":           "VARCHAR(64)",
            "category":     "VARCHAR(64)",
            "source":       "VARCHAR(16)",  # anunturi_ro
            "url":          "VARCHAR(256)",
            "price":        "INT",
            "description":  "TEXT",
            "addDate":      "INT",
            "updateDate":   "INT",
        }, ["id"])
        
        self.maindb.tableCreate("data_contacts", { 
            "idOffer":      "VARCHAR(64)",
            "key":          "VARCHAR(16)",  # email, telephone, address
            "value":        "VARCHAR(256)",
        }, [], ["id"])
        
        self.maindb.tableCreate("data_extracted", { 
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

    def debug_print(self, result, extra=None):
        # 0 = none, 1: only importans, 2: dots, 3: debug
        if(self.args.verbosity>=1):
            self.debug_print_1(result, extra)
        elif(self.args.verbosity>=0):
            self.debug_print_0(result, extra)
            
    
    def debug_print_1(self, result, extra=None):
        if(result=="loop-step"):
            pass
        
        if(result=="loop-new"):
            sys.stdout.write("\n    % 9dEUR %s" % (extra['price'], extra['url']))
            
        if(result=="loop-old"):
            sys.stdout.write('.')
            
        sys.stdout.flush()
    
    def debug_print_0(self, result, extra=None):
        pass

    def run(self):
        rows = self.selectStart();
        timestamp = time.time()
        
        index=0
        for row in rows:
            self.debug_print("loop-step", { "index": index })
            index+=1
            newRow = self._processRow(row)
            
            if(not self.maindb.itemExists("data", newRow['id'])):
                self.debug_print("loop-new", newRow)
                
                if 'contacts' in newRow:
                    for c in newRow['contacts']:
                        self.maindb.itemInsert("data_contacts", { "idOffer":newRow['id'], "key": c['key'], "value": c['value'] })
                        
                if 'extracted' in newRow:
                    for k,v in newRow['extracted'].items():
                        self.maindb.itemInsert("data_extracted", { "idOffer":newRow['id'], "key": k, "value": v })
                        
                self.maindb.itemInsert("data", {
                      "source":     self.source, 
                      "id":         newRow['id'],
                      "category":   newRow['category'], 
                      "url":        newRow['url'], 
                      "price":      newRow['price'],
                      "description":newRow['description'],
                      "addDate":    timestamp,
                      "updateDate": timestamp,
                      })
            else:
                self.debug_print("loop-old", newRow)
            
        self.selectEnd(rows)
        self.maindb.close()
