# -*- coding: utf-8 -*-

import sources.base.Processor.Processor as Processor
import sources.base.HTML as HTML
 
import re, time

class doProcess( Processor.Processor ):
    def selectStart(self):
        c = self.db.selectStart("SELECT `id`, `category`, `html`, `url` FROM `imopedia_ro_data` WHERE 1")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
    def _extractData_houses(self, newRow, row, tree):
        newRow['surface_total'] =     tree.asFloat(".//div[@id='informatii']//ul/li[contains(text(), 'total teren')]/text()")
        newRow['surface_built']  =    tree.asFloat(".//div[@id='informatii']//ul//*[contains(text(), 'suprafata construita')]/../text()") or \
                                    tree.asFloat(".//div[@id='informatii']//ul//*[contains(text(), 'suprafata utila')]/../text()")
                                    
        x = tree.asFloat(".//div[@id='informatii']//ul/li[contains(text(), 'teren liber')]/text()")
        if x:
            if newRow['surface_total'] and not newRow['surface_built']:
                newRow['surface_built'] = newRow['surface_total'] - x 
        
            if not newRow['surface_total'] and newRow['surface_built']:
                newRow['surface_total'] = newRow['surface_built'] + x
                
        return newRow
    
    def _extractData_apt(self, newRow, row, tree):
        newRow['surface_total'] =      tree.asFloat(".//div[@id='informatii']//ul/li//*[contains(text(), 'suprafata utila')]/../text()")
        newRow['surface_built'] =      tree.asFloat(".//div[@id='informatii']//ul/li//*[contains(text(), 'suprafata construita')]/../text()")
        if not newRow['surface_total'] and newRow['surface_built']:
            newRow['surface_total'] = newRow['surface_built']
        
        
        r = tree.first(".//div[@id='informatii']//ul//*[contains(text(), 'etaj')]/text()")
        m = re.search("(?P<floor>([0-9]+|parter|p|demisol|d|mansarda|m))[\s]*\/[\s]*([p\+]*)[\s]*(?P<floor_max>[0-9]+)", r.lower())
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
#            print ". %s" % (newRow['url'])
        
        r = tree.first(".//div[@id='informatii']//ul//*[contains(text(), 'comandat')]/text()")
        newRow['apartmentType'] =  None
        if r:
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
        
        newRow['location'] =      tree.first(".//div[contains(@class, 'det')]//strong[contains(text(), 'Zona')]/span/text()") or \
                                  tree.first(".//div[contains(@class, 'det')]//span[contains(@class, 'color_2')]/text()")

        newRow['price'] =         tree.asPrice(".//div[contains(@class, 'pret_1')]/strong/text()")
        
        t = re.search("(?P<rooms>[0-9]+) camere", tree.concat(".//*[@id='info_oferta']//div[contains(@class, 'info_2')]/text()"))
        newRow['rooms'] = t.groups('rooms')[0] if t else None

        description = tree.concat(".//div[contains(@class, 'alte_informatii')]//text()")
        lis = tree.xpath(".//*[@id='informatii']//div[contains(text(), 'utile')]/../ul/li")
        s=""
        for li in lis:
            li = tree.extend(li)
            tx = li.concat(".//text()")
            tx = re.sub("-", "", tx)
            tx = re.sub("[\s]+", " ", tx)
            tx = tx.strip()
            if tx:
                description+= s + tx
                s=". "
        newRow['description'] =   description.strip()
        
        if newRow['category']=="case-vile":
            newRow = self._extractData_houses(newRow, row, tree)
        else:
            newRow = self._extractData_apt(newRow, row, tree)
                
        newRow['year_built'] = tree.asYear(".//div[@id='informatii']//ul/li[contains(text(), 'construit in')]/text()")

        newRow = super(doProcess, self).extractData_base(newRow)
                            
        return newRow
    