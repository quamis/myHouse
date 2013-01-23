#!/usr/bin/python
# -*- coding: utf-8 -*-

# @see http://lxml.de/lxmlhtml.html#parsing-html
# @see https://gist.github.com/823821
import os, sys, time, codecs, importlib
import re
from datetime import date, timedelta


from DB import DB
from CACHE import CACHE
import logging
import locale
import argparse
import datetime
import csv
import collections

class View:
	def __init__(self, db, viewer, args):
		self.db = db
		self.args = args
		self.viewer = viewer
		
	
	def printRow(self, id):
		#                                 0           1         2              3      4        5     6         7          8
		data = self.db.selectAll("SELECT `category`, `source`, `description`, `url`, `price`, `id`, `status`, `addDate`, `updateDate`  FROM `data` WHERE `id`='%s'" %(id))[0]
		data_contacts = self.db.selectAll("SELECT `key`, `value` FROM `data_contacts` WHERE `idOffer`='%s' ORDER BY `key` ASC, `value` ASC" %(id))
		data_extracted = self.db.selectAll("SELECT `key`, `value` FROM `data_extracted` WHERE `idOffer`='%s' ORDER BY `key`" %(id))

		self.viewer.printItem(data, data_contacts, data_extracted)
		
		if self.args.newStatus is not None:
			self.db.execute("UPDATE `data` SET `status`='%s' WHERE `id`='%s'" % (self.args.newStatus, id))
			self.db.flushRandom(0.001)
			sys.stdout.write("\n      ~UPDATED to '%s'\n" % (self.args.newStatus))
			
	
	def filter(self):
		#              0     1           2         3        4          5             6         7
		sql = "SELECT `id`, `category`, `source`, `price`, `addDate`, `updateDate`, `status`, `description`  FROM `data` WHERE 1" \
			+ " AND ( `status` IS NULL OR `status` NOT IN ('deleted', 'duplicate', 'hide', 'hide-badArea', 'hide-badConstruction', 'hide-badPayment', 'old', 'checked-notOk') )" \
		
		if(self.args.id):
			sql+=" AND( 0 "
			for k in self.args.id:
				sql+=" OR `id` LIKE '%s'" % (k)
			sql+=")"
		else:
			if(self.args.area):
				sql+="/*area*/ AND( 0 "
				for k in self.args.area:
					sql+=" OR `description` LIKE '%s%%'" % (k)
				sql+=")"
				
			if(self.args.narea):
				sql+="/*narea*/ AND( 1 "
				for k in self.args.narea:
					sql+=" AND `description` NOT LIKE '%s%%'" % (k)
				sql+=")"
				
			if(self.args.text):
				sql+="/*text*/ AND( 0 "
				for k in self.args.text:
					sql+=" OR `description` LIKE '%%%s%%'" % (k)
				sql+=")"
					
			if(self.args.ntext):
				sql+="/*ntext*/ AND( 1 "
				for k in self.args.ntext:
					sql+=" AND `description` NOT LIKE '%%%s%%'" % (k)
				sql+=")"
			
			if(self.args.ftext):
				sql+="/*ftext*/ AND( 1 "
				for k in self.args.ftext:
					sql+=" AND `description` LIKE '%%%s%%'" % (k)
				sql+=")"
				
			if(self.args.category):
				sql+="/*category*/ AND( 0 "
				for k in self.args.category:
					sql+=" OR `category`='%s'" % (k)
				sql+=")"
			
			if(self.args.ncategory):
				sql+="/*ncategory*/ AND( 0 "
				for k in self.args.ncategory:
					sql+=" OR NOT(`category`='%s')" % (k)
				sql+=")"
			
			
			if(self.args.minPrice):
				sql+=" AND `price` > '%d'" % (self.args.minPrice)
				
			if(self.args.maxPrice):
				sql+=" AND `price` < '%d'" % (self.args.maxPrice)
				
				
			if(self.args.age):
				dt = date.today()-timedelta(days=self.args.age)
				sql+=" AND `updateDate`>%d" % (time.mktime(dt.timetuple()))
			
			if(self.args.agea):
				dt = date.today()-timedelta(days=self.args.agea)
				sql+=" AND `addDate`>%d" % (time.mktime(dt.timetuple()))
				
				
			if(self.args.status and self.args.status!=""):
				sql+="/*status*/ AND( 0 "
				for k in self.args.status:
					sql+=" OR `status`='%s'" % (k)
				sql+=")"
		
		
		sql+= " ORDER BY `price` ASC, `description` ASC"
		
		stats = {}
		results = self.db.selectAll(sql)
		stats['total'] = 0
		self.viewer.printHeader()
		for row in results:
			stats['total']+=1
			self.printRow(row[0])
		
		self.db.close()	
		self.viewer.printFooter(stats)
	

	
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
parser.add_argument('--outputFormat',dest='outputFormat',action='store', 	type=str, default="default",help='?')
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
elif args.profile=="case-leonida":
	args.area = [ "Aparatorii Patriei", "Leonida", "Berceni", "Oltenitei", "Alexandru Obregia", "Obregia", "Popesti Leordeni" ]
	#args.text = [ "metrou" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
