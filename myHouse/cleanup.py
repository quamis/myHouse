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

class Cleanup:
	def __init__(self, db):
		self.db = db
	
	def extract(self, args):
		#              0     1           2         3        4          5             6         7
		sql = "SELECT `id`, `category`, `source`, `price`, `addDate`, `updateDate`, `status`, `description`  FROM `data` WHERE 1" \
			+ " AND ( `status` IS NULL OR `status` NOT IN ('deleted') )" \
			+ " ORDER BY `price` ASC, `description` ASC"
		
		print sql
		rows = self.db.selectAll(sql)
		for row in rows:
			updated = "."
			delete = False
			
			if args.fixstatus and row[6] is None:
				updated = "*"
				self.db.itemUpdate("data", {
					"id": row[0],
					"status": '',
				})

			
			if args.nodescription and delete is False and row[7] is None:
				delete = True
				
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
parser.add_argument('-nodescription', 	dest='nodescription', 	action='store', 	type=int, default=1,	help='remove items with no description')
parser.add_argument('-fixstatus', 		dest='fixstatus', 		action='store', 	type=int, default=1,	help='fix status=None')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

db = DB("../db/main.sqlite")
stats = Cleanup(db)
stats.extract(args)
sys.stdout.write("\n")
raise SystemExit
