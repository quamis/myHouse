#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
duplicates cleanup:
	- fa o lista cu description-ul din care elimini tot ce nu e a-z, lowercase, ca sa compari doar pe lista aia. Lasa spatiile
	- trebuie mentinuta o lista de "duplicate posibile" cu tot cu sansele lor. indexata numeric, dupa indexul intern de la sql
		- apoi daca indexul se afla in lista aia, sa sar cu totul procesarea(dar asta presupune ca parsez toata lista la fiecare 
			pas, mai rapid ar putea sa fie parsarea doar "up" sau "down")
			as putea sa reduc intervalul de cautare daca lista ar fi presortata dupa categorie, descriere, link, si sa folosesc 
				o "ferestra" de cautare de 1000 de elemente de ex. Daca folosesc metoda asta, periodic (10% chances) ar trebui 
				sa fac un shuffle la lista sau sa maresc f mult fereastra, ca sa aiba sanse sa prinda si alte elemente in fereastra
				
	- matcherul trebuie instantiat o sg data, si apoi folosit set_seq1(), set_seq2() ca sa updateze datele interne si atat
	- la matcher, folosita o combinatie intre real_quick_ratio(), quick_ratio(), ratio() ca sa faca matching-ul cat mai rapid 
				
				
TODO: implementat -v=1, -v=2... 
"""

import sys, time, os, codecs
import re
import datetime

from DB import DB
from CACHE import CACHE
import logging
import locale
import argparse
from datetime import date, timedelta
import difflib
import importlib

class Cleanup:
	def __init__(self, db):
		self.db = db
	
	def findDuplicateItems(self, originalRows, args):
		windowSize = args.dup_windowSize
		minAutoMatch = args.dup_minAutoMatch
		
		duplicateRowsIndexes = []
		duplicateRowsIndexesToHide = []
		rows2 = []
		
		
		# cleanup & process the texts before doing some matching
		if args.dup_algorithm_c=='disabled':
			pass
		elif args.dup_algorithm_c=='desc:0':
			for index in range(len(originalRows)):
				row = list(originalRows[index])
				row[7] = row[7].lower()
				row[7] = re.sub("[\s]+", " ", row[7])
				row[0] = index
				rows2.insert(index, row)
		elif args.dup_algorithm_c=='desc:1':
			for index in range(len(originalRows)):
				row = list(originalRows[index])
				row[7] = row[7].lower()
				row[7] = re.sub("[^a-z0-9]", " ", row[7])
				row[7] = re.sub("[\s]+[^\s]{1,2}[\s]+", " ", row[7])
				row[7] = re.sub("[\s]+[^\s]{1,2}[\s]+", " ", row[7])
				row[7] = re.sub("[\s]+", " ", row[7])
				row[0] = index
				rows2.insert(index, row)
		elif args.dup_algorithm_c=='desc:2':
			for index in range(len(originalRows)):
				row = list(originalRows[index])
				row[7] = row[7].lower()
				row[7] = re.sub("[^a-z0-9]", " ", row[7])
				row[7] = re.sub("[\s]+[^\s]{1,3}[\s]+", " ", row[7])
				row[7] = re.sub("[\s]+[^\s]{1,3}[\s]+", " ", row[7])
				row[7] = re.sub("[\s]+", " ", row[7])
				row[0] = index
				rows2.insert(index, row)
				
		if args.dup_algorithm_s=='disabled':
			pass
		elif args.dup_algorithm_s=='1.7.2':
			rows2 = sorted(rows2, key = lambda x: (x[1], x[7], x[2]))
		elif args.dup_algorithm_s=='7.2':
			rows2 = sorted(rows2, key = lambda x: (x[7], x[2]))
		elif args.dup_algorithm_s=='len':
			rows2 = sorted(rows2, key = lambda x: (len(x[7])))

		rows = rows2
		rows2 = []
		maxindex = len(rows)
		
		seqm = difflib.SequenceMatcher(None, "", "")
		for index in range(len(rows)):
			found = False
			r1 = rows[index]
			r17 = r1[7]
			
			similarityList = []
			
			i21 = max(0, index-windowSize)
			i22 = min(maxindex, index+windowSize)
			rows2 = rows[i21:i22]
			index2 = i21
			
			seqm.set_seq1(r17)
			
			for i2 in range(len(rows2)):
				r2 = rows2[i2]
				r27 = r2[7]
				
				if index2+i2!=index and (index2+i2) not in duplicateRowsIndexes:
					seqm.set_seq2(r27)
					d1 = seqm.quick_ratio()
					if d1>minAutoMatch:
						d2 = seqm.ratio()
						if d2>minAutoMatch:
							found = True
							
							if (index) not in similarityList:
								similarityList.append(index)
							
							if (index2+i2) not in similarityList:
								similarityList.append(index2+i2)
							
							if (index) not in duplicateRowsIndexes:
								duplicateRowsIndexes.append(index)
							
							if (index2+i2) not in duplicateRowsIndexes:
								duplicateRowsIndexes.append(index2+i2)

			if found:
				similarityList = sorted(similarityList, key = lambda x: (originalRows[x][5], originalRows[x][4], originalRows[x][0]), reverse=True)

				delItem = False				
				for i2 in similarityList:
					r2 = originalRows[rows[i2][0]]
					if delItem:
						duplicateRowsIndexesToHide.append(rows[i2][0])
					delItem = True
					
				if args.verbosity>=2:
					print "\n"
					for i2 in similarityList:
						r2 = originalRows[rows[i2][0]]
						print "->[% 6s], %s, %s : %s" % (
							r2[0], 
							datetime.datetime.fromtimestamp(r2[4]).strftime('%Y-%m-%d %H:%M:%S'), 
							datetime.datetime.fromtimestamp(r2[5]).strftime('%Y-%m-%d %H:%M:%S'),
							r2[7])
				elif args.verbosity>=1:
					sys.stdout.write("\r [%05.2f%%] %04.1f%% duplicates (%d items)" % (100*float(index)/float(maxindex), 100*float(len(duplicateRowsIndexes))/float(maxindex), len(duplicateRowsIndexes)) )

		if not args.dup_apply:
			duplicateRowsIndexesToHide = []
			raise SystemExit
			
		return duplicateRowsIndexesToHide
	
	def vacuum(self, args):
		sql = "SELECT `id`, `category`, `source`, `price`, `addDate`, `updateDate`, `status`, `description`, `url`  FROM `data` WHERE 1" \
			+ " AND ( `status` IS NULL OR `status` IN ('deleted', 'duplicate', 'hide', 'hide-badArea', 'hide-badConstruction', 'hide-badPayment', 'old', 'checked-notOk') )" \
			+ " ORDER BY `price` ASC, `description` ASC"
		
		rows = self.db.selectAll(sql)
		for index in range(len(rows)):
			row = rows[index]
			sys.stdout.write("X")
			self.db.itemDelete("data", row[0])
		sys.stdout.write("\n")
		
		self.db.close()
		self.db.open()
		self.db.execute("VACUUM")
		
	def cleanup(self, args):
		if args.vacuum:
			self.vacuum(args)
		
		#              0     1           2         3        4          5             6         7              8
		sql = "SELECT `id`, `category`, `source`, `price`, `addDate`, `updateDate`, `status`, `description`, `url`  FROM `data` WHERE 1" \
			+ " AND ( `status` IS NULL OR `status` NOT IN ('deleted', 'duplicate', 'hide', 'hide-badArea', 'hide-badConstruction', 'hide-badPayment', 'old', 'checked-notOk') )" \
			+ " ORDER BY `price` ASC, `description` ASC"
		
		rows = self.db.selectAll(sql)
		
		duplicateRowsIndexesToHide = self.findDuplicateItems(rows, args)
		
		dt = date.today()-timedelta(days=5)
		maxUpdatedTime = time.mktime(dt.timetuple())
		
		for index in range(len(rows)):
			row = rows[index]
			updated = ""
			delete = False
			
			if index in duplicateRowsIndexesToHide:
				updated = "#"
				self.db.itemUpdate("data", {
					"id": row[0],
					"status": 'duplicate',
				})
			
			if args.fixstatus and row[6] is None:
				updated = "*"
				self.db.itemUpdate("data", {
					"id": row[0],
					"status": '',
				})

			
			if args.nodescription and delete is False and row[7] is None:
				delete = True
				
			if args.deleteOldItems and delete is False and row[5]<maxUpdatedTime:
				updated = "_"
				self.db.itemUpdate("data", {
					"id": row[0],
					"status": 'old',
				})
				
				
			if args.nodescription and delete is False and re.match("^[\s]*$", row[7]):
				delete = True
			
			if args.nodescription and delete is False and row[6]=='hide':
				delete = True
				
			if delete:
				updated = "X"
				self.db.itemUpdate("data", {
					"id": row[0],
					"status": 'deleted',
				})
				#self.db.itemDelete("data", row[0])
				
			sys.stdout.write(updated)
				
				
		self.db.close()

	
parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-nodescription', 	dest='nodescription', 	action='store', 	type=int, default=0,			help='remove items with no description')
parser.add_argument('-fixstatus', 		dest='fixstatus', 		action='store', 	type=int, default=0,			help='fix status=None')
parser.add_argument('-deleteOldItems', 	dest='deleteOldItems', 	action='store', 	type=int, default=0,			help='delete old items')
parser.add_argument('-vacuum', 			dest='vacuum', 			action='store', 	type=int, default=0,			help='delete old items')

parser.add_argument('-dup_apply',		dest='dup_apply',		action='store', 	type=int, default=1,			help='debug swith to be able to disabele applying updated to duplicates found')
parser.add_argument('-dup_algorithm_c',	dest='dup_algorithm_c', action='store', 	type=str, default='disabled',	help='used algorithm for duplicates detection(cleanup method), defaults to disabled. values: disabled, desc:0, desc:1, desc:2')
parser.add_argument('-dup_algorithm_s',	dest='dup_algorithm_s', action='store', 	type=str, default='disabled',	help='used algorithm for duplicates detection(sort algorithm), defaults to disabled. values: disabled, 1.7.2, 7.2, len')
parser.add_argument('-dup_windowSize', 	dest='dup_windowSize', 	action='store', 	type=int, default=5,			help='duplicates window size(will get doubled internally)')
parser.add_argument('-dup_minAutoMatch',dest='dup_minAutoMatch',action='store', 	type=float, default=0.99,		help='duplicates match percent(DO NOT SET THIS BELOW 0.80)')

parser.add_argument('-module',  		dest='module',        	action='store', 	type=str, default=None,     	help='used module')
parser.add_argument('-v',       		dest='verbosity',     	action='store', 	type=int, default='1', 			help='[default: 1] verbosity')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

if args.module:
	moduleStr = args.module
	
	db = DB("../db/"+moduleStr+".sqlite")
	cache = CACHE(moduleStr)
	
	sys.path.insert(0, os.path.abspath(moduleStr))
	module = importlib.import_module("cleanup", moduleStr)
	mod = module.doCleanup(moduleStr, db, cache, args)
	sys.stdout.write("\n")
	mod.run()
	sys.stdout.write("\n")
else:
	db = DB("../db/main.sqlite")
	cleanup = Cleanup(db)
	cleanup.cleanup(args)

sys.stdout.write("\n")
raise SystemExit
