# -*- coding: utf-8 -*-

import logging
import re
import random, time
import mechanize
import cookielib
import hashlib
import numconv
import warnings
import datetime
import urllib2

class Extractor(object):
    def __init__(self, category, url, db, cache, args):
        self.category = category
        self.url = url
        self.db = db
        self.cache = cache
        self.args = args
        self.br = None
        
        self.table_data = None
        
        self.wget_stats = {
            'requests': 0,
            'failed': 0,
            'passed': 0,
            'time': 0,
        }
        
        self.lastCallTime = datetime.datetime.now()
        
    def init(self):
        self.db.tableCreate(self.table_data, { 
            "id":             "VARCHAR(32)",
            "category":       "VARCHAR(64)",
            "url":            "VARCHAR(256)",
            "html":           "TEXT",
            "addDate":        "INT",
            "updateDate":     "INT",
        }, ["id"])
        
        
    def destroy(self):
        if self.wget_stats['time']>0:
            print "requests: %d (%d failed), avg: %.3fs/rq" % (
               self.wget_stats['requests'],
               self.wget_stats['failed'],
               self.wget_stats['time']/float(self.wget_stats['requests'])
            )
        
    def getCachePrefix(self, usage):
        if usage=="links":
            return time.strftime("%Y%m%d%H")
        elif usage=="page":
            return "page-"
        else:
            return ""
    
    
    def _custom_sort_natcasesort(self, text):
        def xxatoi(text):
            return int(text) if text.isdigit() else text.lower()
        
        '''
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        @see http://stackoverflow.com/questions/14162838/python-equivalent-to-php-natcasesort
        @see http://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort
        '''    
        return [ xxatoi(c) for c in re.split('(\d+)', text) ]
    
    def removeDuplicates(self, pagesList):
        keys = {}
        for e in pagesList:
            keys[e] = 1
        pagesList = keys.keys()
        pagesList.sort()
        return pagesList
    
    def sortPagesList(self, pagesList):
        pagesList.sort( key=self._custom_sort_natcasesort )
        return pagesList
        
    def extractPaginationUrls(self, html):
        ret = []
        return ret
    
    def extractOffersUrls(self, html):
        ret = []
        return ret

    def gatherLinks(self):
        ret = self._gatherLinks()
        logging.debug("got %d links from %d pages", len(ret[1]), len(ret[0]))
        return ret
    
    def _gatherLinks(self):
        pass
    
    def linkAlreadyLoaded(self, link, gotPagesList):
        if link in gotPagesList:
            return True
        return False
    
    def removePageDuplicates(self, pagesList):
        return self.removeDuplicates(pagesList)
    
    def _gatherLinks_simple(self, urlPrefix=None):
        completePagesList = [self.url]
        gotPagesList = []
        detailedPagesList = []
        gotNewPage = True
        
        cachePrefix = self.getCachePrefix("links")
        while gotNewPage:
            gotNewPage=False
            
            for link in completePagesList:
                if urlPrefix:
                    if re.match("^http", link) is None:
                        link = urlPrefix+link
                
                if not self.linkAlreadyLoaded(link, gotPagesList): 
                    html = self.wget_cached(cachePrefix, link)
                
                    if(html):
                        gotPagesList.append(link)
                        gotPagesList = self.removeDuplicates(gotPagesList)
                        
                        completePagesList2 = self.extractPaginationUrls(html)
                        completePagesList = self.removePageDuplicates(completePagesList + completePagesList2)
                        completePagesList = self.sortPagesList(completePagesList)
                        
                        # TODO: rename detailedPagesList2, detailedPagesList to something offer-like:)
                        detailedPagesList2 = self.extractOffersUrls(html)
                        detailedPagesList = self.removeDuplicates(detailedPagesList + detailedPagesList2)
                        
                    gotNewPage = True
                    #gotNewPage = False
        
        self.cache.flushRandom(1)
        return [completePagesList, detailedPagesList]
    

    def getAll(self):
        t = self.gatherLinks()[1]
        self._getAll(t)
        self.cache.close()
        self.db.close()
    
    def _getAll(self):
        pass
    
    def _getAll_simple(self, detailedPagesList, encoding="utf-8", urlPrefix=None):
        # loop through all pages and gather individual links
        timestamp = time.time()
        cachePrefix = self.getCachePrefix("page")
        for link in detailedPagesList:
            if urlPrefix:
                if re.match("^http", link) is None:
                    link = urlPrefix+link
                
            html = self.wget_cached(cachePrefix, link)
                
            # extract data from the selected page
            idstr = self.hash(link)
            if html and self.updateIfExists(idstr, timestamp):
                self.writeItem({ 
                    "id":           idstr,
                    "category":     self.category,
                    "url":          link,
                    "html":         self.db.compress( unicode(html.decode(encoding)) ),
                    "addDate":      timestamp,
                    "updateDate":   timestamp,
                })

    
    def hash(self, text):
        ident = hashlib.md5()
        ident.update(text)
        digest = ident.hexdigest()
        number = int(digest, 16) % 0xffffffff
        return numconv.int2str(number, 64)



    def updateIfExists(self, idstr, updateDate):
        if(self.db.itemExists(self.table_data, idstr)):
            self.db.itemUpdate(self.table_data,{ "id": idstr,   "updateDate":     updateDate, })
            return False
        return True
    
    def writeItem(self, item):
        if(self.db.itemExists(self.table_data, item['id'])):
            self.db.itemUpdate(self.table_data,{ "id": item['id'], "updateDate":     item['updateDate'], })
        else:
            self.db.itemInsert(self.table_data, item)
            self.db.flushRandom(0.010)
        

    def wait(self, mode="default"): 
        # TODO: configure sleep period from the command-line/system specific args
        if mode=="default":
            try:
                now = datetime.datetime.now()
                remainingSleep = max(0, self.args.sleep - (now - self.lastCallTime).total_seconds())
                self.lastCallTime = now 
                time.sleep(remainingSleep)
            except AttributeError:
                time.sleep(random.random()*self.args.sleep)
        else:
            time.sleep(random.random()*self.args.sleep)
            
        
    def wget(self, url):
        logging.debug('wget %s'% (url))
        
        if self.br is None:
            logging.debug("initialize browser")
            br = mechanize.Browser()
            
            # Cookie Jar
            cj = cookielib.LWPCookieJar()
            br.set_cookiejar(cj)
            
            # Browser options
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
            
                br.set_handle_equiv(True)
                br.set_handle_gzip(True)
                br.set_handle_redirect(True)
                br.set_handle_referer(True)
                br.set_handle_robots(False)
                
                # Follows refresh 0 but not hangs on refresh > 0
                br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

            br.addheaders = [('User-agent', self.args.UA)]
            
            # Want debugging messages?
            #br.set_debug_http(True)
            #br.set_debug_redirects(True)
            #br.set_debug_responses(True)
            
            self.br = br
            logging.debug("got a brand new browser object")

        html = ""
        
        t1 = time.time()
        
        try:
            self.wget_stats['requests']+=1
            html = self.br.open(url).read()
            self.wget_stats['passed']+=1
        except Exception, ex:
            self.wget_stats['failed']+=1
            logging.debug('Browser.open.read() returned with exception: %s\n '% (ex))
            html = None
        
        t2 = time.time()
        self.wget_stats['time']+=t2-t1
        
        logging.debug('  done')
        return html
    
    def wget_cached(self, cachePrefix, url):
        html = self.cache.get(cachePrefix+url)
        if(html is None):
            try:
                html = self.wget(url)
                self.cache.set(cachePrefix+url, html)
                self.wait()
            except urllib2.URLError, ex:
                logging.debug('wget failed: %s'% (ex))
                html = None
        else:
            logging.debug('wget from cache %s ' % (url))
            
        return html
