# -*- coding: utf-8 -*-

import time, sys, re, string
import sources.base.UnicodeCsvReader as UnicodeCsvReader

class Processor(object):
    def __init__(self, source, maindb, db, cache, args):
        self.args = args
        self.source = source
        self.db = db
        self.maindb = maindb
        self.cache = cache
        
        
        self.processor_helper = Processor_helper()
        
        self.currencyConverter = Processor_currencyConverter()

        #email, phones        
        self.maindb.tableCreate("data", { 
            "id":           "VARCHAR(64)",
			"internalStatus":"VARCHAR(128)",
            
            "userStatus":       "VARCHAR(128)",
            "suggestedStatus":   "VARCHAR(128)",
            
            "category":     "VARCHAR(64)",
            "source":       "VARCHAR(16)",  # anunturi_ro
            "url":          "VARCHAR(256)",
            "description":  "TEXT",
            "price":        "INT",

            "location":     "VARCHAR(256)",
            "rooms":        "INT",
            "year_built":   "INT",
            "surface_total":"FLOAT",
            "surface_built":"FLOAT",
            "price_per_mp_total":"FLOAT",
            "price_per_mp_built":"FLOAT",
            
            "floor":        "INT",
            "floor_max":    "INT",
            "apartmentType":"VARCHAR(64)",
            
            "addDate":      "INT",
            "updateDate":   "INT",
        }, ["id"], ["internalStatus", "category", "source", "price", "addDate", "updateDate"])
        
        self.maindb.tableCreate("data_contacts", { 
            "idOffer":      "VARCHAR(64)",
            "key":          "VARCHAR(16)",  # email, telephone, address
            "value":        "VARCHAR(256)",
        }, [], ["id", "key"])
        
        self.maindb.tableCreate("data_extracted", { 
            "idOffer":      "VARCHAR(64)",
            "key":          "VARCHAR(16)",
            "value":        "VARCHAR(256)",
        }, [], ["id", "key"])
        

    def selectStart(self):
        pass
    
    def selectEnd(self):
        pass
    
    def _processRow(self, row):
        pass

    def extractData_base(self, newRow):
        if newRow['price'] and "surface_built" in newRow and newRow["surface_built"]:
            newRow['price_per_mp_built'] = round(float(newRow['price'])/float(newRow['surface_built']), 0)
            
        if newRow['price'] and "surface_total" in newRow and newRow["surface_total"]:
            newRow['price_per_mp_total'] = round(float(newRow['price'])/float(newRow['surface_total']), 0)
            
        return newRow


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
            sys.stdout.write("\n    % 9sEUR %s" % (int(extra['price']) if extra['price'] else "-", extra['url']))
            
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
            #try:
            newRow = self._processRow(row)
            #except Exception as e:
            #    print "ex: %s" % (e)
                
            if newRow is None:
                continue
            
            if "extracted" not in newRow:
                newRow['extracted'] = {}
                                    
            newRow = self.processor_helper.convert_location(newRow)
            
            if(self.maindb.itemExists("data", newRow['id'])):
                if self.args.forceUpdate:
                    try:
                        self.maindb.execute("DELETE FROM `data_contacts` WHERE `idOffer`='%s'" %(newRow['id']))
                        self.maindb.execute("DELETE FROM `data_extracted` WHERE `idOffer`='%s'" %(newRow['id']))
                        
                        if 'contacts' in newRow:
                            for c in newRow['contacts']:
                                self.maindb.itemInsert("data_contacts", { "idOffer":newRow['id'], "key": c['key'], "value": c['value'] })
                                
                        if 'extracted' in newRow:
                            for k,v in newRow['extracted'].items():
                                self.maindb.itemInsert("data_extracted", { "idOffer":newRow['id'], "key": k, "value": v })
                                
                        self.maindb.itemUpdate("data", {
                              "source":             self.source, 
                              "id":                 newRow['id'],
                              "category":           newRow['category'], 
                              "url":                newRow['url'], 
                              "price":              newRow['price'],
                              "description":        newRow['description'],
                              
                              "location":           newRow['location'] if 'location' in newRow else None,
                              "rooms":              newRow['rooms'] if 'rooms' in newRow else None,
                              "year_built":         newRow['year_built'] if 'year_built' in newRow else None,
                              "surface_total":      newRow['surface_total'] if 'surface_total' in newRow else None,
                              "surface_built":      newRow['surface_built'] if 'surface_built' in newRow else None,
                              "price_per_mp_total": newRow['price_per_mp_total'] if 'price_per_mp_total' in newRow else None,
                              "price_per_mp_built": newRow['price_per_mp_built'] if 'price_per_mp_built' in newRow else None,
                              
                              "updateDate":         timestamp,
                          })
                    except Exception as e:
                        print "Exception(%s): %s" % (e.errno, e.strerror)
                else:
                    self.maindb.itemUpdate("data", { "id": newRow['id'], "updateDate": timestamp, })
                    
                self.debug_print("loop-old", newRow)
            else:
                try:
                    self.debug_print("loop-new", newRow)
                    
                    if 'contacts' in newRow:
                        for c in newRow['contacts']:
                            self.maindb.itemInsert("data_contacts", { "idOffer":newRow['id'], "key": c['key'], "value": c['value'] })
                            
                    if 'extracted' in newRow:
                        for k,v in newRow['extracted'].items():
                            self.maindb.itemInsert("data_extracted", { "idOffer":newRow['id'], "key": k, "value": v })
                            
                    self.maindb.itemInsert("data", {
                              "internalStatus":     "",
                              "userStatus":         "",
                              "suggestedStatus":    "",
                              "source":             self.source, 
                              "id":                 newRow['id'],
                              "category":           newRow['category'], 
                              "url":                newRow['url'], 
                              "price":              newRow['price'],
                              "description":        newRow['description'],
                              
                              "location":           newRow['location'] if 'location' in newRow else None,
                              "rooms":              newRow['rooms'] if 'rooms' in newRow else None,
                              "year_built":         newRow['year_built'] if 'year_built' in newRow else None,
                              "surface_total":      newRow['surface_total'] if 'surface_total' in newRow else None,
                              "surface_built":      newRow['surface_built'] if 'surface_built' in newRow else None,
                              "price_per_mp_total": newRow['price_per_mp_total'] if 'price_per_mp_total' in newRow else None,
                              "price_per_mp_built": newRow['price_per_mp_built'] if 'price_per_mp_built' in newRow else None,
                              
                              "updateDate":         timestamp,
                              "addDate":            timestamp,
                      })
                    self.db.flushRandom(0.025, False)
                except Exception as e:
                    print "Exception(%s): %s" % (e.errno, e.strerror)
                
        self.selectEnd(rows)
        self.maindb.close()



