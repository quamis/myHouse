# -*- coding: utf-8 -*-

import base.process
import base.HTML 
import re, time

class doProcess(base.process.Processor ):
    def __init__(self, source, maindb, db, cache, args):
        super(doProcess, self).__init__(source, maindb, db, cache, args)
    
    def selectStart(self):
        c = self.db.selectStart("SELECT `id`, `category`, `html`, `url` FROM `imobiliare_ro_data` WHERE 1")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
    def _extractData_houses(self, newRow, row, tree):
        r = tree.asFloat("//*[@id='b_detalii_caracteristici']//table//tr/td[1][contains(text(), 'camere')]/../td[2]/text()")
        newRow['rooms'] = int(r) if r else None
        
        r = tree.asFloat("//*[@id='b_detalii']/div/h3/span[contains(text(), 'teren')]/text()")
        newRow['surface_total'] = float(r) if r else None
        
        r = tree.asFloat("//*[@id='b_detalii']/div/h3/span[contains(text(), 'util')]/text()") or \
            tree.asFloat("//*[@id='b_detalii']/div/h3/span[contains(text(), 'construit')]/text()")
        newRow['surface_built'] = float(r) if r else None
        
        r = tree.asYear(".//*[@id='b_detalii']/div/h3/span[contains(text(), 'An constr')]/text()")
        newRow['year_built'] = int(r) if r else None
        
        return newRow
    
    def _extractData_apt(self, newRow, row, tree):
        r = tree.asFloat(unicode("//*[contains(text(), 'Suprafaţa utilă')]/../*[last()]/text()".decode("utf-8")))
        newRow['surface_built'] = float(r) if r else None
        
        r = tree.asFloat(unicode("//*[contains(text(), 'Suprafaţa construită')]/../*[last()]/text()".decode("utf-8")))
        newRow['surface_total'] = float(r) if r else None
        
        r = tree.asYear("//*[contains(text(), 'An const')]/../*[last()]/text()")
        newRow['year_built'] = int(r) if r else None
        
        
        r = tree.first("//*[contains(text(), 'Etaj')]/../*[last()]/text()")
        m = re.search("(?P<floor>([0-9]+|parter|p|demisol|d|mansarda|m))[\s]*\/[\s]*(?P<floor_max>[0-9]+)", r.lower())
        if m:
            newRow['floor_max'] =  int(m.group('floor_max'))
            
            if m.group('floor')=="mansarda" or m.group('floor')=="m":
                newRow['floor'] = newRow['floor_max']+1
            elif m.group('floor')=="demisol" or m.group('floor')=="d":
                newRow['floor'] =  -1
            elif m.group('floor')=="parter" or m.group('floor')=="p":
                newRow['floor'] =  0
            else:
                newRow['floor'] =  int(m.group('floor'))
                
#            print "%s %s  %s" % (newRow['floor'], newRow['floor_max'], newRow['url'])
#        else:
#            print " %s" % (newRow['url'])
        
        r = tree.first("//*[contains(text(), 'Compartimentare')]/../*[last()]/text()")
        newRow['apartmentType'] =  None
        if r:
            if r=="semidecomandat":
                newRow['apartmentType'] =  "semidec"
            elif r=="nedecomandat":
                newRow['apartmentType'] =  "nondec"
            elif r=="decomandat":
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

        tree = base.HTML.HTML(self.db.decompress(row[2]))
        
        newRow['location'] =   ", ".join(re.split("[\s]*,[\s]*", re.sub("[^a-zA-Z0-9](zona|Sector [0-9])[^a-zA-Z0-9]", "", tree.first("//div[contains(@class, 'titlu')]//span/text()"))))
                
        newRow['price'] = tree.asPrice("//*[@id='b_detalii_titlu']/div/div/div/text()")
        
        newRow['description'] = tree.concat(".//*[@id='b_detalii_text']/div/div/*/text()") or \
                                tree.concat("//*[@id='b_detalii_specificatii']//div[@class='content']//text()")
        
        # extract data
        if newRow['category']=="case-vile":
            newRow = self._extractData_houses(newRow, row, tree)
        else: #apt
            newRow = self._extractData_apt(newRow, row, tree)
            
        newRow = super(doProcess, self).extractData_base(newRow)
        
        return newRow
    