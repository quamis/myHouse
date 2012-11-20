import base.process

import re
import logging

class doProcess(base.process.Processor ):
    def __init__(self, source, maindb, db, cache, args):
        super(doProcess, self).__init__(source, maindb, db, cache, args)
    
    def selectStart(self):
        #                                 0              1       2         3      4          5         6                7                8            9
        c = self.db.selectStart("SELECT `category`, `location`, `rooms`, `url`, `details`, `price`, `surface_total`, `surface_built`, `year_built`, `id` FROM `imobiliare_ro_data` WHERE 1 ORDER BY `category` ASC, `description` ASC")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
    def myTrim(self, regex, text):
        tx = ""
        while tx!=text:
            tx = text
            text = re.sub(regex, "", tx)
        return text
    
    def _extractData_houses(self, newRow, row):
        extr = {}
        extr['location'] = row[1]
        extr['rooms'] = row[2]
        extr['surface_built'] = row[7]
        extr['surface_total'] = row[6]

        if "surface_built" in extr:
            print newRow['price']
            print extr['surface_built']
            extr['price_per_mp_built'] = round(float(newRow['price'])/float(extr['surface_built']), 0)
            
        return extr
        
    def _processRow(self, row):
        newRow = {}
        newRow['category'] = row[0]
        newRow['description'] = re.sub("[\s]+", " ", row[4])
        newRow['url'] =     row[3]
        newRow['price'] =   row[5]
        newRow['id'] =      row[9]
        
        """
        contact = []
        for c in row[1].split("/"): 
            c = re.sub("[\.\s\-]", "", c)
            contact.append({ "key":"phone", "value":c })
        newRow['contacts'] = contact
        """
        
        
        # extract data
        if newRow['category']=="case-vile":
            newRow['extracted'] = self._extractData_houses(newRow, row)
        
                
            #raise SystemExit  
        
        #raise SystemExit
        
        
        #print newRow
        return newRow
    