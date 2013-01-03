import base.gather

from lxml import etree
import re
import time

import urllib2 # to be able to catch Browser expcetions

class newGatherer(base.gather.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)
        
        self.db.tableCreate("az_ro_links", { 
            "id":             "VARCHAR(256)",
            "url":             "VARCHAR(256)",
        }, ["id"])
        
        self.db.tableCreate("az_ro_data", { 
            "id":             "VARCHAR(64)",
            "category":       "VARCHAR(64)",
            "url":            "VARCHAR(256)",
            "contact":        "VARCHAR(256)",
            "price":          "INT",
            "description":    "TEXT",
            "addDate":        "INT",
            "updateDate":     "INT",
        }, ["id"])
        
        
    def extractPaginationUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath("//a/@href")
        for a in hrefs:
            if(re.search("\/imobiliare-vanzari\/(case-vile|[1-9]-camere)\?page=[0-9]+", a)):
                ret.append(a)
        return ret
    
    def extractOffersUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath("//a/@href")
        for a in hrefs:
            if(re.search("\/imobiliare-vanzari\/(case-vile|[1-9]-camere)\/[^?]+", a)):
                ret.append(a)

        return ret
    
    def _gatherLinks(self):
        completePagesList = [self.url]
        gotPagesList = []
        detailedPagesList = []
        gotNewPage = True
        
        cachePrefix = self.getCachePrefix("links")
        while gotNewPage:
            gotNewPage=False
            for link in completePagesList:
                if re.match("^http", link) is None:
                    link = "http://az.ro"+link
                
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
                        
                        completePagesList2 = self.extractPaginationUrls(html)
                        completePagesList = self.removeDuplicates(completePagesList + completePagesList2)
                        
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
            linkIndex+=1
            # TODO: this is a "pattern", used by imopedia also
            if re.match("^http", link) is None:
                link = "http://az.ro"+link
            
            html = self.cache.get(cachePrefix+link)
            if(html is None):
                try:
                    html = self.wget(link)
                    self.cache.set(cachePrefix+link, html)
                    self.wait("new-offer")
                except urllib2.URLError, e:
                    self.debug_print("wget-failed")
                    continue
            else:
                self.debug_print("wget-cached", link)
                
            # extract data from the selected page
            if(html):
                tree   = etree.HTML(html)
                try:
                    locations =     re.sub(" (-|\/) Ilfov", "", re.sub("Localitate", "", self.xpath_getTexts(tree, ".//*[@id='specs']/li/strong[contains(text(), 'Localitate')]/../*/text()"))).strip()
                    m = re.match("(?P<loc1>[^\n]+)\n(?P<loc2>[^\n]+)", locations)
                    location = ""
                    if m:
                        location =  m.group("loc2") + " - " + m.group("loc1")
                        
                    text =          re.sub("[\s]+", " ", location + ", " + self.xpath_getTexts(tree, ".//div[contains(@class, 'az-content-body')]//text()"))
                    contact =       self.xpath_getOne(tree, ".//div[contains(@class, 'az-content-contact')]/span[contains(@class, 'act-phone')]/a/text()")
                    pret =          re.sub("[^0-9]", "", re.sub("Pret:", "", self.xpath_getOne(tree, ".//div[contains(@class, 'az-price')]/text()")))
                    
                    idstr = self.hash(link)
                    self.writeItem({ 
                        "id":               idstr,
                        "price":            pret,
                        "category":         self.category,
                        "url":              link,
                        "description":      text,
                        "contact":          contact,
                        "addDate":          timestamp,
                        "updateDate":       timestamp,
                    })
                except IndexError as e:
                    self.debug_print("parse-failed", e)

    def writeItem(self, item):
        if(self.db.itemExists("az_ro_data", item['id'])):
            self.db.itemUpdate("az_ro_data",{ "id": item['id'], "updateDate":     item['updateDate'], })
        else:
            self.db.itemInsert("az_ro_data", item)
            self.db.flushRandom(0.025)
        