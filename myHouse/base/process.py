import time, sys, re

class Processor(object):
    def __init__(self, source, maindb, db, cache, args):
        self.args = args
        self.source = source
        self.db = db
        self.maindb = maindb
        self.cache = cache
        
        self.processor_helper = Processor_helper()

        #email, phones        
        self.maindb.tableCreate("data", { 
            "id":           "VARCHAR(64)",
			"status":       "VARCHAR(128)",
            "category":     "VARCHAR(64)",
            "source":       "VARCHAR(16)",  # anunturi_ro
            "url":          "VARCHAR(256)",
            "price":        "INT",
            "description":  "TEXT",
            "addDate":      "INT",
            "updateDate":   "INT",
        }, ["id"])
        
        self.maindb.tableCreate("data_contacts", { 
            "idOffer":      "VARCHAR(64)",
            "key":          "VARCHAR(16)",  # email, telephone, address
            "value":        "VARCHAR(256)",
        }, [], ["id"])
        
        self.maindb.tableCreate("data_extracted", { 
            "idOffer":      "VARCHAR(64)",
            "key":          "VARCHAR(16)",
            "value":        "VARCHAR(256)",
        }, [], ["id"])

    def selectStart(self):
        pass
    
    def selectEnd(self):
        pass
    
    def _processRow(self, row):
        pass

    def debug_print(self, result, extra=None):
        # 0 = none, 1: only importans, 2: dots, 3: debug
        if(self.args.verbosity>=1):
            self.debug_print_1(result, extra)
        elif(self.args.verbosity>=0):
            self.debug_print_0(result, extra)
            
    
    def debug_print_1(self, result, extra=None):
        if(result=="loop-error"):
            sys.stdout.write("\n # %s -> %s" % ("error on", extra['url']))
            
        if(result=="loop-step"):
            pass
        
        if(result=="loop-new"):
            if not extra['price']:
                extra['price'] = 1
            sys.stdout.write("\n    % 9dEUR %s" % (extra['price'], extra['url']))
            
        if(result=="loop-old"):
            #sys.stdout.write('.')
            pass
            
        sys.stdout.flush()
    
    def debug_print_0(self, result, extra=None):
        pass

    def run(self):
        rows = self.selectStart();
        timestamp = time.time()
        
        index=0
        for row in rows:
            self.debug_print("loop-step", { "index": index })
            index+=1
            newRow = self._processRow(row)
            if newRow is None:
                continue
            
            if(self.maindb.itemExists("data", newRow['id'])):
                if self.args.forceUpdate:
                    self.maindb.execute("DELETE FROM `data_contacts` WHERE `idOffer`='%s'" %(newRow['id']))
                    self.maindb.execute("DELETE FROM `data_extracted` WHERE `idOffer`='%s'" %(newRow['id']))
                    
                    if 'contacts' in newRow:
                        for c in newRow['contacts']:
                            self.maindb.itemInsert("data_contacts", { "idOffer":newRow['id'], "key": c['key'], "value": c['value'] })
                            
                    if 'extracted' in newRow:
                        for k,v in newRow['extracted'].items():
                            self.maindb.itemInsert("data_extracted", { "idOffer":newRow['id'], "key": k, "value": v })
                            
                    self.maindb.itemUpdate("data", {
                          "source":     self.source, 
                          "id":         newRow['id'],
                          "category":   newRow['category'], 
                          "url":        newRow['url'], 
                          "price":      newRow['price'],
                          "description":newRow['description'],
                          "updateDate": timestamp,
                      })
                else:
                    self.maindb.itemUpdate("data", { "id": newRow['id'], "updateDate": timestamp, })
                    
                self.debug_print("loop-old", newRow)
            else:
                self.debug_print("loop-new", newRow)
                
                if 'contacts' in newRow:
                    for c in newRow['contacts']:
                        self.maindb.itemInsert("data_contacts", { "idOffer":newRow['id'], "key": c['key'], "value": c['value'] })
                        
                if 'extracted' in newRow:
                    for k,v in newRow['extracted'].items():
                        self.maindb.itemInsert("data_extracted", { "idOffer":newRow['id'], "key": k, "value": v })
                        
                self.maindb.itemInsert("data", {
                      "status":     "",
                      "source":     self.source, 
                      "id":         newRow['id'],
                      "category":   newRow['category'], 
                      "url":        newRow['url'], 
                      "price":      newRow['price'],
                      "description":newRow['description'],
                      "addDate":    timestamp,
                      "updateDate": timestamp,
                  })
                self.db.flushRandom(0.025, False)
                
            
        self.selectEnd(rows)
        self.maindb.close()




