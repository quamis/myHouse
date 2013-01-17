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


class newView(views.base.view.baseView):
    def __init__(self, args):
        super(newView, self).__init__(args)
        self.fmt = fmt = '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"'+"\n"
    
    def printHeader(self):
        sys.stdout.write(self.fmt % ('id', 'category', 'source', 'status', 'description', 'url', 'price', 'currency', 'addDate', 'updateDate'))
        views.base.view.baseView.printHeader(self)
    
    def printItem(self, data, data_contacts, data_extracted):
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
        
        sys.stdout.write(self.fmt % (
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