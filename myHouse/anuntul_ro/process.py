import base.process

import re
import logging


class doProcess(base.process.Processor ):
    def __init__(self, source, maindb, db, cache):
        super(doProcess, self).__init__(source, maindb, db, cache)
    
    def selectStart(self):
        c = self.db.selectStart("SELECT `category`, `contact`, `description`, `url`, `price`, `id`  FROM `anuntul_ro_data` WHERE 1")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
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
        #raise SystemExit
        newRow['contacts'] = contact
        print newRow
        return newRow