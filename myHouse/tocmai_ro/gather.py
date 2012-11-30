import base.gather

from lxml import etree
import re
import time

import urllib2 # to be able to catch Browser expcetions

class newGatherer(base.gather.Extractor ):
    def __init__(self, category, url, db, cache, args):
        super(newGatherer, self).__init__(category, url, db, cache, args)
        
        self.db.tableCreate("tocmai_ro_links", { 
            "id":             "VARCHAR(256)",
            "url":            "VARCHAR(256)",
        }, ["id"])
        
        self.db.tableCreate("tocmai_ro_data", { 
            "id":             "VARCHAR(64)",
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
        
        
    def extractPaginationUrls(self, html):
        ret=[]
        parser = etree.HTMLParser()
        tree   = etree.HTML(html)
        hrefs = tree.xpath("//a/@href")
        for a in hrefs:
            if(re.search("\/cauta(.*)(\?|&)page=[0-9]+", a)):
                ret.append(a)

        return ret
    
    def extractOffersUrls(self, html):
        ret=[]
        parser = etree.HTMLParser()
        tree   = etree.HTML(html)
        hrefs = tree.xpath("//div[contains(@class, 'item-row')]//div[contains(@class, 'items-title')]//a/@href")
        for a in hrefs:
            ret.append(a)

        return ret
    
    
    def removePageDuplicates(self, pagesList):
        keys = {}
        for e in pagesList:
            try:
                page = re.search("page=(?P<page>[0-9]+)", e).groups("page")
                keys[page] = e
            except Exception:
                pass
        pagesList = keys.values()
        pagesList.sort()
        return pagesList
    
    def linkAlreadyLoaded(self, link, gotPagesList):
        page = re.search("page=(?P<page>[0-9]+)", link).groups("page")
        for e in gotPagesList:
            pg = re.search("page=(?P<page>[0-9]+)", e).groups("page")
            if page == pg:
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
                if not self.linkAlreadyLoaded(link, gotPagesList): 
                    html = self.cache.get(cachePrefix+link)
                    if(html is None):
                        try:
                            html = self.wget(link)
                            self.cache.set(cachePrefix+link, html)
                            self.wait("new-page")
                        except urllib2.URLError, e:
                            self.debug_print("wget-failed")
                            continue
                    else:
                        self.debug_print("wget-cached", link)
                
                    if(html):
                        gotPagesList.append(link)
                        gotPagesList = self.removePageDuplicates(gotPagesList)
                        
                        completePagesList = self.extractPaginationUrls(html)
                        completePagesList = self.removePageDuplicates(completePagesList)
                        
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
                
                
            if(html): # TODO: in wget do a throw-exception, thats why we have the above try-catch!!
                # extract data from the selected page
                try:
                    strip_unicode = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)");
                    html = strip_unicode.sub('', html)
                    tree   = etree.HTML(html)
                    
                    location1 =     tree.xpath(".//*[@id='main']//div/p/b[contains(text(), 'Localitate')]/../text()")[0].strip()
                    location2 =     tree.xpath(".//*[@id='main']//div/p/b[contains(text(), 'Zona')]/../text()")[0].strip()
                    location =      "%s, %s" % (location1, location2)
                    
                    price =         re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//*[@id='main']//div[contains(text(), 'Pret')]/text()"))
                    surface_total = re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//*[@id='main']//div/p/b[contains(text(), 'Suprafata')]/../text()"))
                    rooms =         re.sub("[^0-9]", "", self.xpath_getOne(tree, ".//*[@id='main']//div/p/b[contains(text(), 'camere')]/../text()"))
    
                    #descRows =      tree.xpath(".//*[@id='main']/div[3]/div/div[2]/div[8]/text()")
                    descRows =      tree.xpath(".//*[@id='main']//div[contains(@class, 'item-description')]/text()")
                    description = ""
                    for r in descRows:
                        description+= r.strip()+"\n"
                    description = description.strip()
                    
                    if re.search("apartament", description) and re.search("etaj", description):
                        raise Exception("This is not the correct category. Ignoring")
                    
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
                        "rooms":          rooms,
                        "surface_total":  surface_total,
                        "addDate":        timestamp,
                        "updateDate":     timestamp,
                    })
                except Exception:
                    self.debug_print("parse-failed")


    def writeItem(self, item):
        if(self.db.itemExists("tocmai_ro_data", item['id'])):
            self.db.itemUpdate("tocmai_ro_data",{ "id": item['id'], "updateDate":     item['updateDate'], })
        else:
            self.db.itemInsert("tocmai_ro_data", item)
            self.db.flushRandom(0.025)
        