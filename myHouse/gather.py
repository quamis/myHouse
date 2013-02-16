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

parser.add_argument('--timeLimit_gatherLinks', dest='timeLimit_gatherLinks',  action='store',     type=float,   default=None,       help='in minutes(5.5=5m30s)')
parser.add_argument('--timeLimit_getAll',      dest='timeLimit_getAll',       action='store',     type=float,   default=None,       help='in minutes(10.5=10m30s), represents the total time(it takes into consideration the links time)')

args = parser.parse_args()

if args.module is None or args.url is None or args.category is None:
    parser.print_help()
    raise SystemExit

if args.UA=="random":
    # @see http://www.useragentstring.com/pages/useragentstring.php
    # @see http://whatsmyuseragent.com/
    args.UA = random.choice([
                              # Firefox
                            'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1', 
                            'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:16.0) Gecko/20100101 Firefox/16.0 ',
                            'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1', 
                            'Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/13.0.1',  
                            'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:15.0) Gecko/20120910144328 Firefox/15.0.2',

                            # Chrome
                            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/0.2.153.1 Safari/525.19',
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17',
                            'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.26 Safari/537.11', 
                            
                            # Opera
                            'Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02',
                            'Opera/9.80 (Windows NT 6.1; WOW64; U; pt) Presto/2.10.229 Version/11.62',
                             
                            # IE
                            'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
                            'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US))', 
                            'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.2; SV1; .NET CLR 3.3.69573; WOW64; en-US)',
                            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/4.0; InfoPath.2; SV1; .NET CLR 2.0.50727; WOW64)',
                             
                             # others
                            'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:x.xx) Gecko/20030504 Mozilla Firebird/0.6', # Firebird
                            'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-US; rv:1.0.1) Gecko/20021111 Chimera/0.6', # Chimera
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
