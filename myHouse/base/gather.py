import logging
import md5
import random

class Extractor(object):
    def __init__(self, category, url, db, cache):
        self.category = category
        self.url = url
        self.db = db
        self.cache = cache

    def cleanupList(self, pagesList):
        keys = {}
        for e in pagesList:
            keys[e] = 1
        pagesList = keys.keys()
        pagesList.sort()
        return pagesList
    
    def printPagesList(self, pagesList):
        for link in pagesList:
            print link



