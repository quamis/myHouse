import base.gather

from lxml import etree
import re
import time

import urllib2 # to be able to catch Browser expcetions

class newGatherer(base.gather.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)
        
        self.db.tableCreate("imobiliare_ro_links", { 
            "id":             "VARCHAR(256)",
            "url":            "VARCHAR(256)",
        }, ["id"])
        
        self.db.tableCreate("imobiliare_ro_data", { 
            "id":             "VARCHAR(64)",
            "category":       "VARCHAR(64)",
            "url":            "VARCHAR(256)",
            "contact":        "VARCHAR(256)",
            "location":       "VARCHAR(256)",
            "details":        "TEXT",
            "rooms":          "INT",
            "price":          "INT",
            "surface_total":  "INT",
            "surface_built":  "INT",
            "year_built":     "INT",
            "description":    "TEXT",
            "addDate":        "INT",
            "updateDate":     "INT",
        }, ["id"])
        
        
    def extractPaginationUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath("//a/@href")
        for a in hrefs:
            if(re.search("\/vanzare-(.+)\?pagina=[0-9]+$", a)):
                ret.append(a)

        return ret
    
    def extractOffersUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath("//div[contains(@class, 'oferta')]//a/@href")
        for a in hrefs:
            a = re.sub("\?lista=([0-9]+)$", "", a)
            if(re.search("\/vanzare-.+\/", a)):
                ret.append(a)

        return ret
    
    
    def _gatherLinks(self):
        completePagesList = [self.url]
        gotPagesList = []
        detailedPagesList = []
        gotNewPage=True
        
        cachePrefix = time.strftime("%Y%m%d%H")
        while gotNewPage:
            gotNewPage = False
            for link in completePagesList:
                if link not in gotPagesList: 
                    html = self.cache.get(cachePrefix+link)
                    if(html is None):
                        try:
                            html = self.wget(link)
                            self.cache.set(cachePrefix+link, html)
                            self.wait("new-page")
                        except urllib2.URLError:
                            self.debug_print("wget-failed")
                            continue
                    else:
                        self.debug_print("wget-cached", link)
                
                    if(html):
                        gotPagesList.append(link)
                        gotPagesList = self.removeDuplicates(gotPagesList)
                        
                        completePagesList = self.extractPaginationUrls(html)
                        completePagesList = self.removeDuplicates(completePagesList)
                        
                        # TODO: rename detailedPagesList2, detailedPagesList to something offer-like:)
                        detailedPagesList2 = self.extractOffersUrls(html)
                        detailedPagesList = self.removeDuplicates(detailedPagesList + detailedPagesList2)
                    
                    gotNewPage = True
                    #gotNewPage = False
                    
        return [completePagesList, detailedPagesList]

    
    def _getAll(self, detailedPagesList):
        # loop through all pages and gather individual links
        linkIndex = 0
        timestamp = time.time()
        #cachePrefix = time.strftime("%Y%m%d")
        cachePrefix = "page-"
        for link in detailedPagesList:
            linkIndex+=1
            html = self.cache.get(cachePrefix+link)
            if(html is None):
#                
                try:
                    html = self.wget(link)
                    self.cache.set(cachePrefix+link, html)
                    self.wait("new-offer")
                except urllib2.URLError:
                    self.debug_print("wget-failed")
                    continue
            else:
                self.debug_print("wget-cached", link)
                
                
            # extract data from the selected page
            strip_unicode = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)");
            html = strip_unicode.sub('', html)
            tree   = etree.HTML(html)
            
            location_full =     tree.xpath("//div[contains(@class, 'titlu')]//span/text()")[0].strip()
            location = re.search("^(?P<loc>[^,]+)", location_full).groups("loc")[0]
            
            price =             re.sub("[^0-9]", "", tree.xpath("//*[@id='b_detalii_titlu']/div/div/div/text()")[0].strip())
            #price_currency =    tree.xpath("//*[@id='b_detalii_titlu']/div/div/div/div/text()")[0].strip()
            
            surface_total =    re.sub("[^0-9]", "", self.xpath_getOne(tree, "//*[@id='b_detalii']/div/h3/span[contains(text(), 'teren')]/text()"))
            surface_built =    re.sub("[^0-9]", "", self.xpath_getOne(tree, "//*[@id='b_detalii']/div/h3/span[contains(text(), 'util')]/text()"))
            
            year_built =       re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//*[@id='b_detalii']/div/h3/span[contains(text(), 'An constr')]/text()"))
            x_rooms =          tree.xpath("//*[@id='b_detalii_caracteristici']//table//tr/td[1][contains(text(), 'camere')]/../td[2]/text()")
            rooms = 0
            if x_rooms:
                rooms = x_rooms[0]
            
            details =    location_full+". "+re.sub("[\s]+", " ", " ".join(tree.xpath(".//*[@id='b_detalii_text']/div/div/*/text()")))
            
            idstr = self.hash(link)
            self.writeItem({ 
                "id":             idstr,
                "category":       self.category,
                "url":            link,
                "location":       location,
                "details":        details,
                "price":          price,
                "rooms":          rooms,
                "surface_total":  surface_total,
                "surface_built":  surface_built,
                "year_built":     year_built,
                "addDate":        timestamp,
                "updateDate":     timestamp,
            })


    def writeItem(self, item):
        if(self.db.itemExists("imobiliare_ro_data", item['id'])):
            self.db.itemUpdate("imobiliare_ro_data",{ "id": item['id'], "updateDate":     item['updateDate'], })
        else:
            self.db.itemInsert("imobiliare_ro_data", item)
            self.db.flushRandom(0.025)
        