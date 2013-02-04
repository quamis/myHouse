#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, codecs
import logging
from DB import DB
from CACHE import CACHE
import argparse
import importlib

sys.path.insert(0, "sources/base")


logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Gather data')
parser.add_argument('-v',       dest='verbosity',     action='store', type=int, default='1', help='[default: 1] verbosity')
parser.add_argument('-module',  dest='module',        action='store', type=str, default=None,     help='used module')
parser.add_argument('-forceUpdate',dest='forceUpdate',action='store', type=str, default=None,     help='TODO')
args = parser.parse_args()

if args.module is None:
    parser.print_help()
    raise SystemExit

moduleStr = args.module
modulePath = "sources/"+args.module

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

maindb = DB("../db/main.sqlite")
db = DB("../db/"+moduleStr+".sqlite")
cache = CACHE(moduleStr)

sys.path.insert(0, os.path.abspath(modulePath))
module = importlib.import_module("process", moduleStr)
gatherer = module.doProcess(moduleStr, maindb, db, cache, args)
sys.stdout.write("\n")
gatherer.run()
sys.stdout.write("\n")

raise SystemExit
