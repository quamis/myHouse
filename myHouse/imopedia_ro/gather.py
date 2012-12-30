import base.gather

from lxml import etree
import re
import time

import urllib2 # to be able to catch Browser expcetions

class newGatherer(base.gather.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)
        
        self.db.tableCreate("imopedia_ro_links", { 
            "id":             "VARCHAR(256)",
            "url":            "VARCHAR(256)",
        }, ["id"])
        
        self.db.tableCreate("imopedia_ro_data", { 
            "id":             "VARCHAR(64)",
            "category":       "VARCHAR(64)",
            "url":            "VARCHAR(256)",
            "location":       "VARCHAR(256)",
            "price":          "INT",
            "surface_total":  "INT",
            "description":    "TEXT",
            "addDate":        "INT",
            "updateDate":     "INT",
        }, ["id"])
        
        
    def extractPaginationUrls(self, html):
        ret=[]
        parser = etree.HTMLParser()
        tree   = etree.HTML(html)
        hrefs = tree.xpath(".//div[contains(@class, 'listing_paginare')]//div[contains(@class, 'paginare')]//a/@href")
        for a in hrefs:
            ret.append(a)

        return ret
    
    def extractOffersUrls(self, html):
        ret=[]
        parser = etree.HTMLParser()
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
        
        cachePrefix = time.strftime("%Y%m%d%H")
        while gotNewPage:
            gotNewPage = False
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
        #cachePrefix = time.strftime("%Y%m%d")
        cachePrefix = "page-"
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
                
                
            if(html): # TODO: in wget do a throw-exception, thats why we have the above try-catch!!
                # extract data from the selected page
                try:
                    tree   = etree.HTML(html)
                    
                    location =      self.xpath_getOne(tree, ".//div[contains(@class, 'det')]//strong[contains(text(), 'Zona')]/span/text()")
                    
                    price =         re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//div[contains(@class, 'pret_1')]/strong/text()"))
                    surface_total = re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//div[@id='informatii']//ul/li[contains(text(), 'total teren')]/text()"))
    
                    description =   self.xpath_getTexts(tree, ".//div[contains(@class, 'alte_informatii')]//text()")
                    
                    if re.search("^[\s]*$", description):
                        raise Exception("This description is empty. Ignoring")
    
                    idstr = self.hash(link)
                    self.writeItem({ 
                        "id":             idstr,
                        "category":       self.category,
                        "url":            link,
                        "location":       location,
                        "description":    description,
                        "price":          price,
                        "surface_total":  surface_total,
                        "addDate":        timestamp,
                        "updateDate":     timestamp,
                    })
                except Exception:
                    self.debug_print("parse-failed")


    def writeItem(self, item):
        if(self.db.itemExists("imopedia_ro_data", item['id'])):
            self.db.itemUpdate("imopedia_ro_data",{ "id": item['id'], "updateDate":     item['updateDate'], })
        else:
            self.db.itemInsert("imopedia_ro_data", item)
            self.db.flushRandom(0.025)
        