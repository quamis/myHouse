#!/usr/bin/python
# -*- coding: utf-8 -*-

# @see http://lxml.de/lxmlhtml.html#parsing-html
# @see https://gist.github.com/823821

import sys, time, codecs
import re
from datetime import date, timedelta

from DB import DB
from CACHE import CACHE
import logging
import locale
import argparse
import datetime

class View:
	def __init__(self, db):
		self.db = db
		
	def printRow(self, id, newStatus=None):
		#                                 0           1         2              3      4        5     6         7          8
		data = self.db.selectAll("SELECT `category`, `source`, `description`, `url`, `price`, `id`, `status`, `addDate`, `updateDate`  FROM `data` WHERE `id`='%s'" %(id))[0]
		data_contacts = self.db.selectAll("SELECT `key`, `value` FROM `data_contacts` WHERE `idOffer`='%s' ORDER BY `key` ASC, `value` ASC" %(id))
		data_extracted = self.db.selectAll("SELECT `key`, `value` FROM `data_extracted` WHERE `idOffer`='%s' ORDER BY `key`" %(id))

		#print data
		#print data_contacts
		#print data_extracted
		#print "[%2s]\t% 9s\t %s" % (row[0], row[5], row[2])
		
		sys.stdout.write(unicode(
			"[% 9s]%s %s\n"+
			"  %s\n"
			"  % 7s EUR, \tid: %s (add:%s, upd:%s)\n") % (
			unicode(data[0]), 
			("#[%s]"%(data[6])) if data[6]!=None and data[6]!="" else "",
			unicode(data[2]), 
			unicode(data[3]), 
			locale.format(unicode("%.*f"), (0, data[4]), True),
			data[5],
			datetime.datetime.fromtimestamp(data[7]).strftime('%Y-%m-%d'), 
			datetime.datetime.fromtimestamp(data[8]).strftime('%Y-%m-%d')  ))
		
		if data_extracted:
			extr = {}
			for k in data_extracted:
				extr[k[0]] = k[1]
			
			str_surface = ""
			s = ""
			if "surface_total" in extr and extr["surface_total"]!='':
				str_surface+="%ssupraf. tot: %dmp" % (s, int(extr["surface_total"]))
				s=", "
			
			if "surface_built" in extr and extr["surface_built"]!='':
				str_surface+="%sconstr: %dmp" % (s, int(extr["surface_built"]))
				s=", "
				
			if "price_per_mp_built" in extr and extr["price_per_mp_built"]!='':
				str_surface+="%s%dEUR/mp" % (s, float(extr["price_per_mp_built"]))
				s=", "
				
			if "rooms" in extr and extr["rooms"]!='':
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
				
				
		if newStatus is not None:
			self.db.execute("UPDATE `data` SET `status`='%s' WHERE `id`='%s'" % (newStatus, id))
			self.db.flushRandom(0.001)
			sys.stdout.write("\n      ~UPDATED to '%s'\n" % (newStatus))
		
		sys.stdout.write("\n\n")
	
	
	def filter(self, args):
		#              0     1           2         3        4          5             6         7
		sql = "SELECT `id`, `category`, `source`, `price`, `addDate`, `updateDate`, `status`, `description`  FROM `data` WHERE 1" \
			+ " AND ( `status` IS NULL OR `status` NOT IN ('deleted', 'duplicate', 'hide') )" \
		
		if(args.id):
			sql+=" AND( 0 "
			for k in args.id:
				sql+=" OR `id` LIKE '%s'" % (k)
			sql+=")"
		else:
			if(args.area):
				sql+="/*area*/ AND( 0 "
				for k in args.area:
					sql+=" OR `description` LIKE '%s%%'" % (k)
				sql+=")"
				
			if(args.narea):
				sql+="/*narea*/ AND( 1 "
				for k in args.narea:
					sql+=" AND `description` NOT LIKE '%s%%'" % (k)
				sql+=")"
				
			if(args.text):
				sql+="/*text*/ AND( 0 "
				for k in args.text:
					sql+=" OR `description` LIKE '%%%s%%'" % (k)
				sql+=")"
					
			if(args.ntext):
				sql+="/*ntext*/ AND( 1 "
				for k in args.ntext:
					sql+=" AND `description` NOT LIKE '%%%s%%'" % (k)
				sql+=")"
			
			if(args.ftext):
				sql+="/*ftext*/ AND( 1 "
				for k in args.ftext:
					sql+=" AND `description` LIKE '%%%s%%'" % (k)
				sql+=")"
				
			if(args.category):
				sql+="/*category*/ AND( 0 "
				for k in args.category:
					sql+=" OR `category`='%s'" % (k)
				sql+=")"
			
			if(args.ncategory):
				sql+="/*ncategory*/ AND( 0 "
				for k in args.ncategory:
					sql+=" OR NOT(`category`='%s')" % (k)
				sql+=")"
			
			
			if(args.minPrice):
				sql+=" AND `price` > '%d'" % (args.minPrice)
				
			if(args.maxPrice):
				sql+=" AND `price` < '%d'" % (args.maxPrice)
				
				
			if(args.age):
				dt = date.today()-timedelta(days=args.age)
				sql+=" AND `updateDate`>%d" % (time.mktime(dt.timetuple()))
			
			if(args.agea):
				dt = date.today()-timedelta(days=args.agea)
				sql+=" AND `addDate`>%d" % (time.mktime(dt.timetuple()))
				
				
			if(args.status and args.status!=""):
				sql+="/*status*/ AND( 0 "
				for k in args.status:
					sql+=" OR `status`='%s'" % (k)
				sql+=")"
		
		
		sql+= " ORDER BY `price` ASC, `description` ASC"
		
		print sql
		print "-----------------------------------------------"
		
		results = self.db.selectAll(sql)
		for row in results:
			self.printRow(row[0], args.newStatus)
			
		self.db.close()

	
parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-id', 			dest='id', 			action='append', 	type=str, default=[],		help='id')
parser.add_argument('-area', 		dest='area', 		action='append', 	type=str, default=[],		help='search area')
parser.add_argument('-narea', 		dest='narea', 		action='append', 	type=str, default=[],		help='deny search area')
parser.add_argument('-text', 		dest='text', 		action='append', 	type=str, default=[],		help='text to find')
parser.add_argument('-ntext', 		dest='ntext', 		action='append', 	type=str, default=[],		help='text to skip')
parser.add_argument('-ftext', 		dest='ftext', 		action='append', 	type=str, default=[],		help='text to contain(mandatory text in the text)')
parser.add_argument('-category', 	dest='category',    action='append', 	type=str, default=[],		help='category')
parser.add_argument('-ncategory', 	dest='ncategory',   action='append', 	type=str, default=[],		help='not in category')
parser.add_argument('-maxPrice', 	dest='maxPrice', 	action='store', 	type=int, default=None,		help='max price to match')
parser.add_argument('-minPrice', 	dest='minPrice', 	action='store', 	type=int, default=None,		help='min price to match')
parser.add_argument('-age', 		dest='age', 		action='store', 	type=float, default=3.0,	help='max age in days')
parser.add_argument('-agea', 		dest='agea', 		action='store', 	type=float, default=14.0,	help='max age when added in days')
parser.add_argument('-status', 		dest='status', 		action='append', 	type=str, default=[],		help='?')
parser.add_argument('--profile', 	dest='profile', 	action='store', 	type=str, default="default",help='internal profile to use')
parser.add_argument('--newStatus', 	dest='newStatus', 	action='store', 	type=str, default=None,		help='?')
parser.add_argument('--mark', 		dest='newStatus', 	action='store', 	type=str, default=None,		help='?')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

class blank:
	def __getattr__(self, attr):
		return None
	
if args.profile=="none":
	#args = blank()
	pass
elif args.profile=="default":
	args.maxPrice = 70000
	args.minPrice = 30000
elif args.profile=="casa-leonida":
	args.area = [ "Aparatorii Patriei", "Leonida", "Berceni", "Oltenitei", "Alexandru Obregia", "Obregia", "Popesti Leordeni" ]
	#args.text = [ "metrou" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
elif args.profile=="casa-titan":
	args.area = [ "Titan", "Auchan", "Cora", "Dristor", "1 Decembrie", "23 August", "Baba Novac", "Grigorescu", "Nic% grigorescu", "Republica" ] # "Pantelimon", 
	#args.text = [ "metrou" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
elif args.profile=="casa-1mai":
	args.area = [ "Bucuresti Noi", "1 Mai", "Parc Bazilescu", "Bazilescu", "Pajura" ]
	#args.text = [ "metrou" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
elif args.profile=="case-noi":
	#args.text = [ "metrou" ]
	args.narea = [ "Balotesti", "Chiajna", "Corbeanca", "Tunari", "Comuna Berceni", "Bragadiru", "Adunatii Copaceni", "Glina", "Comuna Chitila", "Comuna Pantelimon", "Bolintin" ]
	args.ntext = [ "comuna" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
	args.agea = 1.5
elif args.profile=="case-noi-metrou":
	#args.text = [ "metrou" ]
	args.narea = [ "Balotesti", "Chiajna", "Corbeanca", "Tunari", "Comuna Berceni", "Bragadiru", "Adunatii Copaceni", "Glina", "Comuna Chitila", "Comuna Pantelimon", "Bolintin" ]
	args.ntext = [ "comuna" ]
	args.text = [ "metrou" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
	args.agea = 1.5
elif args.profile=="case-valide":
	#args.text = [ "metrou" ]
	args.narea = [ "Balotesti", "Chiajna", "Corbeanca", "Tunari", "Comuna Berceni", "Bragadiru", "Adunatii Copaceni", "Glina", "Comuna Chitila", "Comuna Pantelimon", "Bolintin" ]
	args.ntext = [ "comuna" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
	args.age = 1.5
	args.agea = 90
else:
	print "no profile, or unknown profile specified"
	raise SystemExit

	
# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

db = DB("../db/main.sqlite")
viewer = View(db)
viewer.filter(args)

raise SystemExit
