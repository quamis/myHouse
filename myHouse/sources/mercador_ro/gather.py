# -*- coding: utf-8 -*-

import sources.base.gather as base

from lxml import etree
import re

class newGatherer(base.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)
        self.table_data = "mercador_ro_data"
        
        
    def extractPaginationUrls(self, html):
        ret=[]
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
    
    def _gatherLinks(self):
        return self._gatherLinks_simple()
    
    def _getAll(self, detailedPagesList):
        return self._getAll_simple(detailedPagesList, "utf-8")