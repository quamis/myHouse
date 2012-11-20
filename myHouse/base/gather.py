import logging
import md5
import sys
import random, time
from mechanize import Browser
import urllib2

class Extractor(object):
    def __init__(self, category, url, db, cache, args):
        self.category = category
        self.url = url
        self.db = db
        self.cache = cache
        self.args = args
        
    def xpath_getOne(self, tree, xpath, ):
        ret = tree.xpath(".//*[@id='b_detalii']/div/h3/span[contains(text(), 'An constr')]/text()")
        if ret: 
            return ret[0].strip()
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

    def getAll(self):
        pass
    
    def wait(self, reason):
        # TODO: configure sleep period from the command-line/system specific args
        if reason=="new-page":
            time.sleep(random.random()*self.args.sleepp)
        elif reason=="new-offer":
            time.sleep(random.random()*self.args.sleepo)
        else:
            time.sleep(random.random()*self.args.sleepp)
            
        
    def wget(self, url):
        self.debug_print("wget-start", url)
        br = Browser()
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', self.args.UA)]
        html = br.open(url).read()
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
            sys.stdout.write(">")
        elif(result=="wget-done"):
            sys.stdout.write("<")
        elif(result=="wget-fail"):
            sys.stdout.write("!")
        elif(result=="wget-cached"):
            sys.stdout.write(".")
        elif(result=="parse-failed"):
            sys.stdout.write("X")
        elif(result=="got-links"):
            sys.stdout.write("\n\n")
            
        sys.stdout.flush()
        
    def debug_print_1(self, result, extra=None):
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
        
    def debug_print_0(self, result, extra=None):
        pass
