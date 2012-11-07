#!/usr/bin/python

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
import sqlite3
import md5
import pickle


def extractPagesList(br):
	ret=[]
	for link in br.links(url_regex="\/anunturi-imobiliare-vanzari\/(.+)\/pag-[0-9]+\/"):
		ret.append(link.url)
	return ret

	
def extractDetailedPagesList(br):
	ret=[]
	for link in br.links(url_regex="\/anunturi-imobiliare-vanzari\/(.+)\/(.+)\.html"):
		ret.append(link.url)
	return ret

	
def cleanupPagesList(pagesList):
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
		self.db.create("anuntul_ro_links")
		self.db.create("anuntul_ro_data")
		
		if sys.stdout.isatty():
			self.default_encoding = sys.stdout.encoding
		else:
			self.default_encoding = "ascii"
	
	def printRecord(self, status, percent, price, description):
		if(status=="new"):
			print "<%02d%%>\x1b[32m%15s\x1b[0m %s" % (100*percent, price.encode(self.default_encoding, 'replace'), (description).encode(self.default_encoding, 'replace'))
		else:
			print "[%02d%%]\x1b[32m%15s\x1b[0m %s" % (100*percent, price.encode(self.default_encoding, 'replace'), (description).encode(self.default_encoding, 'replace'))
	
	def getAll(self):
		completePagesList = [self.url]
		gotPagesList = []
		detailedPagesList = []
		gotNewPage=True
		
		while gotNewPage:
			gotNewPage=False
			for link in completePagesList:
				if link not in gotPagesList: 
					#time.sleep(1.50)
					logging.debug('wget %s', link)
					br = Browser()
					br.set_handle_robots(False)
					br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
					br.open(link)
					logging.debug('  wget done')
					
					gotPagesList.append(link)
					gotPagesList = cleanupPagesList(gotPagesList)
					
					completePagesList = extractPagesList(br)
					completePagesList = cleanupPagesList(completePagesList)
					
					detailedPagesList2 = extractDetailedPagesList(br)
					detailedPagesList = cleanupPagesList(detailedPagesList + detailedPagesList2)
					
					gotNewPage=True
					#gotNewPage=False
		
		# printPagesList(detailedPagesList);
		logging.debug("got %d links from %d pages", len(detailedPagesList), len(completePagesList));

		# loop through all pages and gather individual links
		linkTotal = len(detailedPagesList)+1
		linkIndex = 0
		for link in detailedPagesList:
			linkIndex+=1
			#time.sleep(3.00)
			logging.debug("wget %s", link)
			br = Browser()
			br.set_handle_robots(False)
			br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
			html = br.open(link).read()
			logging.debug('  wget done')
			
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
				
				id = md5.new()
				id.update(link)
				idstr = id.hexdigest()
				
				if(db.recordExists("anuntul_ro_data", idstr)):
					self.printRecord("old", linkIndex/linkTotal, pret, location + text)
				else:
					self.printRecord("new", linkIndex/linkTotal, pret, location + text)
					db.insert("anuntul_ro_data", (idstr, location, pret, location+" "+text, date.today(), date.today()))
					
			except IndexError:
				logging.debug("  cannot extract info")

	
	
#logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

class DB:
	def __init__(self, file):
		self.file = file
		self.connection = None
		self.open()
		
	def open(self):
		self.connection = sqlite3.connect(self.file)
		
	def create(self, table):
		c = self.connection.cursor()
		sql = 'CREATE TABLE IF NOT EXISTS ' + table + ' (\
			id VARCHAR(64), \
			area VARCHAR(64), \
			price INT, \
			description TEXT, \
			addDate VARCHAR(20), \
			updateDate VARCHAR(20)\
		)'
		c.execute(sql)
		self.connection.commit()
		c.close()
		self.connection.close()
		self.open()
		
	def createCache(self, section):
		c = self.connection.cursor()
		sql = 'CREATE TABLE IF NOT EXISTS ' + section + ' (\
			id VARCHAR(64), \
			data BLOB, \
			addDate VARCHAR(20) \
		)'
		c.execute(sql)
		sql = 'CREATE UNIQUE INDEX IF NOT EXISTS "id" on ' + section + ' (id ASC)'
		c.execute(sql)
		self.connection.commit()
		c.close()
		self.connection.close()
		self.open()
	
	
	def update(self, table, data):
		c = self.connection.cursor()
		sql = 'UPDATE ' + table + ' SET '
		
		s = ""
		for k, v in data.items():
			sql+= s+k+"=?"
			s = ","
		sql+=" WHERE id='" + data['id'] + "'"
		
		dataList = [];
		for k, v in data.items():
			dataList.append(v)
		
		c.execute(sql, (dataList))
		self.connection.commit()
		c.close()
		
	def insert(self, table, data):
		c = self.connection.cursor()
		sql = 'INSERT INTO ' + table + ' ('
		
		s = ""
		for k, v in data.items():
			sql+= s+k
			s = ","
		sql+= ') VALUES ('
		
		s = ""
		for k, v in data.items():
			sql+= s+'?'
			s = ","
		sql+= ')'
		
		dataList = [];
		for k, v in data.items():
			dataList.append(v)
		
		c.execute(sql, (dataList))
		self.connection.commit()
		c.close()
	
	def select(self, table, id):
		c = self.connection.cursor()
		c.execute('SELECT * FROM ' + table + ' WHERE id="'+id+'"')
		ret = c.fetchone()
		self.connection.commit()
		c.close()
		return ret

	def delete(self, table, id):
		c = self.connection.cursor()
		c.execute('DELETE FROM ' + table + ' WHERE id="'+id+'"')
		ret = c.fetchone()
		self.connection.commit()
		c.close()
		return ret


	def selectCache(self, table, id):
		c = self.connection.cursor()
		c.execute('SELECT data FROM ' + table + ' WHERE id="'+id+'"')
		ret = c.fetchone()
		self.connection.commit()
		c.close()
		return ret

	def recordExists(self, table, id):
		c = self.connection.cursor()
		c.execute('SELECT id FROM ' + table + ' WHERE id="'+id+'"')
		ret = c.fetchone()
		self.connection.commit()
		c.close()
		return bool(ret)

		
		
class CACHE:
	def __init__(self, tablePrefix):
		self.tablePrefix = tablePrefix
		self.db = DB("cache.sqlite3")
		self.db.createCache("cache_"+self.tablePrefix)
	
	def get(self, id):
		row = self.db.selectCache("cache_"+self.tablePrefix, id)
		if(row):
			return pickle.loads(row[0])
		return None
		
	def set(self, id, data):
		if(self.get(id)):
			self.db.update("cache_"+self.tablePrefix, { "id":id, "data":pickle.dumps(data) })
		else:
			self.db.insert("cache_"+self.tablePrefix, { "id":id, "data":pickle.dumps(data) })
	
	def delete(self, id):
		return self.db.delete("cache_"+self.tablePrefix, id)	

		
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

db = DB("anunturi_ro.sqlite3")
cache = CACHE("anunturi_ro")

parser = extract_anunturi_ro("http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/", db, cache)
parser.getAll()

raise SystemExit
