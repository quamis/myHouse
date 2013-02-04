# -*- coding: utf-8 -*-

import sources.base.Processor.Processor as Processor
import sources.base.HTML as HTML
 
import re

class doProcess( Processor.Processor ):
    def selectStart(self):
        c = self.db.selectStart("SELECT `id`, `category`, `html`, `url` FROM `mercador_ro_data` WHERE 1")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
    
    def _extractData_houses(self, newRow, row, tree):
        return newRow
    
    def _extractData_apt(self, newRow, row, tree):
        # this isn't actually tested, we cannot gather too many announcements from this site, so i'm only gathering houses, no apartments
        
        desc = newRow['description']
        newRow = self.processor_helper.extract_floor(newRow, desc, "apt")
         
        r =    tree.first(".//table[contains(@class, 'details')]//div[contains(text(), 'Compartimentare')]/strong//text()")
        newRow['apartmentType'] =  None
        if r:
            r = r.lower()
            if r=="semidecomandat" or r=="semi-decomandat":
                newRow['apartmentType'] =  "semidec"
            elif r=="nedecomandat":
                newRow['apartmentType'] =  "nondec"
            elif r=="decomandat" or r=="comandat":
                newRow['apartmentType'] =  "dec"
            elif r=="circular":
                newRow['apartmentType'] =  "nondec"
            elif r=="vagon":
                newRow['apartmentType'] =  "nondec"
            elif r=="---":
                newRow['apartmentType'] =  None
#            else:
#                print "Unknwon apartmentType: '%s'" % (r)
#        print "ApartmentType: '%s'\n" % (newRow['apartmentType'])    
            
        
        return newRow
        
    def _processRow(self, row):
        newRow = {}
        newRow['id'] =      row[0]
        newRow['category'] =row[1]
        newRow['url'] =     row[3]

        tree = HTML.HTML(self.db.decompress(row[2]))
        
        newRow['location'] =      tree.first("..//p[contains(@class, 'addetails')]//strong[contains(@class, 'brrighte5')]/text()")
        
        p = tree.first(".//div[contains(@class, 'pricelabel')]/strong[contains(@class, 'xxxx-large')]/text()")
        if re.search("lei", p):
            m = re.search("^(?P<price>[0-9]+)", re.sub("[\s]", "", p))
            p = round(self.currencyConverter.RONEUR(float(m.group('price'))))
        else:
            m = re.search("^(?P<price>[0-9]+)", re.sub("[\s]", "", p))
            p = float(m.group('price'))
            
        newRow['price'] = p
        
        newRow['surface_total'] =  tree.asFloat(".//table[contains(@class, 'details')]//div[contains(text(), 'Suprafata')]/strong/text()")
        
        newRow['rooms'] =          int(tree.asFloat(".//table[contains(@class, 'details')]//div[contains(text(), 'Camere')]/strong/*/text()"))
        
        newRow['description'] =    tree.first(".//div[contains(@class, 'offerdescription')]/p[contains(@class, 'large')]/text()")
        
        newRow = self.processor_helper.extract_year(newRow, newRow['description'])
        

        if re.search("apartament", newRow['description']) and re.search("etaj", newRow['description']):
            print("\nThis is not the correct category(its an apartment). Ignoring")
            return None
        
        if re.search("cumpar", newRow['description']):
            print("\nThis is not the correct category(this guy buys stuff, not selling). Ignoring")
            return None
    
        if newRow['category']=="case-vile":
            newRow = self._extractData_houses(newRow, row, tree)
        else:
            newRow = self._extractData_apt(newRow, row, tree)
            
        
        newRow = super(doProcess, self).extractData_base(newRow)
        
        return newRow
    