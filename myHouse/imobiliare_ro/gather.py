# -*- coding: utf-8 -*-

import base.gather

from lxml import etree
import re
import time

import urllib2 # to be able to catch Browser expcetions

class newGatherer(base.gather.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)
        
        self.db.tableCreate("imobiliare_ro_data", { 
            "id":             "VARCHAR(32)",
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
        
        self.table_data = "imobiliare_ro_data"
        
        
    def extractPaginationUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath("//a/@href")
        for a in hrefs:
            if(re.search("\/vanzare-(.+)(\?|\&|\;)pagina=[0-9]+$", a)):
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
        
        cachePrefix = self.getCachePrefix("links")
        while gotNewPage:
            gotNewPage = False
            self.sortPagesList(completePagesList)
            
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
        cachePrefix = self.getCachePrefix("page")
        for link in detailedPagesList:
            linkIndex+=1
            html = self.cache.get(cachePrefix+link)
            if(html is None):
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
            idstr = self.hash(link)
            if html and self.updateIfExists(idstr, timestamp):
                tree   = etree.HTML(html)
                
                location_full =     tree.xpath("//div[contains(@class, 'titlu')]//span/text()")[0].strip()
                location = re.search("^(?P<loc>[^,]+)", location_full).groups("loc")[0]
                
                price =             re.sub("[^0-9]", "", tree.xpath("//*[@id='b_detalii_titlu']/div/div/div/text()")[0].strip())
                
                if self.category=="case-vile":
                    x_rooms =          tree.xpath("//*[@id='b_detalii_caracteristici']//table//tr/td[1][contains(text(), 'camere')]/../td[2]/text()")
                    rooms = x_rooms[0] if x_rooms else None 
                        
                    surface_total =     re.sub("[^0-9]", "", self.xpath_getOne(tree, "//*[@id='b_detalii']/div/h3/span[contains(text(), 'teren')]/text()"))
                    surface_built =     re.sub("[^0-9]", "", self.xpath_getOne(tree, "//*[@id='b_detalii']/div/h3/span[contains(text(), 'util')]/text()")) or \
                                        re.sub("[^0-9]", "", self.xpath_getOne(tree, "//*[@id='b_detalii']/div/h3/span[contains(text(), 'construit')]/text()")) 
                    year_built =        re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//*[@id='b_detalii']/div/h3/span[contains(text(), 'An constr')]/text()"))
                    
                    
                    details =    location_full+". "+re.sub("[\s]+", " ", " ".join(tree.xpath(".//*[@id='b_detalii_text']/div/div/*/text()")))
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
                else:
                    # apt
                    details =    re.sub("[\s]+", " ", " ".join(tree.xpath(".//*[@id='b_detalii_text']/div/div/*/text()")))
                    surface_built =    re.sub("[^0-9]", "", self.xpath_getOne(tree, "//*[@id='b_detalii']/div/h3/span[contains(text(), 'Suprafaa construit')]/text()"))
                    year_built =       re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//*[@id='b_detalii']/div/h3/span[contains(text(), 'An constr')]/text()"))
                    self.writeItem({ 
                        "id":             idstr,
                        "category":       self.category,
                        "url":            link,
                        "location":       location,
                        "details":        details,
                        "price":          price,
                        "surface_built":  surface_built,
                        "year_built":     year_built,
                        "addDate":        timestamp,
                        "updateDate":     timestamp,
                    })
            