class Processor_currencyConverter(object):
    def __init__(self, ):
        self.rates = {
            'RON' : 1.000,
            'EUR' : 4.500, 
        }
        
    def RONEUR(self, price):
        return (float(price)*self.rates['RON']/self.rates['EUR'])




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
        
        
        self.locationsAssoc = {}
        for row in UnicodeCsvReader.UnicodeCsvReader(open("data/sources/process/locationsAssoc.csv")):
            self.locationsAssoc[row[0].strip().lower()] = row[2].strip()
            
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
            
        #if 'debug' in formulas:
        #    print "DEBUG, regex:  %s -> %s" % (rx, m.groups() if m else None)

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
                                match = unicode(s)
                        else:
                            match = float(s)
                    except ValueError, e:
                        print "Cannot convert '%s' to number: %s" % (s, e)
                
        return match
    
    def extract_location(self, newRow, text):
        s = None
        m = re.search("^(?P<location>([\w\-\.\(\)]+( |(?=,)))+)", text, re.UNICODE)
        if m:
            newRow['location']  = m.group('location')
            s = self.reformat(newRow['location'], self.presets['case-vile']['reformatter']['extractLocation'])
            if s:
                #print "extract: location #2: %s" % (s)
                newRow['location'] = s
            else:
                #print "extract: location #1: %s" % (s)
                pass
        
        #if s is None:
        #    print "extract: location: NOT FOUND"        
                
        return newRow
            
    def extract_rooms(self, extr, text):
        s = None    
        if s is None:
            s = self.extract_withFormula(text, {
                  'type':'int',
                  'match:raw': "(?P<match>[0-9]+)[\s]*("+"|".join([ "dormitoare", "dorm", "camere", "cam\.", "cam"])+")"
            })
            #if s:
            #    print "extract: rooms #1: %s" % (s)
                
        #if s is None:
        #    print "extract: rooms: NOT FOUND"
        
        if s:
            extr['rooms'] = s
            
        return extr
    
    def extract_floor(self, newRow, text, profile):
        #print "\n->%s" % (text)
        
        etj =   [ "etaje", "etajul", "etaj", "etj", "et", ]
        etj2 =   etj + [ ""]
        f =     ["\/", "din"]
        p =     [ "parter", "parter [a-z]+", "[^a-z0-9\+]p[^a-z0-9\+]"]
        
        s = None    
        if s is None:
            # etaj 1/8
            s = self.extract_withFormula(text, {
                  'type':'int',
                  'match:raw': "("+"|".join(etj2)+")[\s]*(?P<match>[0-9]+)[\s]*("+"|".join(f)+")[\s]*(?P<x>[0-9]+)[\s]*"
            })
            #if s:
            #    print "extract: floor #1: %s" % (s)
        
        if s is None:
            # etaj 1
            s = self.extract_withFormula(text, {
                  'type':'str',
                  'match:raw': "("+"|".join(etj)+")[\s]*(?P<match>[0-9]+)"
            })
            #if s:
            #    print "extract: floor #3: %s" % (s)
                
            if s:
                s=0
                
        if s is None:
            # etaj parter/10
            s = self.extract_withFormula(text, {
                  'type':'str',
                  'match:raw': "("+"|".join(etj2)+")[\s]*(?P<match>("+"|".join(p)+"))[\s]*("+"|".join(f)+")[\s]*(?P<x>[0-9]+)[\s]*"
            })
            #if s:
            #    print "extract: floor #4: %s" % (s)
                
            if s:
                s=0
                
        if s is None:
            # parter
            s = self.extract_withFormula(text, {
                  'type':'str',
                  'match:raw': "[^a-z0-9\+](?P<match>("+"|".join(p)+"))"
            })
            #if s:
            #    print "extract: floor #5: %s" % (s)
                
            if s:
                s=0
                
