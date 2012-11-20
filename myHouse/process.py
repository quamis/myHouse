#!/usr/bin/python
# -*- coding: utf-8 -*-

# @see http://lxml.de/lxmlhtml.html#parsing-html
# @see https://gist.github.com/823821

import os, sys
import logging
from DB import DB
from CACHE import CACHE
import argparse
import importlib
    
sys.path.insert(0, "base")
import base.gather


logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Gather data')
parser.add_argument('-v',       dest='verbosity',     action='store', type=int, default='1', help='[default: 1] verbosity')
parser.add_argument('-module',  dest='module',        action='store', type=str, default=None,     help='used module')
args = parser.parse_args()

    
moduleStr = args.module

maindb = DB("main.sqlite")
db = DB(moduleStr+".sqlite")
cache = CACHE(moduleStr)

sys.path.insert(0, os.path.abspath(moduleStr))
module = importlib.import_module("process", moduleStr)
gatherer = module.doProcess(moduleStr, maindb, db, cache, args)
sys.stdout.write("\n")
gatherer.run()

raise SystemExit
