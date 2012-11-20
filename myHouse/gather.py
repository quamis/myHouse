#!/usr/bin/python
# -*- coding: utf-8 -*-

# @see http://lxml.de/lxmlhtml.html#parsing-html
# @see https://gist.github.com/823821

import sys
import logging
from DB import DB
from CACHE import CACHE
import importlib
    
sys.path.insert(0, "base")
import base.gather


logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

    
moduleStr = "anuntul_ro";
startUrl = "http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/"
category = "case-vile"

db = DB(moduleStr+".sqlite")
cache = CACHE(moduleStr)

sys.path.insert(0, os.path.abspath(moduleStr))
module = importlib.import_module("gather", moduleStr)
gatherer = module.newGatherer(category, startUrl, db, cache)
gatherer.getAll()

"""
parser = extract_anunturi_ro("apt-2-camere", "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/", db, cache)
parser.getAll()

parser = extract_anunturi_ro("apt-3-camere", "http:/www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-2/", db, cache)
parser.getAll()

parser = extract_anunturi_ro("apt-4-camere", "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-4-camere/pag-2/", db, cache)
parser.getAll()
"""

raise SystemExit
