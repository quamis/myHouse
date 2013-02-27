# -*- coding: utf-8 -*-

import sources.base.gather as base

from lxml import etree
import re

class newGatherer(base.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)
        self.table_data = "romino_ro_data"
        
        
    def extractPaginationUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath(".//div[contains(@class,  'pagination')]//span[contains(@class,  'pages')]//a/@href")
        for a in hrefs:
            ret.append(a)
        return ret
    
    def extractOffersUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath(".//div[@class= 'property']//div[@class= 'info']//a/@href")
        for a in hrefs:
            ret.append(a)
        return ret
    
        
    def _gatherLinks(self):
        return self._gatherLinks_simple()
    
    def _getAll(self, detailedPagesList):
        return self._getAll_simple(detailedPagesList, "utf-8")
    