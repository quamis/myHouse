# -*- coding: utf-8 -*-

import sources.base.Processor.Processor as Processor
import sources.base.HTML as HTML

import re

class doProcess( Processor.Processor ):
    def selectStart(self):
        c = self.db.selectStart("SELECT `id`, `category`, `html`, `url` FROM `romino_ro_data` WHERE 1")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
    def _processRow(self, row):
        newRow = {}
        newRow['id'] =      row[0]
        newRow['category'] =row[1]
        newRow['url'] =     row[3]

        tree = HTML.HTML(self.db.decompress(row[2]))
        
        newRow['location'] =   ", ".join(filter(None, [
              tree.first(".//div[@id='details']//td//*[contains(text(), 'Localitatea')]/../../td[2]//span//text()"),
              tree.first(".//div[@id='details']//td//*[contains(text(), 'Zona')]/../../td[2]//span//text()"),
              tree.first(".//div[@id='details']//td//*[contains(text(), 'Adresa')]/../../td[2]//span//text()"),
          ]))
                
        newRow['price'] = tree.asPrice(".//div[@id='details']//td//*[contains(text(), 'Pret')]/../../td[2]//span//text()")
        if newRow['price']<10000:
            return None
        
        newRow['description'] = tree.first(".//div[@id='description']//p/text()")
        newRow['description']+= "\n"+", ".join(filter(None, [
              tree.conditional("Incalzire: ", tree.first(".//div[@id='details']//td//*[contains(text(), 'Incalzire')]/../../td[2]//span//text()")),
              tree.conditional("Gradina: ", tree.first(".//div[@id='details']//td//*[contains(text(), 'Gradina')]/../../td[2]//span//text()")),
              tree.conditional("Pivnita: ", tree.first(".//div[@id='details']//td//*[contains(text(), 'Pivnita')]/../../td[2]//span//text()")),
              tree.conditional("Terasa: ", tree.first(".//div[@id='details']//td//*[contains(text(), 'Terasa')]/../../td[2]//span//text()")),
              tree.conditional("Bai: ", tree.first(".//div[@id='details']//td//*[contains(text(), 'Numar bai')]/../../td[2]//span//text()")),
              tree.conditional("Etaje: ", tree.first(".//div[@id='details']//td//*[contains(text(), 'Numar nivele')]/../../td[2]//span//text()")),
          ]))
        newRow['description'] = tree.sanitize(newRow['description'].strip())
        
        if not newRow['description']:
            return None
        
        newRow['year_built'] = tree.asYear(".//div[@id='details']//td//*[contains(text(), 'Anul construirii')]/../../td[2]//span//text()")

        newRow['surface_built'] = tree.asFloat(".//div[@id='highDetails']//td//*[contains(text(), 'Suprafata utila')]/../../td[2]//span//text()")
        newRow['surface_total'] = tree.asFloat(".//div[@id='highDetails']//td//*[contains(text(), 'Suprafata terenului')]/../../td[2]//span//text()")
        
        newRow['rooms'] =         tree.asInt(".//div[@id='highDetails']//td//*[contains(text(), 'Numar camere')]/../../td[2]//span//text()")

        if re.search("(apartament|garsoniera)", newRow['description']) and re.search("etaj", newRow['description']):
            #print("\nThis is not the correct category(its an apartment). Ignoring")
            return None
        
        if re.search("cumpar", newRow['description']):
            #print("\nThis is not the correct category(this guy buys stuff, not selling). Ignoring")
            return None
        
        src = tree.first(".//tbody[@id='phoneBox']//*[contains(text(), 'Telefon')]/../..//img/@src")
        contact = []
        m = re.search("(?P<phone>[0-9]{10})$", src)
        if m and m.group('phone'):
            contact.append({ "key":"phone", "value":m.group('phone') })

        newRow['contacts'] = contact            

        # extract data
        if newRow['category']=="case-vile":
            newRow = self._extractData_houses(newRow, row, tree)
        else: #apt
            newRow = self._extractData_apt(newRow, row, tree)
            
        newRow = super(doProcess, self).extractData_base(newRow)

        return newRow
    