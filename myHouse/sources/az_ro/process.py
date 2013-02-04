# -*- coding: utf-8 -*-

import sources.base.Processor.Processor as Processor
import sources.base.HTML as HTML
 
import re, time

class doProcess( Processor.Processor ):
    def selectStart(self):
        c = self.db.selectStart("SELECT `id`, `category`, `html`, `url` FROM `az_ro_data` WHERE 1")
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
        
        locations =     re.sub(" (-|\/) Ilfov", "", re.sub("Localitate", "", tree.concat(".//*[@id='specs']/li/strong[contains(text(), 'Localitate')]/../*/text()", False))).strip()
        m = re.match("(?P<loc1>[^\n]+)\n(?P<loc2>[^\n]+)", locations)
        loc = ""
        if m:
            loc =  m.group("loc2") + " - " + m.group("loc1")
        newRow['location'] = loc
        
        newRow['description'] = tree.concat(".//div[contains(@class, 'az-content-body')]//text()")

        contacts =       tree.concat(".//div[contains(@class, 'az-content-contact')]/span[contains(@class, 'act-phone')]/a/text()")
        contact = []
        for c in contacts.split(" "):
            if c:
                contact.append({ "key":"phone", "value": c})
        newRow['contacts'] = contact
        
        newRow['price'] = tree.asPrice(".//div[contains(@class, 'az-price')]/text()")

        if newRow['category']=="case-vile":
            newRow = self._extractData_houses(newRow)
        else:
            newRow = self._extractData_apt(newRow)
        
        newRow = super(doProcess, self).extractData_base(newRow)
        
        return newRow
    