#!/usr/bin/python
# -*- coding: utf-8 -*-

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
			sql+=" AND( 0 "
			for k in args.area:
				sql+=" OR `description` LIKE '%s%%'" % (k)
			sql+=")"
			
		if(args.narea):
			sql+=" AND( 0 "
			for k in args.area:
				sql+=" OR `description` NOT LIKE '%s%%'" % (k)
			sql+=")"
			
		if(args.text):
			sql+=" AND( 0 "
			for k in args.text:
				sql+=" OR `description` LIKE '%%%s%%'" % (k)
			sql+=")"
				
		if(args.ntext):
			sql+=" AND( 0 "
			for k in args.ntext:
				sql+=" OR `description` NOT LIKE '%%%s%%'" % (k)
			sql+=")"
		
		if(args.maxPrice):
			sql+=" AND `price` < '%d'" % (args.maxPrice)
			
		if(args.minPrice):
			sql+=" AND `price` > '%d'" % (args.minPrice)
		
		
		sql+= " ORDER BY `price` ASC, `description` ASC"
		
		print sql
		results = self.db.selectCustom(sql)
		for row in results:
			self.printRow(row)

	
		
parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-area', dest='area', 			action='append', type=str, default=[],		help='search area')
parser.add_argument('-narea', dest='narea', 		action='append', type=str, default=[],		help='deny search area')
parser.add_argument('-text', dest='text', 			action='append', type=str, default=[],		help='text to find')
parser.add_argument('-ntext', dest='ntext', 		action='append', type=str, default=[],		help='text to skip')
parser.add_argument('-maxPrice', dest='maxPrice', 	action='store', type=int, default=70000,	help='max price to match')
parser.add_argument('-minPrice', dest='minPrice', 	action='store', type=int, default=20000,	help='min price to match')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

db = DB("anunturi_ro.sqlite")
cache = CACHE("anunturi_ro")
viewer = view_anunturi_ro(db, cache)
viewer.filter(args)

raise SystemExit