#        if s is None:
#            print "extract: floor: NOT FOUND"
        
        if s and s>0 and s<20:
            newRow['floor'] = s
        
        
        
        s = None    
        if s is None:
            # etaj 1/8
            s = self.extract_withFormula(text, {
                  'type':'int',
                  'match:raw': "("+"|".join(etj2)+")[\s]*(?P<x>[0-9]+)[\s]*("+"|".join(f)+")[\s]*(?P<match>[0-9]+)[\s]*"
            })
#            if s:
#                print "extract: floor_max #1: %s" % (s)
        
        if s is None:
            # etaj parter/10
            s = self.extract_withFormula(text, {
                  'type':'int',
                  'match:raw': "("+"|".join(etj)+")[\s]*(?P<x>("+"|".join(p)+"))[\s]*("+"|".join(f)+")[\s]*(?P<match>[0-9]+)[\s]*"
            })
#            if s:
#                print "extract: floor_max #2: %s" % (s)
        
        if s is None:
            #  parter/10
            s = self.extract_withFormula(text, {
                  'type':'int',
                  'match:raw': "[^a-z0-9](?P<x>("+"|".join(p)+"))[\s]*("+"|".join(f)+")[\s]*(?P<match>[0-9]+)[\s]*"
            })
#            if s:
#                print "extract: floor_max #3: %s" % (s)
                        
        if s is None:
            # 10 etaje
            s = self.extract_withFormula(text, {
                  'type':'int',
                  'match:raw': "(?P<match>[0-9]+)[\s]*("+"|".join(etj)+")"
            })
#            if s:
#                print "extract: floor_max #4: %s" % (s)
                
#        if s is None:
#            print "extract: floor_max: NOT FOUND"
        
        if s:
            newRow['floor_max'] = s
        
        return newRow
    
    
    def extract_apartmentType(self, newRow, text, profile):
#        print "\n->%s" % (text)
        s = None    
        if s is None:
            s = self.extract_withFormula(text, {
                  'type':'str',
                  'match:raw': "[^a-z0-9](?P<match>"+"|".join(["semidecomandat"])+")[^a-z0-9]"
            })
#            if s:
#                print "extract: apartmentType #1: %s" % (s)

            if s:
                s = "semidec"
        
        
        if s is None:
            s = self.extract_withFormula(text, {
                  'type':'str',
                  'match:raw': "[^a-z0-9](?P<match>"+"|".join(["nedecomandat"])+")[^a-z0-9]"
            })
