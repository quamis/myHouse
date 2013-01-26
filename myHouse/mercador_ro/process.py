import base.process
import base.HTML 
import re, time

class doProcess( base.process.Processor ):
    def __init__(self, source, maindb, db, cache, args):
        super(doProcess, self).__init__(source, maindb, db, cache, args)
    
    def selectStart(self):
        c = self.db.selectStart("SELECT `id`, `category`, `html`, `url` FROM `mercador_ro_data` WHERE 1")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
    
    def _processRow(self, row):
        newRow = {}
        newRow['id'] =      row[0]
        newRow['category'] =row[1]
        newRow['url'] =     row[3]

        tree = base.HTML.HTML(self.db.decompress(row[2]))
        
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
        
        newRow['description'] =                 tree.first(".//div[contains(@class, 'offerdescription')]/p[contains(@class, 'large')]/text()")
        
        newRow = self.processor_helper.extract_year(newRow, newRow['description'])
        

        if re.search("apartament", newRow['description']) and re.search("etaj", newRow['description']):
            print("\nThis is not the correct category(its an apartment). Ignoring")
            return None
        
        if re.search("cumpar", newRow['description']):
            print("\nThis is not the correct category(this guy buys stuff, not selling). Ignoring")
            return None
    
        newRow = super(doProcess, self).extractData_base(newRow)
        
        return newRow
    