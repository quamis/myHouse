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
import locale
import argparse

class View:
	def __init__(self, db):
		self.db = db
		
	def printRow(self, id):
		#                                       0           1           2          3       4       5
		data = self.db.selectCustom("SELECT `category`, `source`, `description`, `url`, `price`, `id` FROM `data` WHERE `id`='%s'" %(id))[0]
		data_contacts = self.db.selectCustom("SELECT `key`, `value` FROM `data_contacts` WHERE `idOffer`='%s' ORDER BY `key` ASC, `value` ASC" %(id))
		data_extracted = self.db.selectCustom("SELECT `key`, `value` FROM `data_extracted` WHERE `idOffer`='%s' ORDER BY `key`" %(id))

		#print data
		#print data_contacts
		#print data_extracted
		#print "[%2s]\t% 9s\t %s" % (row[0], row[5], row[2])
		
		sys.stdout.write(("[% 9s] %s\n"+
			"  %s\n"
			"  % 7s EUR\n") % (data[0], data[2], data[3], locale.format("%.*f", (0, data[4]), True)))
		
		if data_extracted:
			extr = {}
			for k in data_extracted:
				extr[k[0]] = k[1]
			
			str_surface = ""
			s = ""
			if "surface_total" in extr:
				str_surface+="%ssupraf. tot: %dmp" % (s, int(extr["surface_total"]))
				s=", "
			
			if "surface_built" in extr:
				str_surface+="%sconstr: %dmp" % (s, int(extr["surface_built"]))
				s=", "
				
			if "price_per_mp_built" in extr:
				str_surface+="%s%dEUR/mp" % (s, float(extr["price_per_mp_built"]))
				s=", "
				
			if "rooms" in extr:
				str_surface+="%s%d camere" % (s, int(extr["rooms"]))
				s=", "
					
			
			if str_surface!="":
				sys.stdout.write("      %s\n" % (str_surface))
			
			
			"""	
			for k in data_extracted:
				sys.stdout.write("      %s: %s\n" % (k[0], k[1]))
			"""
			
		if data_contacts:
			for k in data_contacts:
				if k[0]=="phone":
					sys.stdout.write("      %s: %s" % (k[0], re.sub("(.+)([0-9]{3})([0-9]{4})$", r'\1.\2.\3', k[1])))
				else:
					sys.stdout.write("      %s: %s" % (k[0], k[1]))
				
		sys.stdout.write("\n\n")
	
	
	def filter(self, args):
		sql = "SELECT `id` FROM `data` WHERE 1"
		
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
		
		if(args.ftext):
			sql+=" AND( 1 "
			for k in args.ftext:
				sql+=" AND `description` LIKE '%%%s%%'" % (k)
			sql+=")"
		
		if(args.maxPrice):
			sql+=" AND `price` < '%d'" % (args.maxPrice)
			
		if(args.minPrice):
			sql+=" AND `price` > '%d'" % (args.minPrice)
		
		
		sql+= " ORDER BY `price` ASC, `description` ASC"
		
		print sql
		print "-----------------------------------------------"
		
		results = self.db.selectCustom(sql)
		for row in results:
			self.printRow(row[0])

	
parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-area', dest='area', 			action='append', type=str, default=[],		help='search area')
parser.add_argument('-narea', dest='narea', 		action='append', type=str, default=[],		help='deny search area')
parser.add_argument('-text', dest='text', 			action='append', type=str, default=[],		help='text to find')
parser.add_argument('-ntext', dest='ntext', 		action='append', type=str, default=[],		help='text to skip')
parser.add_argument('-ftext', dest='ftext', 		action='append', type=str, default=[],		help='text to contains(mandatory text in the text)')
parser.add_argument('-maxPrice', dest='maxPrice', 	action='store', type=int, default=70000,	help='max price to match')
parser.add_argument('-minPrice', dest='minPrice', 	action='store', type=int, default=20000,	help='min price to match')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

db = DB("main.sqlite")
viewer = View(db)
viewer.filter(args)

raise SystemExit
