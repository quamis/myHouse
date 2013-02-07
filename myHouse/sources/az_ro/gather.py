# -*- coding: utf-8 -*-

import sources.base.gather as base

from lxml import etree
import re
import time

class newGatherer(base.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)

        self.db.tableCreate("az_ro_data", { 
            "id":             "VARCHAR(64)",
            "category":       "VARCHAR(64)",
            "url":            "VARCHAR(256)",
            "html":           "TEXT",
            "addDate":        "INT",
            "updateDate":     "INT",
        }, ["id"])
        
        self.table_data = "az_ro_data"
        
        
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
                    html = self.wget_cached(cachePrefix, link)
                
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
        return self._getAll_simple(detailedPagesList, "utf-8", "http://az.ro")
