import base.gather

from lxml import etree
import re
import time

import urllib2 # to be able to catch Browser expcetions

class newGatherer(base.gather.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)
        
        self.db.tableCreate("imopedia_ro_data", { 
            "id":             "VARCHAR(32)",
            "category":       "VARCHAR(64)",
            "url":            "VARCHAR(256)",
            "location":       "VARCHAR(256)",
            "price":          "INT",
            "surface_total":  "INT",
            "surface_built":  "INT",
            "year_built":     "INT",
            "rooms":          "INT",
            "description":    "TEXT",
            "addDate":        "INT",
            "updateDate":     "INT",
        }, ["id"])
        
        self.table_data = "imopedia_ro_data"
        
        
    def extractPaginationUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath(".//div[contains(@class, 'listing_paginare')]//div[contains(@class, 'paginare')]//a/@href")
        for a in hrefs:
            ret.append(a)

        return ret
    
    def extractOffersUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath(".//div[contains(@class, 'listing_item')]//div[contains(@class, 'title')]//a/@href")
        for a in hrefs:
            ret.append(a)

        return ret
    
    
    def linkAlreadyLoaded(self, link, gotPagesList):
        for e in gotPagesList:
            if e == link:
                return True
            
        return False
    
    def _gatherLinks(self):
        completePagesList = [self.url]
        gotPagesList = []
        detailedPagesList = []
        gotNewPage=True
        
        cachePrefix = self.getCachePrefix("page")
        while gotNewPage:
            gotNewPage = False
            self.sortPagesList(completePagesList)
            
            for link in completePagesList:
                if re.match("^http", link) is None:
                    link = "http://imopedia.ro"+link
                
                if not self.linkAlreadyLoaded(link, gotPagesList): 
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
        cachePrefix = self.getCachePrefix("page")
        for link in detailedPagesList:
            if re.match("^http", link) is None:
                link = "http://imopedia.ro"+link
                    
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
                
                
            idstr = self.hash(link)
            if html and self.updateIfExists(idstr, timestamp):
                # extract data from the selected page
                tree   = etree.HTML(html)
                try:
                    location =      self.xpath_getOne(tree, ".//div[contains(@class, 'det')]//strong[contains(text(), 'Zona')]/span/text()")
                    
                    price =         re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//div[contains(@class, 'pret_1')]/strong/text()"))
                    
                    surface_built = ""
                    if self.category=="case-vile":
                        surface_total =     re.sub("[^0-9.]", "", self.xpath_getOne(tree, ".//div[@id='informatii']//ul/li[contains(text(), 'total teren')]/text()"))
                        surface_built  =    re.sub("[^0-9.]", "", self.xpath_getOne(tree, ".//div[@id='informatii']//ul/li[contains(text(), 'teren liber')]/text()"))
                    else: # apt
                        surface_total = re.sub("[^0-9.]", "", self.xpath_getOne(tree, ".//div[@id='informatii']//ul/li//*[contains(text(), 'suprafata utila')]/../text()"))
                        if not surface_total:
                            surface_total = re.sub("[^0-9.]", "", self.xpath_getOne(tree, ".//div[@id='informatii']//ul/li//*[contains(text(), 'suprafata construita')]/../text()"))
                            
                            
                    year_built =    self.extractYear(self.xpath_getOne(tree, ".//div[@id='informatii']//ul/li[contains(text(), 'construit in')]/text()"))
    
                    description =   self.xpath_getTexts(tree, ".//div[contains(@class, 'alte_informatii')]//text()")
                    
                    t = re.search("(?P<rooms>[0-9]+) camere", self.xpath_getTexts(tree, ".//*[@id='info_oferta']//div[contains(@class, 'info_2')]/text()"))
                    rooms =         t.groups('rooms')[0] if t else None
    
                    # add info from the end info tables                    
                    lis = tree.xpath(".//*[@id='informatii']//div[contains(text(), 'utile')]/../ul/li")
                    description+= "\n"
                    s=""
                    for li in lis:
                        tx = self.xpath_getTexts(li, ".//text()")
                        tx = re.sub("-", "", tx)
                        tx = re.sub("[\s]+", " ", tx)
                        tx = tx.strip()
                        if tx:
                            description+= s + tx
                            s=". "
                    description = description.strip()
                                
                    if re.search("^[\s]*$", description):
                        raise Exception("This description is empty. Ignoring")
    
                    self.writeItem({ 
                        "id":               idstr,
                        "category":         self.category,
                        "url":              link,
                        "location":         location,
                        "description":      description,
                        "price":            price,
                        "surface_total":    surface_total,
                        "surface_built":    surface_built,
                        "year_built":       year_built,
                        "rooms":            rooms,
                        "addDate":          timestamp,
                        "updateDate":       timestamp,
                        })
                except Exception, e:
                    print e
                    self.debug_print("parse-failed")
