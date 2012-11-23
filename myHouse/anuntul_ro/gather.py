import base.gather

from lxml import etree
import re
import time

import urllib2 # to be able to catch Browser expcetions

class newGatherer(base.gather.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)
        
        self.db.tableCreate("anuntul_ro_links", { 
            "id":             "VARCHAR(256)",
            "url":             "VARCHAR(256)",
        }, ["id"])
        
        self.db.tableCreate("anuntul_ro_data", { 
            "id":             "VARCHAR(64)",
            "category":     "VARCHAR(64)",
            "url":             "VARCHAR(256)",
            "contact":         "VARCHAR(256)",
            "price":         "INT",
            "description":     "TEXT",
            "addDate":         "INT",
            "updateDate":     "INT",
        }, ["id"])
        
        
    def extractPaginationUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath("//a/@href")
        for a in hrefs:
            if(re.search("\/anunturi-imobiliare-vanzari\/(.+)\/pag-[0-9]+\/", a)):
                ret.append(a)
        return ret
    
    def extractOffersUrls(self, html):
        ret=[]
        tree   = etree.HTML(html)
        hrefs = tree.xpath("//a/@href")
        for a in hrefs:
            if(re.search("\/anunturi-imobiliare-vanzari\/(.+)\/(.+)\.html", a)):
                ret.append(a)

        return ret
    
    def _gatherLinks(self):
        completePagesList = [self.url]
        gotPagesList = []
        detailedPagesList = []
        gotNewPage = True
        
        cachePrefix = time.strftime("%Y%m%d%H")
        while gotNewPage:
            gotNewPage=False
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
                except urllib2.URLError, e:
                    self.debug_print("wget-failed")
                    continue
            else:
                self.debug_print("wget-cached", link)
                
            # extract data from the selected page
            strip_unicode = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)");
            html = strip_unicode.sub('', html)
            tree   = etree.HTML(html)
            try:
                text =         tree.xpath("//table[@id='detalii_anunt']//div[@class='detalii_txt']/text()")[0]
                location =     tree.xpath("//table[@id='detalii_anunt']//div[@class='detalii_txt']/strong/text()")[0]
                #addDate =      tree.xpath("//table[@id='detalii_anunt']//div[@class='detalii_txt']/span[@class='data']/text()")[0]
                contact =      tree.xpath("//table[@id='detalii_anunt']//div[@class='contact']/text()")[0]
                pret =         tree.xpath("//table[@id='detalii_anunt']//span[@class='pret']/text()")[0]
                if pret:
                    pret = pret.replace("Pret:", "").replace(".", "")
                    pret =         re.sub("[^0-9]", "", pret)
                
                idstr = self.hash(link)
                self.writeItem({ 
                    "id":             idstr,
                    "price":         pret,
                    "category":     self.category,
                    "url":             link,
                    "description":     location+" "+text,
                    "contact":         contact,
                    "addDate":         timestamp,
                    "updateDate":     timestamp,
                })
            except IndexError as e:
                self.debug_print("parse-failed", e)

    def writeItem(self, item):
        if(self.db.itemExists("anuntul_ro_data", item['id'])):
            self.db.itemUpdate("anuntul_ro_data",{ "id": item['id'], "updateDate":     item['updateDate'], })
        else:
            self.db.itemInsert("anuntul_ro_data", item)
            self.db.flushRandom(0.025)
        