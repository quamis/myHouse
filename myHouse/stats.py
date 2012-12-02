#!/usr/bin/python
# -*- coding: utf-8 -*-

# @see http://lxml.de/lxmlhtml.html#parsing-html
# @see https://gist.github.com/823821

import sys, time, os, codecs
import re
from datetime import date, timedelta

from DB import DB
from CACHE import CACHE
import logging
import locale
import argparse
import numpy 

class Stats:
	def __init__(self, db):
		self.db = db
	
	def extract(self, args):
		#              0       1           2          3       4          5   
		sql = "SELECT `id`, `category`, `source`, `price`, `addDate`, `updateDate`  FROM `data` WHERE 1 ORDER BY `price` ASC, `description` ASC"
		
		timestamp = time.time()
		
		stats = {}
		stats['source'] = {}
		stats['categories'] = {}
		
		prices = {}
		alivePeriods = []
		timeSinceAppeared = []
		timeSinceDisappeared = []
		
		rows = self.db.selectStart(sql)
		for row in rows:
			if row[1] not in stats['categories']:
				stats['categories'][row[1]] = 0
			stats['categories'][row[1]]+=1	

			if row[2] not in stats['source']:
				stats['source'][row[2]] = 0				
			stats['source'][row[2]]+=1
			
			if row[1] not in prices:
				prices[row[1]] = []
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
		print stats
		self.printStats(stats)
		
	def printStats(self, stats):
		sys.stdout.write("\n Sources: ")
		s = ""
		for src in stats['source']:
			sys.stdout.write("%s %s(%s)" % (s, src, locale.format("%.*f", (0, stats['source'][src]), True)))
			s = ","
			
		sys.stdout.write("\n Categories: ")
		s = ""
		for src in stats['categories']:
			sys.stdout.write("\n\t%s: \t% 5s \tmedia % 7s EUR (% 7s EUR)" % (src, 
				locale.format("%.*f", (0, stats['categories'][src]), True), 
				locale.format("%.*f", (0, stats['price_per_category:mean'][src]), True),
				locale.format("%.*f", (0, stats['price_per_category:median'][src]), True)))
	
parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-minPrice', 	dest='minPrice', 	action='store', 	type=int, default=30000,	help='min price to match')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

db = DB("../db/main.sqlite")
stats = Stats(db)
stats.extract(args)
sys.stdout.write("\n")
raise SystemExit
