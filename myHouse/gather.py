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
import urllib2

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
	def __init__(self, category, url, db, cache):
		self.category = category
		self.url = url
		self.db = db
		self.cache = cache
		self.db.create("anuntul_ro_links", { 
			"id": 			"VARCHAR(256)",
			"url": 			"VARCHAR(256)",
		}, ["id"])
		self.db.create("anuntul_ro_data", { 
			"id": 			"VARCHAR(64)",
			"category": 	"VARCHAR(64)",
			"url": 			"VARCHAR(256)",
			"contact": 		"VARCHAR(256)",
			"price": 		"INT",
			"description": 	"TEXT",
			"addDate": 		"INT",
			"updateDate": 	"INT",
		}, ["id"])
		
		
	def extractPaginationInfo(self, html):
		ret=[]
		parser = etree.HTMLParser()
		tree   = etree.HTML(html)
		hrefs = tree.xpath("//a/@href")
		for a in hrefs:
			if(re.search("\/anunturi-imobiliare-vanzari\/(.+)\/pag-[0-9]+\/", a)):
				ret.append(a)

		return ret
	
		"""
		ret=[]
		for link in br.links(url_regex="\/anunturi-imobiliare-vanzari\/(.+)\/pag-[0-9]+\/"):
			ret.append(link.url)
		return ret
		"""
	
		
	def extractOfferPagesList(self, html):
		ret=[]
		parser = etree.HTMLParser()
		tree   = etree.HTML(html)
		hrefs = tree.xpath("//a/@href")
		for a in hrefs:
			if(re.search("\/anunturi-imobiliare-vanzari\/(.+)\/(.+)\.html", a)):
				ret.append(a)

		return ret
	
	
		"""
		ret=[]
		for link in br.links(url_regex="\/anunturi-imobiliare-vanzari\/(.+)\/(.+)\.html"):
			ret.append(link.url)
		return ret
		"""
	

	def getAll(self):
		completePagesList = [self.url]
		gotPagesList = []
		detailedPagesList = []
		gotNewPage=True
		
		cachePrefix = time.strftime("%Y%m%d")
		while gotNewPage:
			gotNewPage=False
			for link in completePagesList:
				if link not in gotPagesList: 
					html = self.cache.get(cachePrefix+link)
					if(html is None):
						# TODO: configure sleep period
						#time.sleep(random.random()*7)
						try:
							logging.debug("wget %s", link)
							br = Browser()
							br.set_handle_robots(False)
							# TODO: configure user-agent
							br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
							html = br.open(link).read()
							logging.debug('  wget done')
							self.cache.set(cachePrefix+link, html)
						except urllib2.URLError, e:
							logging.debug('  wget failed, skipping')
							continue
					else:
						logging.debug("wget from cache %s", link)
				
				
					gotPagesList.append(link)
					gotPagesList = cleanupList(gotPagesList)
					
					completePagesList = self.extractPaginationInfo(html)
					completePagesList = cleanupList(completePagesList)
					
					# TODO: rename detailedPagesList2, detailedPagesList to something offer-like:)
					detailedPagesList2 = self.extractOfferPagesList(html)
					detailedPagesList = cleanupList(detailedPagesList + detailedPagesList2)
					
					gotNewPage=True
					#gotNewPage=False
		
		# printPagesList(detailedPagesList);
		logging.debug("got %d links from %d pages", len(detailedPagesList), len(completePagesList));

		# loop through all pages and gather individual links
		linkTotal = len(detailedPagesList)+1
		linkIndex = 0
		timestamp = time.time()
		#cachePrefix = time.strftime("%Y%m%d")
		cachePrefix = "page-"
		for link in detailedPagesList:
			linkIndex+=1
			html = self.cache.get(cachePrefix+link)
			if(html is None):
#				time.sleep(random.random()*7)
				try:
					logging.debug("[%02d%%]wget %s", 100*float(linkIndex)/linkTotal, link)
					br = Browser()
					br.set_handle_robots(False)
					br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
					html = br.open(link).read()
					logging.debug('  wget done')
					self.cache.set(cachePrefix+link, html)
				except urllib2.URLError, e:
					logging.debug('  wget failed, skipping')
					continue
			else:
				logging.debug("[%02d%%]wget from cache %s", 100*float(linkIndex)/linkTotal, link)
				
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
				
				if(not db.recordExists("anuntul_ro_data", idstr)):
					db.insert("anuntul_ro_data",
						{ 
							"id": 			idstr,
							"price": 		pret,
							"category": 	self.category,
							"url": 			link,
							"description": 	location+" "+text,
							"contact": 		contact,
							"addDate": 		timestamp,
							"updateDate": 	timestamp,
						}) 
			except IndexError:
				logging.debug("  cannot extract info")

	
		
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

db = DB("anunturi_ro.sqlite")
cache = CACHE("anunturi_ro")
parser = extract_anunturi_ro("case-vile", "http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/", db, cache)
parser.getAll()

parser = extract_anunturi_ro("apt-2-camere", "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/", db, cache)
parser.getAll()

parser = extract_anunturi_ro("apt-3-camere", "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-2/", db, cache)
parser.getAll()

parser = extract_anunturi_ro("apt-4-camere", "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-4-camere/pag-2/", db, cache)
parser.getAll()

raise SystemExit
