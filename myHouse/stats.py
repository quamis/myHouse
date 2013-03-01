#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, codecs
import datetime
import os, sys, importlib

from DB import DB
import logging
import locale
import argparse
import numpy 


parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-source', dest='source', action='append', type=str, default=None, help='TODO')
parser.add_argument('-category', dest='category', action='append', type=str, default=None, help='TODO')
parser.add_argument('-status', dest='status', action='store', type=str, default=None, help='TODO')
parser.add_argument('-dtadd_min', dest='dtadd_min', action='store', type=float, default=None, help='TODO')
parser.add_argument('-dtadd_max', dest='dtadd_max', action='store', type=float, default=None, help='TODO')
parser.add_argument('-dtupd_min', dest='dtupd_min', action='store', type=float, default=None, help='TODO')
parser.add_argument('-dtupd_max', dest='dtupd_max', action='store', type=float, default=None, help='TODO')
parser.add_argument('-price_min', dest='price_min', action='store', type=float, default=None, help='TODO')
parser.add_argument('-price_max', dest='price_max', action='store', type=float, default=None, help='TODO')

parser.add_argument('--type', dest='type', action='store', type=str, default="default", help='TODO')
parser.add_argument('--subtype', dest='subtype', action='store', type=str, default="default", help='TODO')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

db = DB("../db/main.sqlite")

module = importlib.import_module("stats." + args.type + ".base")
obj = module.Stats(db, vars(args))
obj.precheck()

obj.doprint(obj.group(obj.gather()))

sys.stdout.write("\n")
