#!/usr/bin/python
# -*- coding: utf-8 -*-

# @see http://lxml.de/lxmlhtml.html#parsing-html
# @see https://gist.github.com/823821

import sys, time, codecs
import datetime

from DB import DB
import logging
import locale
import argparse
import numpy 

class Stats:
	def __init__(self, db, args):
		self.db = db
		self.args = args
	
	def getItem(self, idStr, fields=('data', 'data_contacts', 'data_extracted')):
		data = {}
		data_contacts = {}
		data_extracted = {}
		
		if 'data' in fields:
			data = self.db.selectAll("SELECT `category`, `source`, `description`, `url`, `price`, `id`, `status`, `addDate`, `updateDate`  FROM `data` WHERE `id`='%s'" %(idStr))[0]
			
		if 'data_contacts' in fields:
			data_contacts = self.db.selectAll("SELECT `key`, `value` FROM `data_contacts` WHERE `idOffer`='%s' ORDER BY `key` ASC, `value` ASC" %(idStr))
			
		if 'data_extracted' in fields:
			dt = self.db.selectAll("SELECT `key`, `value` FROM `data_extracted` WHERE `idOffer`='%s' ORDER BY `key`" %(idStr))
			for d in dt:
				data_extracted[d[0]] = d[1]
			
		return { 'data': data, 'data_contacts': data_contacts, 'data_extracted':data_extracted }
	
	def getSQL(self, short=False):
		#              0     1           2         3        4          5             6         7
		if short:
			sql = "SELECT `id` FROM `data` WHERE 1"
		else:
			sql = "SELECT `id`, `category`, `source`, `price`, `addDate`, `updateDate`, `status`, `description`  FROM `data` WHERE 1"
		
		if self.args.category:
			sql+="/*category*/ AND( 0 "
			for k in self.args.category:
				sql+=" OR `category`='%s'" % (k)
			sql+=")"
			
		if self.args.source:
			sql+="/*source*/ AND( 0 "
			for k in self.args.source:
				sql+=" OR `source`='%s'" % (k)
			sql+=")"
			
		if self.args.status:
			sql+="/*status*/ AND (`status`='%s')" % (self.args.status)
		
		sql += " ORDER BY `price` ASC, `description` ASC"
		return sql
	
	def extractGeneralData(self):
		timestamp = time.time()
		
		stats = {}
		stats['source'] = {}
		stats['categories'] = {}
		stats['statuses'] = {}
		
		prices = {}
		alivePeriods = []
		timeSinceAppeared = []
		timeSinceDisappeared = []
		
		rows = self.db.selectStart(self.getSQL())
		for row in rows:
			if row[1] not in stats['categories']:
				stats['categories'][row[1]] = 0
			stats['categories'][row[1]]+= 1 	

			if row[2] not in stats['source']:
				stats['source'][row[2]] = 0				
			stats['source'][row[2]]+= 1
			
			if row[6] not in stats['statuses']:
				stats['statuses'][row[6]] = 0
			stats['statuses'][row[6]]+= 1
			
			if row[1] not in prices:
				prices[row[1]] = []
				
			if row[3]:
				prices[row[1]].append(int(row[3]))
			
			alivePeriods.append(int(row[5]) - int(row[4]))
			timeSinceAppeared.append(timestamp - int(row[4]))
			timeSinceDisappeared.append(timestamp - int(row[5]))

		stats['price_per_category:mean'] = {}
		stats['price_per_category:median'] = {}
		stats['price_per_category:std'] = {}
		stats['price_per_category:var'] = {}
		for categ in prices:
			stats['price_per_category:median'][categ] = numpy.median(prices[categ])
			stats['price_per_category:mean'][categ] = numpy.mean(prices[categ])
			stats['price_per_category:std'][categ] = numpy.std(prices[categ])
			stats['price_per_category:var'][categ] = numpy.var(prices[categ])
		
		stats['alivePeriod'] = 			numpy.mean(alivePeriods)/(60*60*24)
		stats['timeSinceAppeared'] = 	numpy.mean(timeSinceAppeared)/(60*60*24)
		stats['timeSinceDisappeared'] = numpy.mean(timeSinceDisappeared)/(60*60*24)
		
		self.db.selectEnd(rows)
		return stats
		
	def printGeneralData(self, stats):
		sys.stdout.write("\n\n Sources: ")
		s = ""
		for src in sorted(stats['source'].iterkeys()):
			sys.stdout.write("%s %s(%s)" % (s, src, locale.format("%.*f", (0, stats['source'][src]), True)))
			s = ","
			
		sys.stdout.write("\n\n Categories: ")
		for src in sorted(stats['categories'].iterkeys()):
			sys.stdout.write("\n\t%s: \t% 5s \tmedia % 7s EUR (% 7s EUR)" % (src, 
				locale.format("%.*f", (0, stats['categories'][src]), True), 
				locale.format("%.*f", (0, stats['price_per_category:mean'][src]), True),
				locale.format("%.*f", (0, stats['price_per_category:median'][src]), True)))
			
			
		sys.stdout.write("\n\n Statuses: ")
		prio = ("todo", "None")
		unprio = ("old", "deleted", "duplicate")
		
		st = { }
		for src in stats['statuses']:
			val = stats['statuses'][src]
			if  src=='':
				src = "None"
				
			if  src is None:
				src = "None"
				
			st[src] = val
		stats['statuses'] = st
		
		for src in prio:
			if src in stats['statuses']:
				sys.stdout.write("\n\t%- 9s: % 9s" % (src, locale.format("%.*f", (0, stats['statuses'][src]), True)))

		for src in stats['statuses']:
			if src not in prio and src not in unprio:
				sys.stdout.write("\n\t%- 9s: % 9s" % (src, locale.format("%.*f", (0, stats['statuses'][src]), True)))
		
		for src in unprio:
			if src in stats['statuses']:
				sys.stdout.write("\n\t%- 9s: % 9s" % (src, locale.format("%.*f", (0, stats['statuses'][src]), True)))
		
		sys.stdout.write("\n\n Times: %d days alive, appeared %d days ago, dissapeared %d days ago" % (stats['alivePeriod'], stats['timeSinceAppeared'], stats['timeSinceDisappeared']))

	def _incDict(self, dict, key):
		if key not in dict:
			dict[key] = 0
			
		dict[key] +=1
		
		return dict 

	def extractDateData(self):
		stats = {}
		stats['addDate'] = {}
		stats['updateDate'] = {}
		
		if self.args.byDate=="week":
			stats['addDate:week'] = {}
			stats['updateDate:week'] = {}
			
		if self.args.byDate=="month":
			stats['addDate:month'] = {}
			stats['updateDate:month'] = {}
		
		rows = self.db.selectStart(self.getSQL())
		for row in rows:
			addDate = datetime.datetime.fromtimestamp(row[4]).strftime('%Y-%m-%d')
			updateDate = datetime.datetime.fromtimestamp(row[5]).strftime('%Y-%m-%d')
			
			stats['addDate'] = 		self._incDict(stats['addDate'], addDate)
			stats['updateDate'] = 	self._incDict(stats['updateDate'], updateDate)
			
			if self.args.byDate=="week":
				addDate = datetime.datetime.fromtimestamp(row[4]).strftime('%Y-%U')
				updateDate = datetime.datetime.fromtimestamp(row[5]).strftime('%Y-%U')
				
				stats['addDate:week'] = 	self._incDict(stats['addDate:week'], addDate)
				stats['updateDate:week'] = 	self._incDict(stats['updateDate:week'], updateDate)
				
			if self.args.byDate=="month":
				addDate = datetime.datetime.fromtimestamp(row[4]).strftime('%Y-%m')
				updateDate = datetime.datetime.fromtimestamp(row[5]).strftime('%Y-%m')
				
				stats['addDate:month'] = 		self._incDict(stats['addDate:month'], addDate)
				stats['updateDate:month'] = 	self._incDict(stats['updateDate:month'], updateDate)
			
		return stats
		
	def printDateData(self, stats):
		
		if self.args.byDate=="day":
			allKeys = list(set( stats['addDate'].keys() + stats['updateDate'].keys() ))
			fmt = "%-12s: % 9s % 9s"
			print (fmt+" offers") % ("date", "added", "updated")
						
			for key in sorted(allKeys):
				print fmt % (key, 
					locale.format("%.*f", (0, stats['addDate'][key]), True) 	if key in stats['addDate'] 		else 0, 
					locale.format("%.*f", (0, stats['updateDate'][key]), True) 	if key in stats['updateDate'] 	else 0,)
				
		elif self.args.byDate=="week":
			allKeys = list(set( stats['addDate:week'].keys() + stats['updateDate:week'].keys() ))
			fmt = "%-12s: % 9s % 9s"
			print (fmt+" offers") % ("date", "added", "updated")
						
			for key in sorted(allKeys):
				print fmt % (key, 
					locale.format("%.*f", (0, stats['addDate:week'][key]), True) 		if key in stats['addDate:week'] 	else 0, 
					locale.format("%.*f", (0, stats['updateDate:week'][key]), True) 	if key in stats['updateDate:week'] 	else 0,)
				
		elif self.args.byDate=="month":
			allKeys = list(set( stats['addDate:month'].keys() + stats['updateDate:month'].keys() ))
			fmt = "%-12s: % 9s % 9s"
			print (fmt+" offers") % ("date", "added", "updated")
						
			for key in sorted(allKeys):
				print fmt % (key, 
					locale.format("%.*f", (0, stats['addDate:month'][key]), True) 		if key in stats['addDate:month'] 	else 0, 
					locale.format("%.*f", (0, stats['updateDate:month'][key]), True) 	if key in stats['updateDate:month'] else 0,)
		
		
		
		
	def extractLocationData(self):
		stats = {}
		stats[None] = 0
		
		#rows = self.db.selectStart(self.getSQL())
		rows = self.db.selectAll(self.getSQL(True))
		for row in rows:
			data = self.getItem(row[0], ('data_extracted'))
			
			if 'location' in data['data_extracted']:
				loc = data['data_extracted']['location']
				if self.args.byLocation=="simple":
					loc="+++"
					
				if loc not in stats:
					stats[loc] = 0
				stats[loc]+=1
			else:
				stats[None]+=1

		return stats
		
	def printLocationData(self, stats):
		fmt = "%-40s: % 3s"
		print (fmt+" in this location") % ("location", "items")
					
		for key in sorted(stats.keys()):
			print fmt % ( "None" if key is None else key, 
				locale.format("%.*f", (0, stats[key]), True))
		
			
parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-source', 	dest='source', 	action='append', 		type=str, default=None,	help='TODO')
parser.add_argument('-category',dest='category',action='append', 		type=str, default=None,	help='TODO')
parser.add_argument('-status',	dest='status',	action='store', 		type=str, default=None,	help='TODO')

parser.add_argument('-byDate', 	dest='byDate', 	action='store', 		type=str, default=None,	help='TODO')
parser.add_argument('-byLocation',dest='byLocation',action='store', 	type=str, default=None,	help='TODO')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

db = DB("../db/main.sqlite")
stats = Stats(db, args)

if args.byDate:
	stats.printDateData(stats.extractDateData())
elif args.byLocation:
	stats.printLocationData(stats.extractLocationData())
else:
	stats.printGeneralData(stats.extractGeneralData())
	
sys.stdout.write("\n")
raise SystemExit