elif args.profile=="case-titan":
	args.area = [ "Titan", "Auchan", "Cora", "Dristor", "1 Decembrie", "23 August", "Baba Novac", "Grigorescu", "Nic% grigorescu", "Republica", "IOR", "I.O.R." ] # "Pantelimon", 
	#args.text = [ "metrou" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
elif args.profile=="case-1mai":
	args.area = [ "Bucuresti Noi", "1 Mai", "Parc Bazilescu", "Bazilescu", "Pajura" ]
	#args.text = [ "metrou" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
elif args.profile=="case-noi":
	#args.text = [ "metrou" ]
	args.narea = [
				"Balotesti", "Chiajna", "Corbeanca", "Tunari", "Comuna Berceni", "Bragadiru", "Adunatii Copaceni", "Glina", "Comuna Chitila", "Comuna Pantelimon", "Bolintin", 
				"Branesti", "Islaz", "Vlasiei", "Peris", "Snagov", "Domnesti", "Telega", "Cernica", "Cucuieti", "Plataresti", "Vlasca", "Mihailesti", "Mogosoaia", "Urziceni", "Ciocanesti", "Buftea", "Ciolpani", 
				"Frumusani", "Clinceni", "Buturugeni", "Vidra", "Baneasa", "Otopeni", "Tanganu", "Ordoreanu", "Bolintin", "Darasti", "Tamadaul Mare", "Corbeanca"
	]
	args.ntext = [ "comuna" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
	args.agea = 1.5
elif args.profile=="case-noi-metrou":
	#args.text = [ "metrou" ]
	args.narea = [
				"Balotesti", "Chiajna", "Corbeanca", "Tunari", "Comuna Berceni", "Bragadiru", "Adunatii Copaceni", "Glina", "Comuna Chitila", "Comuna Pantelimon", "Bolintin", 
				"Branesti", "Islaz", "Vlasiei", "Peris", "Snagov", "Domnesti", "Telega", "Cernica", "Cucuieti", "Plataresti", "Vlasca", "Mihailesti", "Mogosoaia", "Urziceni", "Ciocanesti", "Buftea", "Ciolpani", 
				"Frumusani", "Clinceni", "Buturugeni", "Vidra", "Baneasa", "Otopeni", "Tanganu", "Ordoreanu", "Bolintin", "Darasti", "Tamadaul Mare", "Corbeanca" 
	]
	args.ntext = [ "comuna" ]
	args.text = [ "metrou" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
	args.agea = 1.5
elif args.profile=="case-valide":
	#args.text = [ "metrou" ]
	args.narea = [ 	
				"Balotesti", "Chiajna", "Corbeanca", "Tunari", "Comuna Berceni", "Bragadiru", "Adunatii Copaceni", "Glina", "Comuna Chitila", "Comuna Pantelimon", "Bolintin", 
				"Branesti", "Islaz", "Vlasiei", "Peris", "Snagov", "Domnesti", "Telega", "Cernica", "Cucuieti", "Plataresti", "Vlasca", "Mihailesti", "Mogosoaia", "Urziceni", "Ciocanesti", "Buftea", "Ciolpani", 
				"Frumusani", "Clinceni", "Buturugeni", "Vidra", "Baneasa", "Otopeni", "Tanganu", "Ordoreanu", "Bolintin", "Darasti", "Tamadaul Mare", "Corbeanca"
	]
	args.ntext = [ "comuna" ]
	args.category = [ "case-vile" ]
	args.maxPrice = 70000
	args.minPrice = 30000
	args.age = 1.5
	args.agea = 90
elif args.profile=="apt-4-cam:metrou":
	args.text = [ "metrou" ]
	args.category = [ "apt-4-cam" ]
	args.maxPrice = 70000
	args.minPrice = 30000
	args.age = 1.5
	args.agea = 90
elif args.profile=="apt-3-cam:metrou":
	args.text = [ "metrou" ]
	args.category = [ "apt-3-cam" ]
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

sys.path.insert(0, os.path.abspath("views/"+args.outputFormat))
module = importlib.import_module("views."+args.outputFormat+".view")
outputFormatter = module.newView(args)

#import views.base.view
#import views.default.view
#outputFormatter = views.default.view.newView(args)


viewer = View(db, outputFormatter, args)
viewer.filter()

raise SystemExit
