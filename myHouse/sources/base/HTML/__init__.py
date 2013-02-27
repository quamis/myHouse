# -*- coding: utf-8 -*-

from lxml import etree
import re

class HTML(object):
    def __init__(self, html, tree=None):
        self.html = html
        self.tree = etree.HTML(self.html) if tree is None else tree
    
    def extend(self, etree):
        return HTML("", etree)
    
    def xpath(self, query):
        return self.tree.xpath(query)

    def conditional(self, prefix, reference):
        if reference:
            return prefix+reference
        return None

    def first(self, xpath):
        ret = self.tree.xpath(xpath)
        if ret:
            return self.sanitize(ret[0].strip())
        return ""
    
    def concat(self, xpath, getSanitized=True):
        elms = self.tree.xpath(xpath)
        ret = ""
        for r in elms:
            ret+= r + "\n"
            
        if ret:
            if getSanitized: 
                return self.sanitize(ret.strip())
            else:
                return ret.strip()
            
        return ""
    
    def sanitize(self, text):
        return re.sub("[\s]+", " ", text)
    
    def asFloat(self, xpath):
        price = self.first(xpath)
        
        if price:
            price =     re.sub("[^0-9]", "", price)
            
        if price:
            return float(price)
        
        return None
    
    def asInt(self, xpath):
        price = self.first(xpath)
        
        if price:
            price =     re.sub("[^0-9]", "", price)
            
        if price:
            return int(price)
        
        return None
    
    def asYear(self, xpath):
        y = self.first(xpath)
        
        if y:
            y =     re.sub("[^0-9]", "", y)
            
        if re.match("^[0-9]{4}$", y):
            return int(y)
        return None
        
        return None
        
    def asPrice(self, xpath):
        return self.asFloat(xpath)
    