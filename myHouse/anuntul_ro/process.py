import base.process
import re

class doProcess(base.process.Processor ):
    def __init__(self, source, maindb, db, cache, args):
        super(doProcess, self).__init__(source, maindb, db, cache, args)
    
    def selectStart(self):
        c = self.db.selectStart("SELECT `category`, `contact`, `description`, `url`, `price`, `id`  FROM `anuntul_ro_data` WHERE 1 ORDER BY `category` ASC, `description` ASC")
        return c
    
    def selectEnd(self, c):
        self.db.selectEnd(c)
        
    def myTrim(self, regex, text):
        tx = ""
        while tx!=text:
            tx = text
            text = re.sub(regex, "", tx)
        return text
    
    def _extractData_houses(self, newRow):
        extr = {}
        desc = newRow['description']
        
        m = re.search("^(?P<location>([A-Za-z0-9-\.]+( |(?=,)))+)", desc)
        if m:
            extr['location'] = self.myTrim("[\s](\
                                                ocazie|\
                                                vila|\
                                                oras|\
                                                prop(r)?ietar(\.)?|\
                                                sector [0-9]|\
                                                stradal|\
                                                nr(\.)? [0-9]+[A-Z]?|\
                                                [0-9] km de .+\
                                                -|\
                                                [\s])[\s]*$", 
                                                          m.group('location'))
        
        
        m = re.search("(?P<rooms>[0-9]+)[\s](dormitoare|camere|cam\.|cam)", desc)
        if m:
            extr['rooms'] = m.group('rooms')
            

        # extract surface_built
        if "surface_built" not in extr:        
            m = re.search("(utili|amprenta|casa|casa de|suprafata (utila|casei|casa)|supr(\.)? (utila|casei|casa)|utila|su|s\.u\|suprafata( de)?.|construita( de)?.)[\s]?(?P<supr>[0-9]+)[\s]?(mpu|mp|m\.p\.)", desc)
            if m:
                extr['surface_built'] = m.group('supr')
                
        if "surface_built" not in extr:        
            m = re.search("[\s]?(?P<supr>[0-9]+)[\s]?(mpu|mpc)", desc)
            if m:
                extr['surface_built'] = m.group('supr')
                
        if "surface_built" not in extr:        
            m = re.search("[\s]?(?P<supr>[0-9]+)[\s]?(mp|m\.p\.) (amprenta|utili|construiti|constr(\.)?)", desc)
            if m:
                extr['surface_built'] = m.group('supr')
                
                
        # extract surface_total
        if "surface_total" not in extr:        
            m = re.search("(?P<supr>[0-9\.]+)[\s]?(mp|m\.p\.) (total teren|teren)", desc)
            if m:
                extr['surface_total'] = re.sub("(\.|\,)", "", m.group('supr'))
                
        if "surface_total" not in extr:        
            m = re.search("(curte de|curte|teren|supr|suprafata)[\s]?(?P<supr>[0-9\.]+)[\s]?(mp|m\.p\.)", desc)
            if m:
                extr['surface_total'] = re.sub("(\.|\,)", "", m.group('supr'))
                
        if "surface_total" not in extr:        
            m = re.search("(?P<supr>[0-9\.]+)[\s]?(mp|m\.p\.)", desc)
            if m:
                extr['surface_total'] = re.sub("(\.|\,)", "", m.group('supr'))
                extr['surface_built'] = re.sub("(\.|\,)", "", m.group('supr'))
                
        # default, final search
        if "surface_total" in extr and "surface_built" not in extr:        
            m = re.search("(?P<supr>[0-9\.]+)[\s]?(mp|m\.p\.)", desc)
            if m:
                b = re.sub("(\.|\,)", "", m.group('supr'))
                if b!=extr['surface_total']:
                    extr['surface_built'] = b
                     

        if "surface_built" in extr and float(extr['surface_built'])>0:
            extr['price_per_mp_built'] = round(float(newRow['price'])/float(extr['surface_built']), 0)
            
        return extr
        
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
        newRow['contacts'] = contact
        
        
        # extract data
        if newRow['category']=="case-vile":
            newRow['extracted'] = self._extractData_houses(newRow)
        
                
            #raise SystemExit  
        
        #raise SystemExit
        
        
        #print newRow
        return newRow
    