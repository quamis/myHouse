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

    
moduleStr = "anunturi_ro";

maindb = DB("main.sqlite")
db = DB(moduleStr+".sqlite")
cache = CACHE(moduleStr)

sys.path.insert(0, moduleStr)
module = importlib.import_module("process", moduleStr)
gatherer = module.doProcess(moduleStr, maindb, db, cache)
gatherer.run()

raise SystemExit
