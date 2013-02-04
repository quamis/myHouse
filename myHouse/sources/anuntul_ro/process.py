# -*- coding: utf-8 -*-

import sources.base.process as base
import sources.base.HTML as HTML

import re, time

class doProcess(base.Processor ):
    def __init__(self, source, maindb, db, cache, args):
        super(doProcess, self).__init__(source, maindb, db, cache, args)
    
    def selectStart(self):
        c = self.db.selectStart("SELECT `id`, `category`, `html`, `url` FROM `anuntul_ro_data` WHERE 1")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
    def _extractData_houses(self, newRow):
        desc = newRow['description']
        
        newRow = self.processor_helper.extract_location(newRow, desc)
        newRow = self.processor_helper.extract_rooms(newRow, desc)
        newRow = self.processor_helper.extract_year(newRow, desc)
        newRow = self.processor_helper.extract_surface(newRow, desc, "case-vile")
        
        return newRow
    
    def _extractData_apt(self, newRow):
        desc = newRow['description']
        
        newRow = self.processor_helper.extract_location(newRow, desc)
        newRow = self.processor_helper.extract_rooms(newRow, desc)
        newRow = self.processor_helper.extract_year(newRow, desc)
        newRow = self.processor_helper.extract_surface(newRow, desc, "apt")
        
        newRow = self.processor_helper.extract_floor(newRow, desc, "apt")
        newRow = self.processor_helper.extract_apartmentType(newRow, desc, "apt")

        return newRow
        
    def _processRow(self, row):
        newRow = {}
        newRow['id'] =      row[0]
        newRow['category'] =row[1]
        newRow['url'] =     row[3]

        tree = HTML.HTML(self.db.decompress(row[2]))
        
        newRow['description'] = tree.first("//table[@id='detalii_anunt']//div[@class='detalii_txt']/text()")
        newRow['location'] =    tree.first("//table[@id='detalii_anunt']//div[@class='detalii_txt']/strong/text()")

        contactStr =     tree.first("//table[@id='detalii_anunt']//div[@class='contact']/text()")
        contact = []
        for c in contactStr.split("/"): 
            c = re.sub("[\.\s\-]", "", c)
            contact.append({ "key":"phone", "value":c })
        newRow['contacts'] = contact
        
        newRow['price'] = tree.asPrice("//table[@id='detalii_anunt']//span[@class='pret']/text()")
        
        # extract data
        if newRow['category']=="case-vile":
            newRow = self._extractData_houses(newRow)
        else:
            newRow = self._extractData_apt(newRow)
            
        newRow = super(doProcess, self).extractData_base(newRow)
        
        return newRow
    