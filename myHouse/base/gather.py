import logging
import md5
import random, time
from mechanize import Browser
import urllib2

class Extractor(object):
    def __init__(self, category, url, db, cache):
        self.category = category
        self.url = url
        self.db = db
        self.cache = cache


    def removeDuplicates(self, pagesList):
        keys = {}
        for e in pagesList:
            keys[e] = 1
        pagesList = keys.keys()
        pagesList.sort()
        return pagesList
    
    def printPagesList(self, pagesList):
        for link in pagesList:
            print link


    def extractPaginationUrls(self, html):
        ret=[]
        return ret
    
    def extractOffersUrls(self, html):
        ret=[]
        return ret

    def getAll(self):
        pass
    
    def wait(self, reason):
        # TODO: configure sleep period from the command-line/system specific args
        #time.sleep(random.random()*5)
        pass
        
    def wget(self, url):
        logging.debug("wget %s", url)
        br = Browser()
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        html = br.open(url).read()
        logging.debug('  wget done')
        return html
            
        
