import base.process

import re

class doProcess(base.process.Processor ):
    def __init__(self, source, maindb, db, cache, args):
        super(doProcess, self).__init__(source, maindb, db, cache, args)
    
    def selectStart(self):
        #                                 0          1           2        3      4              5        6                7    
        c = self.db.selectStart("SELECT `category`, `location`, `rooms`, `url`, `description`, `price`, `surface_total`, `id` FROM `mercador_ro_data` WHERE 1 ORDER BY `category` ASC, `description` ASC")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
    
    def _extractData_houses(self, newRow, row):
        extr = {}
        if row[1]:
            extr['location'] = row[1]
            
        if row[2]:
            extr['rooms'] = row[2]
            
        if row[6]:
            extr['surface_total'] = row[6]

        if newRow['price']!="" and "surface_built" in extr:
            extr['price_per_mp_built'] = round(float(newRow['price'])/float(extr['surface_total']), 0)
            
        return extr
        
    def _processRow(self, row):
        newRow = {}
        newRow['category'] = row[0]
        newRow['description'] = re.sub("[\s]+", " ", row[4])
        newRow['url'] =     row[3]
        newRow['price'] =   row[5]
        newRow['id'] =      row[7]
        
        # extract data
        if newRow['category']=="case-vile":
            newRow['extracted'] = self._extractData_houses(newRow, row)
        
                
        #print newRow
        return newRow
    