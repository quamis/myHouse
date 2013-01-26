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
    
    
    def printHeader(self):
        sys.stdout.write("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
    <title>Anunturi</title>
    <META http-equiv=Content-Type content="text/html; charset=UTF-8"/>
</head>
<body>
    <style>
        div.offer{
            margin-bottom: 1em;
            border-left: 4px dotted #ccc;
            border-top: 2px dotted #ccc;
            padding-left: 0.5em;
            padding-right: 2px;
            padding-bottom: 2px;
            
            color: #444;
            min-height: 8em;
            background-color: #f0f0f0;
        }
        div.offer:hover{
            border-left: 4px solid #888;
            border-top: 2px solid #888;
            border-bottom: 2px solid #888;
            border-right: 2px solid #888;
            
            padding-right: 0px;
            padding-bottom: 0px;
            background-color: #ffffff;
        }
        
        div.offer .category{
            float: right;
            font-size: 1em;
            color: #888;
            font-weight: bold;
            padding-left: 2em; 
        }
        
        div.offer .status{
            float: right;
            font-size: 2em;
            color: #c00;
            font-weight: bold;
            padding-right: 1em;
            padding-left: 1em; 
        }
        
        div.offer .id{
            float: right;
            font-size: 0.8em;
            font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
            color: #006;
        }
        
        div.offer .description{
            display: block;
        }
        
        div.offer a.link{
            display: block;
        }
        
        div.offer .price{
            font-size: 1.5em;
            font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
            color: #c00;
        }
        
        div.offer .extraData-history{
            font-size: 1.25em;
            font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
            color: #888;
            padding-left: 2em;
        }
        div.offer .extraData-surface{
            font-size: 1.25em;
            font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
            color: #888;
        }
        
        
        div.offer .addDate{
            float: right;
            font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
            color: #888;
            padding-left: 2em;
        }
        div.offer .updateDate{
            float: right;
            font-family:Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace;
            color: #888;
            padding-left: 2em;
        }
        
        div.stats .total{
            color: #800;
            padding-left: 2em;
            font-size: 2em;
            
            min-height: 4em;
            border: 1px dotted #ccc;
        }
        
        div.stats .total{
        }


    </style>

    <script type="text/javascript">
    </script>
        """)

        views.base.view.baseView.printHeader(self)
        
    def printFooter(self, stats):
        sys.stdout.write("<div class='stats'>")
        sys.stdout.write("<div class='total'> Total: %s </div>" % (self.format_number(stats['total'])))
        
        sys.stdout.write("</body>")
        sys.stdout.write("</html>")
    
    def printItem(self, data):
        sys.stdout.write("<div class='offer'>")
        
        txtList = collections.OrderedDict()
        txtList['location'] =                 self.printRow_extraData('location',   data, 'location',             'in %s', 'location')
        txtList['year_built'] =               self.printRow_extraData('year',      data, 'year_built',            'constr in: %d', 'year')
        txtList['surface_total'] =            self.printRow_extraData('surface',   data, 'surface_total',         'supraf. tot: %dmp')
        txtList['surface_built'] =            self.printRow_extraData('surface',   data, 'surface_built',         'constr: %dmp')
        txtList['price_per_mp_built'] =       self.printRow_extraData('surface',   data, 'price_per_mp_built',    '%dEUR/mp', 'float')
        txtList['price_per_mp_surface'] =     self.printRow_extraData('surface',   data, 'price_per_mp_surface',  '%dEUR/mp', 'float')
        txtList['rooms'] =                    self.printRow_extraData('rooms',     data, 'rooms',                 '%d camere')

        text = ""
        if txtList:
            text = "<span class='extraData-surface'><span>%s</span></span>" % ("</span>, <span>".join(filter(None, txtList.values())))
        
        
        sys.stdout.write((
            "\n"
            "<span class='price'>%7s EUR</span>"
            " %s "
            "<span class='category'>%s</span>"
            "<span class='id'> %s </span>"
            "<span class='status'>%s</span>"
            "<span class='description'>%s</span>"
            "<a href='%s'>%s</a>"
            "<span class='addDate'>%s</span>"
            "<span class='updateDate'>%s</span> ") % (
            locale.format("%.*f", (0, data['price']), True),
            text, 
            data['category'],
            data['id'], 
            "#[%s]"%(data['userStatus']) if data['userStatus'] else "",
            data['description'], 
            data['url'], data['url'], 
            datetime.datetime.fromtimestamp(data['addDate']).strftime('%Y-%m-%d'), 
            datetime.datetime.fromtimestamp(data['updateDate']).strftime('%Y-%m-%d')  ))

        pre = "UNSTRUCTURED DATA: "
        for k in data['extracted']:
            if k[0] not in txtList.keys():
                if pre: 
                    sys.stdout.write("<div class='extraData-UNSTRUCTURED'> %s" % (pre));
                sys.stdout.write("<span>%s: %s</span>, " % (k[0], k[1]))
                pre = ""
                    
        if data['contacts']:
            sys.stdout.write("<div class='extraData-contacts'>")
            for k in data['contacts']:
                if k[0]=="phone":
                    sys.stdout.write("<span class='phone'>%s: <b>%s</b></span> " % (k[0], re.sub("(.+)([0-9]{3})([0-9]{4})$", r'\1.\2.\3', k[1])))
                else:
                    sys.stdout.write("<span class='misc'>%s: <b>%s</b></span> " % (k[0], k[1]))
            sys.stdout.write("</div>")
                    
        sys.stdout.write("</div>")