class Processor_helper(object):
    def __init__(self):
        self.presets = {}
        self.presets['case-vile'] = {}
        self.presets['case-vile']['reformatter'] = {}
        self.presets['case-vile']['reformatter']['extractLocation'] = {
                 'replace:content': {
                    "[\s]*-[\s]*" : " - ",
                    "[^a-z](facultate|facultatea)[^a-z]*" : " Facultate ",
                    "[^a-z](sos\.)[^a-z]*" : " sos. ",
                    "[^a-z](metrou)[^a-z]*" : " ",
                 },
                 'cleanup:tail': (
                    "ocazie", "urgent", "deosebit(a)", "lux", "ieftin(a)?",
                    "(constr|construcita|contruit)([\s]*|\.|\,)[0-9]+",
                    "(supr|supraf|suprafata)", "mp", "[0-9]+[\s]*m", "[0-9]+[\s]*mp", "[0-9]+[\s]*m2",
                    "de", "in", "la", "cu", "si", "are",
                    "teren(ul)?", "zona", "cheie",
                    "metrou", "stati(a|e)",
                    "vil(a|e)", "cas(a|e)", 
                    "gars", "garsonier(a|e)", 
                    "apt", "apart", "apartament(e)?",
                    "duplex",
                    "(vand|vanzare)", "schimb", "zona", "foarte", "linistit(a)?", 
                    "central", "ultracentral(a)?", "central(a)?",
                    "caramida", "bca", "paianta", "pamant",    
                    "bucatarie", "living", "dormitor", "dormitoare",
                    "utilat(a)?", "mobilat(a)?",   
                    "[0-9]+ (cam|camera|camere)(\.)?", 
                    "oras", "sector [0-9]", "intrare",  
                    "istorie", "istoric(a)?", "valoare",  
                    "arhitectura", "arhitecturala", 
                    "prop(r)?ietar(\.)?", "particular",
                    "acces", "toate", "actele", "locuibil(a)?", "demolabil(a)?", "facilitati(le)?",  
                    "strada", "stradal(a)?", "asfaltat(a)?", "pta", "piata", "p-ta", 
                    "scoala", "gradinita", "cablu", "tv", "telefon", "curent(a)?", "apa", "canalizare", "gaz", "utilitati(le)?",
                    "nr(\.)? ([0-9]+[A-Z])?",
                    "[0-9\.]+ km de (.+)", 
                    "-", "[\s]", "\."
                    ) 
                 }
        
    def reformat(self, text, formulas = { }):
        tx = ""
        
        if "cleanup:tail" in formulas:
            while tx!=text:
                tx = text
                text = re.sub("([\s]|^)("+"|".join(formulas['cleanup:tail'])+")[\s]*$", "", tx, 0, re.IGNORECASE)
                
        if "replace:content" in formulas:
            for k in formulas["replace:content"].iterkeys():
                text = re.sub(k, formulas["replace:content"][k], text, 0, re.IGNORECASE)
                
        return text
    
    def extract_withFormula(self, text, formulas):
        match = None
        m=None
        if "match:content" in formulas:
            if "match" in formulas:
                rx_match = "[\s]*(?P<match>"+formulas['match']+")[\s]*"
            else:
                rx_match = "[\s]*(?P<match>[0-9\.]+)[\s]*"
                
            rx="([\s]|^)"\
                 "("+"|".join(formulas['match:content'][0])+")"\
                 +rx_match+\
                 "("+"|".join(formulas['match:content'][1])+")"\
                 "(\.|\,|[\s]|=|\)|\(|$)"
            m = re.search(rx, text, re.IGNORECASE)
            
        elif "match:raw" in formulas:
            rx=formulas["match:raw"]
            m = re.search(rx, text, re.IGNORECASE)
            

        if m:
            s = m.group('match')
            
            if s:
                if re.search("^[0-9]+(\.|\,)[0-9]{,2}$", s):
                    s = re.sub("(\.|\,)[0-9]{,2}$", "", s)
                    
                s = re.sub("(\.|\,)", "", s)
                if s:
                    try:
                        if "type" in formulas:
                            if formulas['type']=='int':
                                match = int(s)
                            elif formulas['type']=='float':
                                match = int(s)
                            elif formulas['type']=='str':
                                match = str(s)
                        else:
                            match = float(s)
                    except ValueError, e:
                        print "Cannot convert '%s' to number: %s" % (s, e)
                
        return match
    
    def extract_location(self, extr, text):
        s = None
        m = re.search("^(?P<location>([A-Za-z0-9-\.]+( |(?=,)))+)", text)
        if m:
            extr['location']  = m.group('location')
            s = self.reformat(extr['location'], self.presets['case-vile']['reformatter']['extractLocation'])
            if s:
                print "extract: location #2: %s" % (s)
                extr['location'] = s
            else:
                print "extract: location #1: %s" % (s)
        
        if s is None:
            print "extract: location: NOT FOUND"        
                
        return extr
            
    def extract_rooms(self, extr, text):
        s = None    
        if s is None:
            s = self.extract_withFormula(text, {
                  'type':'int',
                  'match:raw': "(?P<match>[0-9]+)[\s]*("+"|".join([ "dormitoare", "dorm", "camere", "cam\.", "cam"])+")"
            })
            if s:
                print "extract: rooms #1: %s" % (s)
                
        if s is None:
            print "extract: rooms: NOT FOUND"
        
        if s:
            extr['rooms'] = s
            
        return extr
    
    def convert_location(self, extr, text):
        return extr
    
    def extract_year(self, extr, text):
        s = None    
        # remove the location from the text, basically we might get distracted by area like "1 decembrie 1918"
        if 'location' in extr: 
            text = re.sub(extr['location'], "", text)
            
        if s is None:
            s = self.extract_withFormula(text, {
                  'type':'int',
                  'match':'(18|19|20)[0-9]{2}',
                  'match:content':((
                        "construit(a)", 
                        "constructie",
                        "bloc",  
                        "in",
                        "din",
                   ), ()),
            })
            if s:
                print "extract: year_built #1: %s" % (s)
        
        if s is None:
            s = self.extract_withFormula(text, {
                  'type':'int',
                  'match':'(18|19|20)[0-9]{2}',
                  'match:content':((), ()),
            })
            if s:
                print "extract: year_built #2: %s" % (s)
                
        if s is None:
            print "extract: year_built: NOT FOUND"
        
        if s:
            extr['year_built'] = s
            
        return extr
    

    def extract_surface(self, extr, text, profile):
        
        mpu = ["mpu", "mpc", "m\.p\.c\.", "m\.p\.", "mp", "m2", "metri patrati"]
        mpt = ["m\.p\.", "mp", "m2", "metri patrati"]
        
        # extract surface_built
        if profile=="case-vile":
            s = None
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((
                          "utili|utila", 
                          "amprenta", 
                          "casa", 
                          "casa de", 
                          "suprafata (utila|casei|casa|construita|constr\.|locuibila)(:)?", 
                          "sup(r)?(\.)? (utila|casei|casa|construita|constr\.|locuibila)(:)?", 
                          "s(\.)?u(\.)?", 
                          "sc(=|-|\s)?",
                          "suprafata( de)?.", 
                          "construita( de)?."), 
                          mpu
                     )})
                if s:
                    print "extract: surface_built #1: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((
                          "utili|utila", 
                          "amprenta", 
                          "casa", 
                          "casa de", 
                          "suprafata (utila|casei|casa|construita|constr\.|locuibila)(:)?", 
                          "sup(r)?(\.)? (utila|casei|casa|construita|constr\.|locuibila)(:)?", 
                          "s(\.)?u(\.)?", 
                          "sc(=|-|\s)?",
                          "suprafata( de)?.", 
                          "(construita|constructie|constructia)( de)?."), 
                          []
                     )})
                if s:
                    print "extract: surface_built #1: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          ( "("+ "|".join(mpu) + ")[\s]+"+
                            "("+ "|".join(("amprenta", "utili", "construiti", "constr(\.)?")) + ")",
                           )
                     )})
                if s:
                    print "extract: surface_built #2: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          mpu
                     )})
                if s:
                    print "extract: surface_built #3: %s" % (s)
                
            if s is None:
                print "extract: surface_built: NOT FOUND"
                
            if s:
                extr['surface_built'] = s
                
                
        elif profile=="apt":
            s = None
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((
                          "utili|utila", 
                          "suprafata (utila|construita|constr\.|locuibila)(:)?", 
                          "sup(r)?(\.)? (utila|casei|casa|construita|constr\.|locuibila)(:)?", 
                          "s(\.)?u(\.)?", 
                          "sc(=|-|\s)?",
                          "suprafata( de)?.", 
                          "construita( de)?."), 
                          mpu
                     )})
                if s:
                    print "extract: surface_built #1: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          ( "("+ "|".join(mpu) + ")[\s]+"+
                            "("+ "|".join(("utili", "construiti", "constr(\.)?")) + ")",
                           )
                     )})
                if s:
                    print "extract: surface_built #2: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          mpu
                     )})
                if s:
                    print "extract: surface_built #3: %s" % (s)
                
            if s is None:
                print "extract: surface_built: NOT FOUND"
                
            if s:
                extr['surface_built'] = s
        
        
        # extract surface_total
        if profile=="case-vile":
            s = None
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((
                            "curte de",
                            "curte",
                            "teren",
                            "sup(r)?(\.)?",
                            "suprafata",
                            "st(=|-|\s)?",
                            "t(=|-|\s)?",
                            "teren(=|-|\s)?",
                        ), 
                          [ "|".join(mpt)]
                     )})
                if s:
                    print "extract: surface_total #1: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          ( "("+ "|".join(mpt) + "[\s]+)?"+
                            "("+ "|".join(("total teren", "tot(\.)? teren", "de teren", "teren", "total(a)", "curte")) + ")",
                           )
                     )})
                if s:
                    print "extract: surface_total #2: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          mpt
                     )})
                if s:
                    print "extract: surface_total #3: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:raw': "(?P<match>[0-9\.]+)[\s]*("+"|".join(mpt)+")"
                })
                if s:
                    print "extract: surface_total #4: %s" % (s)
                    
            if s is None:
                print "extract: surface_total: NOT FOUND"
                
            if s:
                extr['surface_total'] = s
        elif profile=="apt":
            s = None
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          mpt
                     )})
                if s:
                    print "extract: surface_total #1: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:raw': "(?P<match>[0-9\.]+)[\s]*("+"|".join(mpt)+")"
                })
                if s:
                    print "extract: surface_total #2: %s" % (s)
                    
            if s is None:
                print "extract: surface_total: NOT FOUND"
                
            if s:
                extr['surface_total'] = s
        
        return extr
