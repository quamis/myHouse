#!/usr/bin/python
# -*- coding: utf-8 -*-

# @see http://lxml.de/lxmlhtml.html#parsing-html
# @see https://gist.github.com/823821

import sys
import logging
from DB import DB
from CACHE import CACHE

	
sys.path.insert(0, "base")
import base.gather

sys.path.insert(0, "anunturi_ro")
import anunturi_ro.gather

		
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)

db = DB("anunturi_ro.sqlite")
cache = CACHE("anunturi_ro")
parser = anunturi_ro.gather.extract_anunturi_ro("case-vile", "http://www.anuntul.ro/anunturi-imobiliare-vanzari/case-vile/pag-1/", db, cache)
parser.getAll()

"""
parser = extract_anunturi_ro("apt-2-camere", "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-2-camere/pag-1/", db, cache)
parser.getAll()

parser = extract_anunturi_ro("apt-3-camere", "http:/www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-3-camere/pag-2/", db, cache)
parser.getAll()

parser = extract_anunturi_ro("apt-4-camere", "http://www.anuntul.ro/anunturi-imobiliare-vanzari/apartamente-4-camere/pag-2/", db, cache)
parser.getAll()
"""

raise SystemExit
