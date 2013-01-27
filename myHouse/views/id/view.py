import views.base.view

import os, sys, time, codecs, importlib
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
import json


class newView(views.base.view.baseView):
    def __init__(self, args):
        super(newView, self).__init__(args)
        self.items = []
    
    def printFooter(self, stats):
        print json.dumps(self.items)
        #print json.dumps(self.items, indent=4, separators=(',', ': '))
        
    
    def printItem(self, data):
        self.items.append(data['id'])
