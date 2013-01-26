# -*- coding: utf-8 -*-

import base.process
import base.HTML 
import re, time

class doProcess(base.process.Processor ):
    def __init__(self, source, maindb, db, cache, args):
        super(doProcess, self).__init__(source, maindb, db, cache, args)
    
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
            
        return newRow
        
    def _processRow(self, row):
        newRow = {}
        newRow['id'] =      row[0]
        newRow['category'] =row[1]
        newRow['url'] =     row[3]

        tree = base.HTML.HTML(self.db.decompress(row[2]))
        
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
    