#            if s:
#                print "extract: apartmentType #2: %s" % (s)
        
            if s:
                s = "nondec"
                
        if s is None:
            s = self.extract_withFormula(text, {
                  'type':'str',
                  'match:raw': "[^a-z0-9](?P<match>"+"|".join(["decomandat", "dec"])+")[^a-z0-9]"
            })
#            if s:
#                print "extract: apartmentType #3: %s" % (s)
        
            if s:
                s = "dec"
                
#        if s is None:
#            print "extract: apartmentType: NOT FOUND"
        
        if s:
            newRow['apartmentType'] = s
        
        return newRow
    
    
    def convert_location(self, newRow):
        if 'location' in newRow: 
            newRow['location'] = newRow['location'].strip()
            loc = newRow['location']
            
            if loc in self.locationsAssoc and self.locationsAssoc[loc.lower()]:
                loc = self.locationsAssoc[loc.lower()]
                newRow['extracted']['location_raw'] = newRow['location']
                newRow['location'] = loc
                #print "convert: location #1: '%s' => '%s'" % (newRow['extracted']['location_raw'], newRow['location'])
            else:
                newRow['location'] = loc  # at least we stripped the location of spaces:)
                #print "convert: location: NOT FOUND('%s')" % (loc)
                
        return newRow
    
    def extract_year(self, extr, text):
        s = None    
        # remove the location from the text, basically we might get distracted by area like "1 decembrie 1918"
        if 'location' in extr: 
            text = string.replace(text, extr['location'], "")
            
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
            #if s:
            #    print "extract: year_built #1: %s" % (s)
        
        if s is None:
            s = self.extract_withFormula(text, {
                  'type':'int',
                  'match':'(18|19|20)[0-9]{2}',
                  'match:content':((), ()),
            })
            #if s:
            #    print "extract: year_built #2: %s" % (s)
                
        #if s is None:
        #    print "extract: year_built: NOT FOUND"
        
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
                #if s:
                #    print "extract: surface_built #1: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match': '[0-9]{,4}',
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
                #if s:
                #    print "extract: surface_built #2: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          ( "("+ "|".join(mpu) + ")[\s]+"+
                            "("+ "|".join(("amprenta", "utili", "construiti", "constr(\.)?")) + ")",
                           )
                     )})
                #if s:
                #    print "extract: surface_built #3: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          mpu
                     )})
                #if s:
                #    print "extract: surface_built #4: %s" % (s)
                
            #if s is None:
            #    print "extract: surface_built: NOT FOUND"
                
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
                #if s:
                #    print "extract: surface_built #1: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          ( "("+ "|".join(mpu) + ")[\s]+"+
                            "("+ "|".join(("utili", "construiti", "constr(\.)?")) + ")",
                           )
                     )})
                #if s:
                #    print "extract: surface_built #2: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          mpu
                     )})
                #if s:
                #    print "extract: surface_built #3: %s" % (s)
                
            #if s is None:
            #    print "extract: surface_built: NOT FOUND"
                
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
                #if s:
                #    print "extract: surface_total #1: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          ( "("+ "|".join(mpt) + "[\s]+)?"+
                            "("+ "|".join(("total teren", "tot(\.)? teren", "de teren", "teren", "total(a)", "curte")) + ")",
                           )
                     )})
                #if s:
                #    print "extract: surface_total #2: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          mpt
                     )})
                #if s:
                #    print "extract: surface_total #3: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:raw': "(?P<match>[0-9\.]+)[\s]*("+"|".join(mpt)+")"
                })
                #if s:
                #    print "extract: surface_total #4: %s" % (s)
                    
            #if s is None:
            #    print "extract: surface_total: NOT FOUND"
                
            if s:
                extr['surface_total'] = s
        elif profile=="apt":
            s = None
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:content':((), 
                          mpt
                     )})
                #if s:
                #    print "extract: surface_total #1: %s" % (s)
            if s is None:
                s = self.extract_withFormula(text, {
                      'match:raw': "(?P<match>[0-9\.]+)[\s]*("+"|".join(mpt)+")"
                })
                #if s:
                #    print "extract: surface_total #2: %s" % (s)
                    
            #if s is None:
            #    print "extract: surface_total: NOT FOUND"
                
            if s:
                extr['surface_total'] = s
        
        return extr
