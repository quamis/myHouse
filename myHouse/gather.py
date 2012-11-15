#!/usr/bin/python
# -*- coding: utf-8 -*-

# @see http://lxml.de/lxmlhtml.html#parsing-html
# @see https://gist.github.com/823821

import sys, time, os
from mechanize import Browser
from glob import glob
from BeautifulSoup import BeautifulSoup
import shelve
import logging
from lxml import etree
import StringIO
import re
import time
from datetime import date
import md5
import random

from DB import DB
from CACHE import CACHE

def cleanupList(pagesList):
	keys = {}
	#pagesList.sort()
	for e in pagesList:
		keys[e] = 1
	pagesList = keys.keys()
	pagesList.sort()
	return pagesList
	
		
def printPagesList(pagesList):
	for link in pagesList:
		print link

class extract_anunturi_ro:
	def __init__(self, url, db, cache):
		self.url = url
		self.db = db
		self.cache = cache
		self.db.create("anuntul_ro_links", { 
			"id": 			"VARCHAR(256)",
			"url": 			"VARCHAR(256)",
		}, ["id"])
		self.db.create("anuntul_ro_data", { 
			"id": 			"VARCHAR(64)",
			"price": 		"INT",
			"description": 		"TEXT",
			"addDate": 		"INT",
			"updateDate": 	"INT",
		}, ["id"])
		
	def printRecord(self, status, percent, price, description):
		if(status=="new"):
			print "<%02d%%>%15s %s" % (100*percent, price, description)
		else:
			print "[%02d%%]%15s %s" % (100*percent, price, description)
	
	
	def extractPagesList(self, br):
		ret=[]
		for link in br.links(url_regex="\/anunturi-imobiliare-vanzari\/(.+)\/pag-[0-9]+\/"):
			ret.append(link.url)
		return ret
	
		
	def extractDetailedPagesList(self, br):
		ret=[]
		for link in br.links(url_regex="\/anunturi-imobiliare-vanzari\/(.+)\/(.+)\.html"):
			ret.append(link.url)
		return ret
	

	def getAll(self):
		completePagesList = [self.url]
		gotPagesList = []
		detailedPagesList = []
		gotNewPage=True
		
		while gotNewPage:
			gotNewPage=False
			for link in completePagesList:
				if link not in gotPagesList: 
#					time.sleep(random.random()*5)
					logging.debug('wget %s', link)
					br = Browser()
					br.set_handle_robots(False)
					br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
					br.open(link)
					logging.debug('  wget done')
					
					gotPagesList.append(link)
					gotPagesList = cleanupList(gotPagesList)
					
					completePagesList = self.extractPagesList(br)
					completePagesList = cleanupList(completePagesList)
					
					detailedPagesList2 = self.extractDetailedPagesList(br)
					detailedPagesList = cleanupList(detailedPagesList + detailedPagesList2)
					
					gotNewPage=True
					#gotNewPage=False
		
		# printPagesList(detailedPagesList);
		logging.debug("got %d links from %d pages", len(detailedPagesList), len(completePagesList));

		# loop through all pages and gather individual links
		linkTotal = len(detailedPagesList)+1
		linkIndex = 0
		timestamp = time.time()
		cachePrefix = time.strftime("%Y%m%d")
		for link in detailedPagesList:
			linkIndex+=1
			html = self.cache.get(cachePrefix+link)
			if(html is None):
#				time.sleep(random.random()*7)
				logging.debug("wget %s", link)
				br = Browser()
				br.set_handle_robots(False)
				br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
				html = br.open(link).read()
				logging.debug('  wget done')
				self.cache.set(cachePrefix+link, html)
			else:
				logging.debug("wget %s from cache", link)
				
			# extract data from the selected page
			parser = etree.HTMLParser()
			strip_unicode = re.compile("([^-_a-zA-Z0-9!@#%&=,/'\";:~`\$\^\*\(\)\+\[\]\.\{\}\|\?\<\>\\]+|[^\s]+)");
			html = strip_unicode.sub('', html)
			tree   = etree.HTML(html)
			try:
				text = 		tree.xpath("//table[@id='detalii_anunt']//div[@class='detalii_txt']/text()")[0]
				location = 	tree.xpath("//table[@id='detalii_anunt']//div[@class='detalii_txt']/strong/text()")[0]
				addDate = 	tree.xpath("//table[@id='detalii_anunt']//div[@class='detalii_txt']/span[@class='data']/text()")[0]
				contact = 	tree.xpath("//table[@id='detalii_anunt']//div[@class='contact']/text()")[0]
				pret = 		tree.xpath("//table[@id='detalii_anunt']//span[@class='pret']/text()")[0].replace("Pret:", "").replace(".", "")
				pret = 		re.sub("[^0-9]", "", pret)
				
				id = md5.new()
				id.update(link)
				idstr = id.hexdigest()
				
				if(db.recordExists("anuntul_ro_data", idstr)):
					self.printRecord("old", float(linkIndex)/linkTotal, pret, location + text)
				else:
					self.printRecord("new", float(linkIndex)/linkTotal, pret, location + text)
					db.insert("anuntul_ro_data",
						{ 
							"id": 			idstr,
							"price": 		pret,
							"description": 	location+" "+text,
							"addDate": 		timestamp,
							"updateDate": 	timestamp,
						}) 
			except IndexError:
				logging.debug("  cannot extract info")

	
		
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

db = DB("anunturi_ro.sqlite")
cache = CACHE("anunturi_ro")
parser = extract_anunturi_ro("http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/", db, cache)
parser.getAll()

parser = extract_anunturi_ro("http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/", db, cache)
parser.getAll()

parser = extract_anunturi_ro("http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-2/", db, cache)
parser.getAll()

raise SystemExit
