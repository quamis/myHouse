import base.gather

from lxml import etree
import re
import time

import urllib2 # to be able to catch Browser expcetions

class newGatherer(base.gather.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)
        
        self.db.tableCreate("mercador_ro_data", { 
            "id":             "VARCHAR(32)",
            "category":       "VARCHAR(64)",
            "url":            "VARCHAR(256)",
            "location":       "VARCHAR(256)",
            "rooms":          "INT",
            "price":          "INT",
            "surface_total":  "INT",
            "description":    "TEXT",
            "addDate":        "INT",
            "updateDate":     "INT",
        }, ["id"])
        
        self.table_data = "mercador_ro_data"
        
        
    def extractPaginationUrls(self, html):
        ret=[]
        parser = etree.HTMLParser()
        tree   = etree.HTML(html)
        hrefs = tree.xpath(".//*[@id='body-container']//span[contains(@class, 'item')]//a/@href")
        for a in hrefs:
            if(re.search("\/imobiliare\/.+", a)):
                ret.append(a)

        return ret
    
    def extractOffersUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath(".//*[@id='offers_table']//td[contains(@class, 'offer')]//h3//a[contains(@class, 'link')]/@href")
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
        
        cachePrefix = self.getCachePrefix("links")
        while gotNewPage:
            gotNewPage = False
            self.sortPagesList(completePagesList)
            
            for link in completePagesList:
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
                try:
                    tree   = etree.HTML(html)
                    
                    location =      self.xpath_getOne(tree, "..//p[contains(@class, 'addetails')]//strong[contains(@class, 'brrighte5')]/text()")
                    
                    p = self.xpath_getOne(tree, ".//div[contains(@class, 'pricelabel')]/strong[contains(@class, 'xxxx-large')]/text()")
                    if re.search("lei", p):
                        p = re.sub("[\s]", "", p)
                        m = re.search("^(?P<price>[0-9]+)", p)
                        p= int(m.group('price')) / self.conv_EURRON
                    else:
                        p = re.sub("[\s]", "", p)
                        m = re.search("^(?P<price>[0-9]+)", p)
                        p= int(m.group('price'))
                        
                    price =         p
                    surface_total = re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//table[contains(@class, 'details')]//div[contains(text(), 'Suprafata')]/strong/text()"))
                    rooms =         re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//table[contains(@class, 'details')]//div[contains(text(), 'Camere')]/strong/*/text()"))
    
                    #descRows =      tree.xpath(".//*[@id='main']/div[3]/div/div[2]/div[8]/text()")
                    description =   self.xpath_getTexts(tree, ".//div[contains(@class, 'offerdescription')]/p[contains(@class, 'large')]/text()")
                    
                    if re.search("^[\s]*$", description):
                        raise Exception("This description is empty. Ignoring")
                    
                    if re.search("apartament", description) and re.search("etaj", description):
                        raise Exception("This is not the correct category. Ignoring")
                    
                    if re.search("cumpar", description):
                        raise Exception("This is not the correct category. Ignoring")
    
                    self.writeItem({ 
                        "id":             idstr,
                        "category":       self.category,
                        "url":            link,
                        "location":       location,
                        "description":    description,
                        "price":          price,
                        "rooms":          rooms,
                        "surface_total":  surface_total,
                        "addDate":        timestamp,
                        "updateDate":     timestamp,
                    })
                except Exception:
                    self.debug_print("parse-failed")


