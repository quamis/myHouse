import logging
import sys
import random, time
import mechanize
import cookielib
import hashlib
import numconv
import warnings
import datetime

class Extractor(object):
    def __init__(self, category, url, db, cache, args):
        self.category = category
        self.url = url
        self.db = db
        self.cache = cache
        self.args = args
        self.br = None
        self.conv_EURRON = 4.55
        
        self.lastCallTime = datetime.datetime.now()
        
    def xpath_getOne(self, tree, xpath):
        ret = tree.xpath(xpath)
        if ret: 
            return ret[0].strip()
        return ""
    
    def xpath_getTexts(self, tree, xpath):
        elms = tree.xpath(xpath)
        ret = ""
        for r in elms:
            ret+= r + "\n"
            
        if ret: 
            return ret.strip()
        return ""
    
    def getCachePrefix(self, usage):
        if usage=="links":
            return time.strftime("%Y%m%d%H")
        elif usage=="page":
            return "page-"
        else:
            return ""
    
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
        ret = []
        return ret
    
    def extractOffersUrls(self, html):
        ret = []
        return ret

    def gatherLinks(self):
        ret = self._gatherLinks()
        self.debug_print("got-links", [len(ret[1]), len(ret[0])])
        return ret
    
    def _gatherLinks(self):
        pass

    def getAll(self):
        self._getAll(self.gatherLinks()[1])
        self.cache.close()
        self.db.close()
    
    def _getAll(self):
        pass
    
    def hash(self, text):
        ident = hashlib.md5()
        ident.update(text)
        digest = ident.hexdigest()
        number = int(digest, 16) % 0xffffffff
        return numconv.int2str(number, 64)
            
    
    def wait(self, reason): 
        # TODO: configure sleep period from the command-line/system specific args
        if reason=="new-page" or reason=="new-offer":
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
        self.debug_print("wget-start", url)
        if self.br is None:
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

        html = ""
        try:
            html = self.br.open(url).read()
        except Exception, ex:
            sys.stdout.write("\n Browser.open.read() returned with exception: %s\n" % (ex))
            return None
            
        self.debug_print("wget-done")
        return html
    
    def debug_print(self, result, extra=None):
        # 0 = none, 1: only importans, 2: dots, 3: debug
        if(self.args.verbosity>=3):
            self.debug_print_3(result, extra)
        elif(self.args.verbosity>=2):
            self.debug_print_2(result, extra)
        elif(self.args.verbosity>=1):
            self.debug_print_1(result, extra)
        elif(self.args.verbosity>=0):
            self.debug_print_0(result, extra)
            
    
    def debug_print_3(self, result, extra=None):
        if(result=="wget-start"):
            logging.debug('wget %s', extra)
        elif(result=="wget-done"):
            logging.debug('  wget done')
        elif(result=="wget-fail"):
            logging.debug('  wget failed, skipping')
        elif(result=="wget-cached"):
            logging.debug("wget from cache %s", extra)
        elif(result=="parse-failed"):
            logging.debug("cannot extract data")
        elif(result=="got-links"):
            logging.debug("got %d links from %d pages", extra[0], extra[1]);
            
    def debug_print_2(self, result, extra=None):
        if(result=="wget-start"):
            sys.stdout.write("\n %s" % (extra))
        elif(result=="wget-done"):
            pass
        elif(result=="wget-fail"):
            sys.stdout.write(" (fail)")
        elif(result=="wget-cached"):
            sys.stdout.write("\n %s" % (extra))
        elif(result=="parse-failed"):
            sys.stdout.write(" (parse fail)")
        elif(result=="got-links"):
            pass
            
        sys.stdout.flush()
        
    def debug_print_1(self, result, extra=None):
        if(result=="wget-start"):
            sys.stdout.write(">")
        elif(result=="wget-done"):
            sys.stdout.write("<")
        elif(result=="wget-fail"):
            sys.stdout.write("!")
        elif(result=="wget-cached"):
            sys.stdout.write("-")
        elif(result=="parse-failed"):
            sys.stdout.write("*")
        elif(result=="got-links"):
            sys.stdout.write("\n\n")
            
        sys.stdout.flush()
        
    def debug_print_0(self, result, extra=None):
        pass
