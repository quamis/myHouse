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
import csv
import collections

class View:
	def __init__(self, db, args):
		self.db = db
		self.args = args
		self.heap = {}
		
	def printRow_extraData(self, type, extr, tag, fmt=None, valType='int'):
		if tag in extr and extr[tag]!='':
			val = extr[tag]
			if valType==None:
				val = val
			elif valType=='int':
				val = int(val)
			elif valType=='float':
				val = float(val)
			elif valType=='year':
				val = int(val)
			elif valType=='location':
				val = str(val)
			else:
				raise Exception("invalid 'valType'")
			
			if fmt:
				return fmt % (val)
			else:
				pass
		return None
		
	def printRow(self, id):
		#                                 0           1         2              3      4        5     6         7          8
		data = self.db.selectAll("SELECT `category`, `source`, `description`, `url`, `price`, `id`, `status`, `addDate`, `updateDate`  FROM `data` WHERE `id`='%s'" %(id))[0]
		data_contacts = self.db.selectAll("SELECT `key`, `value` FROM `data_contacts` WHERE `idOffer`='%s' ORDER BY `key` ASC, `value` ASC" %(id))
		data_extracted = self.db.selectAll("SELECT `key`, `value` FROM `data_extracted` WHERE `idOffer`='%s' ORDER BY `key`" %(id))

		#print data
		#print data_contacts
		#print data_extracted
		#print "[%2s]\t% 9s\t %s" % (row[0], row[5], row[2])
		
		if self.args.outputFormat=="default":
			sys.stdout.write(unicode(
				"[% 9s]%s %s\n"
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
				# make the list associative
				for k in data_extracted:
					extr[k[0]] = k[1]
				
				surf = collections.OrderedDict()
				surf['surface_total'] = 		self.printRow_extraData('surface', 	extr, 'surface_total', 		'supraf. tot: %dmp')
				surf['surface_built'] = 		self.printRow_extraData('surface', 	extr, 'surface_built', 		'constr: %dmp')
				surf['price_per_mp_built'] = 	self.printRow_extraData('surface', 	extr, 'price_per_mp_built', '%dEUR/mp', 'float')
				surf['price_per_mp_surface'] = 	self.printRow_extraData('surface', 	extr, 'price_per_mp_surface','%dEUR/mp', 'float')
				surf['rooms'] = 				self.printRow_extraData('rooms', 	extr, 'rooms', 				'%d camere')
				
				if surf:
					sys.stdout.write("      %s\n" % (", ".join(filter(None, surf.values()))))
				
				
				
				
				
				
				
				
				hist = collections.OrderedDict()
				hist['location'] = 						self.printRow_extraData('location', extr, 'location', 			'in %s', 'location')
				hist['year_built'] = 					self.printRow_extraData('year', 	extr, 'year_built', 		'constr in: %d', 'year')
				
				if hist:
					sys.stdout.write("      %s\n" % (", ".join(filter(None, hist.values()))))
				
				
				pre = "UNSTRUCTURED DATA: "
				for k in data_extracted:
					if k[0] not in surf.keys() and k[0] not in hist.keys():
						sys.stdout.write("%s" % (pre))
						sys.stdout.write("%s: %s, " % (k[0], k[1]))
						pre = ""
						
			if data_contacts:
				for k in data_contacts:
					if k[0]=="phone":
						sys.stdout.write("      %s: %s" % (k[0], re.sub("(.+)([0-9]{3})([0-9]{4})$", r'\1.\2.\3', k[1])))
					else:
						sys.stdout.write("      %s: %s" % (k[0], k[1]))
						
					
			if self.args.newStatus is not None:
				self.db.execute("UPDATE `data` SET `status`='%s' WHERE `id`='%s'" % (self.args.newStatus, id))
				self.db.flushRandom(0.001)
				sys.stdout.write("\n      ~UPDATED to '%s'\n" % (self.args.newStatus))
			
			sys.stdout.write("\n\n")
		elif self.args.outputFormat=="csv":
			fmt = '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"'+"\n"
			if 'headerWritten' not in self.heap:
				self.heap['headerWritten'] = True
				sys.stdout.write(fmt % ('id', 'category', 'source', 'status', 'description', 'url', 'price', 'currency', 'addDate', 'updateDate'))
			
			def smart_truncate(content, length=100, suffix='...'):
			    if len(content) <= length:
			        return content
			    else:
			        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix
			
			def wordwrap(text, width):
			    """
			    A word-wrap function that preserves existing line breaks
			    and most spaces in the text. Expects that existing line
			    breaks are posix newlines (\n).
			    """
			    return reduce(lambda line, word, width=width: '%s%s%s' %
					 (line,
					  ' \n'[(len(line)-line.rfind('\n')-1
					        + len(word.split('\n',1)[0]
					             ) >= width)],
					  word),
					 text.split(' ')
					)
			
			def format(text):
				text = re.sub("'", "\\'", unicode(text))
				return wordwrap(text, 100)
			
			sys.stdout.write(fmt % (
				format(data[5]),
				format(data[0]),
				format(data[1]),
				format(data[6]),
				format(data[2]),
				format(data[3]),
				format(data[4]),
				format('EUR'),
				format(datetime.datetime.fromtimestamp(data[7]).strftime('%Y-%m-%d')),
				format(datetime.datetime.fromtimestamp(data[8]).strftime('%Y-%m-%d'))
			))
		elif self.args.outputFormat=="html":
			if 'headerWritten' not in self.heap:
				self.heap['headerWritten'] = True
				sys.stdout.write("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
	<title>Anunturi</title>
	<META http-equiv=Content-Type content="text/html; charset=UTF-8"/>
</head>
<body>
	<style>
		div.offer{
			margin-bottom: 1em;
			border-left: 4px dotted #ccc;
			border-top: 2px dotted #ccc;
			padding-left: 0.5em;
			padding-right: 2px;
			padding-bottom: 2px;
			
			color: #444;
			min-height: 6em;
			background-color: #f0f0f0;
		}
		div.offer:hover{
			border-left: 4px solid #888;
			border-top: 2px solid #888;
			border-bottom: 2px solid #888;
			border-right: 2px solid #888;
			
			padding-right: 0px;
			padding-bottom: 0px;
			background-color: #ffffff;
		}
		
		div.offer .category{
			float: right;
			font-size: 1em;
			color: #888;
			font-weight: bold;
			padding-left: 2em; 
		}
		
		div.offer .status{
			float: right;
			font-size: 2em;
			color: #c00;
			font-weight: bold;
			padding-right: 1em;
			padding-left: 1em; 
		}
		
		div.offer .id{
			float: right;
			font-size: 0.8em;
			font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
			color: #006;
		}
		
		div.offer .description{
			display: block;
		}
		
		div.offer a.link{
			display: block;
		}
		
		div.offer .price{
			font-size: 1.5em;
			font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
			color: #c00;
		}
		
		div.offer .extraData-history{
			font-size: 1.25em;
			font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
			color: #888;
			padding-left: 2em;
		}
		div.offer .extraData-surface{
			font-size: 1.25em;
			font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
			color: #888;
		}
		
		
		div.offer .addDate{
			float: right;
			font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
			color: #888;
			padding-left: 2em;
		}
		div.offer .updateDate{
			float: right;
			font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
			color: #888;
			padding-left: 2em;
		}


	</style>

	<script type="text/javascript">
	</script>
				""")

			extr = {}			
			if data_extracted:
				# make the list associative
				for k in data_extracted:
					extr[k[0]] = k[1]
					
			sys.stdout.write(unicode("<div class='offer'>"))
			
				
			txtList = collections.OrderedDict()
			txtList['location'] = 				self.printRow_extraData('location', extr, 'location', 			'in %s', 'location')
			txtList['year_built'] = 			self.printRow_extraData('year', 	extr, 'year_built', 		'constr in: %d', 'year')
			txtList['surface_total'] = 			self.printRow_extraData('surface', 	extr, 'surface_total', 		'supraf. tot: %dmp')
			txtList['surface_built'] = 			self.printRow_extraData('surface', 	extr, 'surface_built', 		'constr: %dmp')
			txtList['price_per_mp_built'] = 	self.printRow_extraData('surface', 	extr, 'price_per_mp_built', '%dEUR/mp', 'float')
			txtList['price_per_mp_surface'] = 	self.printRow_extraData('surface', 	extr, 'price_per_mp_surface','%dEUR/mp', 'float')
			txtList['rooms'] = 					self.printRow_extraData('rooms', 	extr, 'rooms', 				'%d camere')

			text = ""
			if txtList:
				text = "<span class='extraData-surface'><span>%s</span></span>" % ("</span>, <span>".join(filter(None, txtList.values())))
			
			
			sys.stdout.write(unicode(
				"\n"
				"<span class='price'>%7s EUR</span>"
				" %s "
				"<span class='category'>%s</span>"
				"<span class='id'> %s </span>"
				"<span class='status'>%s</span>"
				"<span class='description'>%s</span>"
				"<a href='%s'>%s</a>"
				"<span class='addDate'>%s</span>"
				"<span class='updateDate'>%s</span> ") % (
				locale.format(unicode("%.*f"), (0, data[4]), True),
				text, 
				unicode(data[0]),
				data[5], 
				("#[%s]"%(data[6])) if data[6]!=None and data[6]!="" else "",
				unicode(data[2]), 
				unicode(data[3]), unicode(data[3]), 
				datetime.datetime.fromtimestamp(data[7]).strftime('%Y-%m-%d'), 
				datetime.datetime.fromtimestamp(data[8]).strftime('%Y-%m-%d')  ))

			pre = "UNSTRUCTURED DATA: "
			for k in data_extracted:
				if k[0] not in txtList.keys():
					if pre: 
						sys.stdout.write("<div class='extraData-UNSTRUCTURED'> %s" % (pre));
					sys.stdout.write("<span>%s: %s</span>, " % (k[0], k[1]))
					pre = ""
						
			if data_contacts:
				sys.stdout.write("<div class='extraData-contacts'>")
				for k in data_contacts:
					if k[0]=="phone":
						sys.stdout.write("<span class='phone'>%s: <b>%s</b></span> " % (k[0], re.sub("(.+)([0-9]{3})([0-9]{4})$", r'\1.\2.\3', k[1])))
					else:
						sys.stdout.write("<span class='misc'>%s: <b>%s</b></span> " % (k[0], k[1]))
				sys.stdout.write("</div>")
						
			
			sys.stdout.write(unicode("</div>"))
			sys.stdout.write(unicode("</body>"))
			sys.stdout.write(unicode("</html>"))
			
	def printHeader(self):
		pass

	def printFooter(self, stats):
		if self.args.outputFormat=="default":
			print "\n\nTotal: %d" % (stats['total'])
	
	def filter(self):
		#              0     1           2         3        4          5             6         7
		sql = "SELECT `id`, `category`, `source`, `price`, `addDate`, `updateDate`, `status`, `description`  FROM `data` WHERE 1" \
			+ " AND ( `status` IS NULL OR `status` NOT IN ('deleted', 'duplicate', 'hide', 'old') )" \
		
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
		self.printHeader()
		for row in results:
			stats['total']+=1
			self.printRow(row[0])
		
		self.db.close()	
		self.printFooter(stats)
	

	
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
viewer = View(db, args)
viewer.filter()

raise SystemExit
