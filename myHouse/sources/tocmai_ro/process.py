# -*- coding: utf-8 -*-

import sources.base.Processor.Processor as Processor
import sources.base.HTML as HTML
 
import re, time

class doProcess( Processor.Processor ):
    def selectStart(self):
        c = self.db.selectStart("SELECT `id`, `category`, `html`, `url` FROM `tocmai_ro_data` WHERE 1")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
        
    def _extractData_houses(self, newRow, row, tree):
        return newRow
    
    def _extractData_apt(self, newRow, row, tree):
        desc = newRow['description']
        newRow = self.processor_helper.extract_floor(newRow, desc, "apt")
        newRow = self.processor_helper.extract_apartmentType(newRow, desc, "apt")
        return newRow
        
    def _processRow(self, row):
        newRow = {}
        newRow['id'] =      row[0]
        newRow['category'] =row[1]
        newRow['url'] =     row[3]

        tree = HTML.HTML(self.db.decompress(row[2]))
        
        location1 =     tree.first(".//*[@id='main']//div/p/b[contains(text(), 'Localitate')]/../text()")
        location2 =     tree.first(".//*[@id='main']//div/p/b[contains(text(), 'Zona')]/../text()")
        if location1 and location2:
            newRow['location'] =      ", ".join((location1, location2))
        elif location1:
            newRow['location'] =      location1
        elif location2:
            newRow['location'] =      location2
            
        
        newRow['price'] =   tree.asPrice(".//*[@id='main']//span[@itemprop= 'price']/text()")
        if not newRow['price']:
            newRow['price']=tree.asPrice(".//*[@id='main']//div[contains(text(), 'Pret')]/text()")
            
        newRow['surface_total'] = tree.asFloat(".//*[@id='main']//div/p/b[contains(text(), 'Suprafata')]/../text()")
        
        newRow['rooms'] =         int(tree.asFloat(".//*[@id='main']//div/p/b[contains(text(), 'camere')]/../text()"))
        
        newRow['description'] =      tree.concat(".//*[@id='main']//div[contains(@class, 'item-description')]/text()")
        
        newRow = self.processor_helper.extract_year(newRow, newRow['description'])
        
        if newRow['category']=="case-vile":
            if not re.search("(vila|casa|curte)", newRow['description']) and re.search("apartament", newRow['description']) and re.search("etaj", newRow['description']):
                newRow['category'] = "apt-%d-cam" %(max(2, min(4, newRow['rooms'])))
        
        if newRow['category']=="case-vile":
            newRow = self._extractData_houses(newRow, row, tree)
        else:
            newRow = self._extractData_apt(newRow, row, tree)
            
            
        newRow = super(doProcess, self).extractData_base(newRow)
            
        return newRow
    