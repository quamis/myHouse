#!/usr/bin/python

# @see http://lxml.de/lxmlhtml.html#parsing-html
# @see https://gist.github.com/823821

import sys, time, os
import re
from datetime import date

from DB import DB
from CACHE import CACHE
import logging
import argparse

class view_anunturi_ro:
	def __init__(self, db, cache):
		self.db = db
		self.cache = cache
		
	def printRow(self, row):
		print "[%2s]\t %s\n" % (row[1], row[4])
	
	
	def filter(self, args):
		sql = "SELECT * FROM `anuntul_ro_data` WHERE 1"
		
		if(args.area):
			sql+=" AND `description` LIKE '%s%%'" % (args.area)
			
		if(args.text):
			sql+=" AND `description` LIKE '%%%s%%'" % (args.text)
		
		if(args.maxPrice):
			sql+=" AND `price` < '%d'" % (args.maxPrice)
			
		if(args.minPrice):
			sql+=" AND `price` > '%d'" % (args.minPrice)
		
		
		sql+= " ORDER BY `price` ASC, `description` ASC"
		
		#print sql
		results = self.db.selectCustom(sql)
		for row in results:
			self.printRow(row)

	
		
parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-area', dest='area', 			action='store', type=str, default="TITAN",	help='search area')
parser.add_argument('-text', dest='text', 			action='store', type=str, default=None,		help='text to find(regexp)')
parser.add_argument('-maxPrice', dest='maxPrice', 	action='store', type=int, default=70000,	help='max price to match')
parser.add_argument('-minPrice', dest='minPrice', 	action='store', type=int, default=20000,	help='min price to match')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

db = DB("anunturi_ro.sqlite")
cache = CACHE("anunturi_ro")
viewer = view_anunturi_ro(db, cache)
viewer.filter(args)

raise SystemExit
