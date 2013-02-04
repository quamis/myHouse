# -*- coding: utf-8 -*-

import time, sys
import sources.base.Processor.Helper as Helper
import sources.base.Processor.CurrencyConverter as Currency

class Processor(object):
    def __init__(self, source, maindb, db, cache, args):
        self.args = args
        self.source = source
        self.db = db
        self.maindb = maindb
        self.cache = cache
        
        
        self.processor_helper = Helper.Helper()
        
        self.currencyConverter = Currency.CurrencyConverter()

        #email, phones        
        self.maindb.tableCreate("data", { 
            "id":           "VARCHAR(64)",
			"internalStatus":"VARCHAR(128)",
            
            "userStatus":       "VARCHAR(128)",
            "suggestedStatus":   "VARCHAR(128)",
            
            "category":     "VARCHAR(64)",
            "source":       "VARCHAR(16)",  # anunturi_ro
            "url":          "VARCHAR(256)",
            "description":  "TEXT",
            "price":        "INT",

            "location":     "VARCHAR(256)",
            "rooms":        "INT",
            "year_built":   "INT",
            "surface_total":"FLOAT",
            "surface_built":"FLOAT",
            "price_per_mp_total":"FLOAT",
            "price_per_mp_built":"FLOAT",
            
            "floor":        "INT",
            "floor_max":    "INT",
            "apartmentType":"VARCHAR(64)",
            
            "addDate":      "INT",
            "updateDate":   "INT",
        }, ["id"], ["internalStatus", "category", "source", "price", "addDate", "updateDate"])
        
        self.maindb.tableCreate("data_contacts", { 
            "idOffer":      "VARCHAR(64)",
            "key":          "VARCHAR(16)",  # email, telephone, address
            "value":        "VARCHAR(256)",
        }, [], ["id", "key"])
        
        self.maindb.tableCreate("data_extracted", { 
            "idOffer":      "VARCHAR(64)",
            "key":          "VARCHAR(16)",
            "value":        "VARCHAR(256)",
        }, [], ["id", "key"])
        

    def selectStart(self):
        pass
    
    def selectEnd(self):
        pass
    
    def _processRow(self, row):
        pass

    def extractData_base(self, newRow):
        if newRow['price'] and "surface_built" in newRow and newRow["surface_built"]:
            newRow['price_per_mp_built'] = round(float(newRow['price'])/float(newRow['surface_built']), 0)
            
        if newRow['price'] and "surface_total" in newRow and newRow["surface_total"]:
            newRow['price_per_mp_total'] = round(float(newRow['price'])/float(newRow['surface_total']), 0)
            
        return newRow


    def debug_print(self, result, extra=None):
        # 0 = none, 1: only importans, 2: dots, 3: debug
        if(self.args.verbosity>=1):
            self.debug_print_1(result, extra)
        elif(self.args.verbosity>=0):
            self.debug_print_0(result, extra)
            
    
    def debug_print_1(self, result, extra=None):
        if(result=="loop-error"):
            sys.stdout.write("\n # %s -> %s" % ("error on", extra['url']))
            
        if(result=="loop-step"):
            pass
        
        if(result=="loop-new"):
            sys.stdout.write("\n    % 9sEUR %s" % (int(extra['price']) if extra['price'] else "-", extra['url']))
            
        if(result=="loop-old"):
            #sys.stdout.write('.')
            pass
        
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
            #try:
            newRow = self._processRow(row)
            #except Exception as e:
            #    print "ex: %s" % (e)
                
            if newRow is None:
                continue
            
            if "extracted" not in newRow:
                newRow['extracted'] = {}
                                    
            newRow = self.processor_helper.convert_location(newRow)
            
            if(self.maindb.itemExists("data", newRow['id'])):
                if self.args.forceUpdate:
                    try:
                        self.maindb.execute("DELETE FROM `data_contacts` WHERE `idOffer`='%s'" %(newRow['id']))
                        self.maindb.execute("DELETE FROM `data_extracted` WHERE `idOffer`='%s'" %(newRow['id']))
                        
                        if 'contacts' in newRow:
                            for c in newRow['contacts']:
                                self.maindb.itemInsert("data_contacts", { "idOffer":newRow['id'], "key": c['key'], "value": c['value'] })
                                
                        if 'extracted' in newRow:
                            for k,v in newRow['extracted'].items():
                                self.maindb.itemInsert("data_extracted", { "idOffer":newRow['id'], "key": k, "value": v })
                                
                        self.maindb.itemUpdate("data", {
                              "source":             self.source, 
                              "id":                 newRow['id'],
                              "category":           newRow['category'], 
                              "url":                newRow['url'], 
                              "price":              newRow['price'],
                              "description":        newRow['description'],
                              
                              "location":           newRow['location'] if 'location' in newRow else None,
                              "rooms":              newRow['rooms'] if 'rooms' in newRow else None,
                              "year_built":         newRow['year_built'] if 'year_built' in newRow else None,
                              "surface_total":      newRow['surface_total'] if 'surface_total' in newRow else None,
                              "surface_built":      newRow['surface_built'] if 'surface_built' in newRow else None,
                              "price_per_mp_total": newRow['price_per_mp_total'] if 'price_per_mp_total' in newRow else None,
                              "price_per_mp_built": newRow['price_per_mp_built'] if 'price_per_mp_built' in newRow else None,
                              
                              "updateDate":         timestamp,
                          })
                    except Exception as e:
                        print "Exception(%s): %s" % (e.errno, e.strerror)
                else:
                    self.maindb.itemUpdate("data", { "id": newRow['id'], "updateDate": timestamp, })
                    
                self.debug_print("loop-old", newRow)
            else:
                try:
                    self.debug_print("loop-new", newRow)
                    
                    if 'contacts' in newRow:
                        for c in newRow['contacts']:
                            self.maindb.itemInsert("data_contacts", { "idOffer":newRow['id'], "key": c['key'], "value": c['value'] })
                            
                    if 'extracted' in newRow:
                        for k,v in newRow['extracted'].items():
                            self.maindb.itemInsert("data_extracted", { "idOffer":newRow['id'], "key": k, "value": v })
                            
                    self.maindb.itemInsert("data", {
                              "internalStatus":     "",
                              "userStatus":         "",
                              "suggestedStatus":    "",
                              "source":             self.source, 
                              "id":                 newRow['id'],
                              "category":           newRow['category'], 
                              "url":                newRow['url'], 
                              "price":              newRow['price'],
                              "description":        newRow['description'],
                              
                              "location":           newRow['location'] if 'location' in newRow else None,
                              "rooms":              newRow['rooms'] if 'rooms' in newRow else None,
                              "year_built":         newRow['year_built'] if 'year_built' in newRow else None,
                              "surface_total":      newRow['surface_total'] if 'surface_total' in newRow else None,
                              "surface_built":      newRow['surface_built'] if 'surface_built' in newRow else None,
                              "price_per_mp_total": newRow['price_per_mp_total'] if 'price_per_mp_total' in newRow else None,
                              "price_per_mp_built": newRow['price_per_mp_built'] if 'price_per_mp_built' in newRow else None,
                              
                              "updateDate":         timestamp,
                              "addDate":            timestamp,
                      })
                    self.db.flushRandom(0.025, False)
                except Exception as e:
                    print "Exception(%s): %s" % (e.errno, e.strerror)
                
        self.selectEnd(rows)
        self.maindb.close()

