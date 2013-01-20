import base.process
import re

class doProcess(base.process.Processor ):
    def __init__(self, source, maindb, db, cache, args):
        super(doProcess, self).__init__(source, maindb, db, cache, args)
    
    def selectStart(self):
        c = self.db.selectStart("SELECT `category`, `contact`, `description`, `url`, `price`, `id`  FROM `anuntul_ro_data` WHERE 1 ORDER BY `category` ASC, `description` ASC")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
    def _extractData_houses(self, newRow):
        extr = {}
        #desc = re.sub("\xa0|\d20ac", "", newRow['description'])
        desc = newRow['description']
        
        #print ""
        #print desc
        extr = self.processor_helper.extract_location(extr, desc)
        extr = self.processor_helper.convert_location(extr, desc)
        
        extr = self.processor_helper.extract_rooms(extr, desc)
        
        extr = self.processor_helper.extract_year(extr, desc)
        
        extr = self.processor_helper.extract_surface(extr, desc, "case-vile")
        
        if newRow['price'] and "surface_built" in extr and float(extr['surface_built'])>1:
            extr['price_per_mp_built'] = round(float(newRow['price'])/float(extr['surface_built']), 0)

        return extr
    
    def _extractData_apt(self, newRow):
        extr = {}
        desc = newRow['description']
        
        #print ""
        #print desc
        extr = self.processor_helper.extract_location(extr, desc)
        extr = self.processor_helper.convert_location(extr, desc)
        
        extr = self.processor_helper.extract_rooms(extr, desc)
        
        extr = self.processor_helper.extract_year(extr, desc)
            
        extr = self.processor_helper.extract_surface(extr, desc, "apt")

        if "surface_built" in extr and float(extr['surface_built'])>0:
            extr['price_per_mp_built'] = round(float(newRow['price'])/float(extr['surface_built']), 0)
            
        return extr
        
    def _processRow(self, row):
        newRow = {}
        newRow['category'] = row[0]
        newRow['description'] = re.sub("[\s]+", " ", row[2])
        newRow['url'] =     row[3]
        newRow['price'] =   row[4]
        newRow['id'] =      row[5]
        
        contact = []
        for c in row[1].split("/"): 
            c = re.sub("[\.\s\-]", "", c)
            contact.append({ "key":"phone", "value":c })
        newRow['contacts'] = contact
        
        
        # extract data
        if newRow['category']=="case-vile":
            newRow['extracted'] = self._extractData_houses(newRow)
        else:
            newRow['extracted'] = self._extractData_apt(newRow)
        
        return newRow
    