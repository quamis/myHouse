# -*- coding: utf-8 -*-

import re, string
import sources.base.UnicodeCsvReader as UnicodeCsvReader

class Helper(object):
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
