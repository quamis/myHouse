#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, codecs
import logging
from DB import DB
from CACHE import CACHE
import importlib
import random
   
import argparse

sys.path.insert(0, "sources/base")


logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Gather data')
parser.add_argument('-sleep',       dest='sleep',       action='store', type=float, default=3,          help='[default: 3] default sleep between wget calls')
parser.add_argument('-user-agent',  dest='UA',          action='store', type=str,   default='random',   help='[default: real] used user-agent("random" will pick from internal list)')
parser.add_argument('-v',           dest='verbosity',   action='store', type=int,   default='1',        help='[default: 1] verbosity')
parser.add_argument('-module',      dest='module',      action='store', type=str,   default=None,       help='used module')
parser.add_argument('-url',         dest='url',         action='store', type=str,   default=None,       help='start url')
parser.add_argument('-category',    dest='category',    action='store', type=str,   default=None,       help='url category(case-vile)')
args = parser.parse_args()

if args.module is None or args.url is None or args.category is None:
    parser.print_help()
    raise SystemExit

if args.UA=="random":
    args.UA = random.choice(['Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1',  # Firefox/Linux
                             'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:16.0) Gecko/20100101 Firefox/16.0 ', # Firefox/Linux
                             'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:x.xx) Gecko/20030504 Mozilla Firebird/0.6', # Firebird
                             'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/0.2.153.1 Safari/525.19', # Chrome
                             ])
    sys.stdout.write("Chosen UA: %s\n" % (args.UA))
    
if args.UA=="real":
    args.UA = "myHouse/0.7 (CLI; Python)";
    

moduleStr = args.module
modulePath = "sources/"+args.module
startUrl = args.url
category = args.category

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

db = DB("../db/"+moduleStr+".sqlite")
cache = CACHE(moduleStr)

sys.path.insert(0, os.path.abspath(modulePath))
module = importlib.import_module("gather", moduleStr)
gatherer = module.newGatherer(category, startUrl, db, cache, args)
gatherer.init()
gatherer.getAll()
gatherer.destroy()
sys.stdout.write("\n")
raise SystemExit
