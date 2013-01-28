#!/usr/bin/python
# -*- coding: utf-8 -*-

# ./view.py -category="case-vile" -status="todo" --outputFormat=id > /tmp/TODO.json
# ./view.py -category="case-vile" -status="hide" --outputFormat=id > /tmp/HIDE.json
# ./suggestions.py -datasetHIDE="/tmp/HIDE.json" -datasetTODO="/tmp/TODO.json" -datasetTEST="/tmp/TEST.json" -train=1

import sys, time, codecs
import datetime

from DB import DB
import logging
import locale
import argparse
import numpy 
import collections
import re
import json

class Stats:
    def __init__(self, db, args):
        self.db = db
        self.args = args
        
        self.results = {}
        
        
        """
        when comon keywords are found(in the TODO & HIDE list), the score is calculated like (TODO-HIDE)*knobs_commonKeywordsmultipler
        the multiply is done because the difference will be very small, and i want to "amplify" it
        """
        self.knobs_commonKeywordsmultipler = 0.5
        
        """
        when finally differentiating the final score to match it into TODO or HIDE, 2 cutoff points are used
        the categorisation is done by doing 
            score>todo_cuoff then its TODO
            score<hide_cuoff then its HIDE
        what falls between them is "undecided"
        
        the cutoffpoint is
            todo_cuoff = avg(TODO)
            hide_cuoff = avg(HIDE)
            
        in most cases, the "undecided" range is pretty big, and i want to desensitize it(make it smaller) by getting them closer together
        knobs_cutoffMultiplier = 1 => the "undecided" interval is 0
        knobs_cutoffMultiplier = 2..5 => usefull
        knobs_cutoffMultiplier = BIG_NUMBER => the "undecided" interval is close to the original cutoffs(not desensitized)
        """
        self.knobs_cutoffMultiplier = 3  
        
        """
        a list of special items to be considered when weghtening and comparing things
        """
        #self.knobs_descriptionsConsidered = ( 'price', 'surface_built', 'surface_total', 'description' )
        self.knobs_descriptionsConsidered = ( 'price', 'surface_built', 'surface_total', 'year_built', 'description' )
    
    def getItem(self, idStr, fields=('data', 'data_contacts', 'data_extracted')):
        data = {}
        data_contacts = {}
        data_extracted = {}
        if 'data' in fields:
            keys = ('id', 'internalStatus', 'userStatus', 'category', 'source', 'url', 'description', 'price', 'location', 'rooms', 'year_built', 'surface_total', 'surface_built', 'price_per_mp_total', 'price_per_mp_built', 'addDate', 'updateDate')
            values = self.db.selectAll("SELECT `" + "`, `".join(keys) + "` FROM `data` WHERE `id`='%s'" % (idStr))[0]
            data = dict(zip(keys, values))
            
        if 'data_contacts' in fields:
            data_contacts = self.db.selectAll("SELECT `key`, `value` FROM `data_contacts` WHERE `idOffer`='%s' ORDER BY `key` ASC, `value` ASC" % (idStr))
            data['contacts'] = data_contacts
            
        if 'data_extracted' in fields:
            dt = self.db.selectAll("SELECT `key`, `value` FROM `data_extracted` WHERE `idOffer`='%s' ORDER BY `key`" % (idStr))
            for d in dt:
                data_extracted[d[0]] = d[1]
            data['extracted'] = data_extracted
        
        return data
    
    def getDescription(self, idStr):
        item = self.getItem(idStr, ('data'))
        desc = []
        if 'location' in self.knobs_descriptionsConsidered:
            desc.append(item['location'])
            
        if 'price' in self.knobs_descriptionsConsidered and item['price']:
            desc.append("KEYWORDprice%d" % (round(float(item['price'])/5000)*5000))
            
        if 'surface_built' in self.knobs_descriptionsConsidered and item['surface_built']:
            desc.append("KEYWORDsurface_built%d" % (round(float(item['surface_built'] if item['surface_built'] else 0)/25)*25))
            
        if 'surface_total' in self.knobs_descriptionsConsidered and item['surface_total']:
            desc.append("KEYWORDsurface_total%d" % (round(float(item['surface_total'] if item['surface_total'] else 0)/25)*25))
        
        if 'year_built' in self.knobs_descriptionsConsidered and item['year_built']:
            desc.append("KEYWORDyear_built%d" % (round(float(item['year_built'] if item['year_built'] else 0)/5)*5))
        
        internal = self.getWords(", ".join(desc))
        
        
        desc = []
        if 'description' in self.knobs_descriptionsConsidered and item['description']:
            desc.append(item['description'])
            
        general = self.getWords(", ".join(desc), 'textOnly')
        
        return internal+general
    
    def getSQL(self, type):
        sql = "SELECT `id` FROM `data` WHERE 1"
        if type=="datasetTEST":
            ids = json.loads(open(self.args.datasetTEST).read()) 
            sql += "/*TEST*/ AND `id` IN ('"+"', '".join(ids)+"')" 
        elif type=="datasetTODO":
            ids = json.loads(open(self.args.datasetTODO).read()) 
            sql += "/*TODO*/ AND `id` IN ('"+"', '".join(ids)+"')"
        elif type=="datasetHIDE":
            ids = json.loads(open(self.args.datasetHIDE).read()) 
            sql += "/*HIDE*/ AND `id` IN ('"+"', '".join(ids)+"')"
        else:
            raise Exception("No select type specified")
        
        sql += " ORDER BY `price` ASC, `location` ASC"
        
        return sql
    
    def getWords(self, desc, type='general'):
        words = []
        w = re.split("[\s\.\,\!\;\/\+]", desc)
        for k in w:
            if type=='textOnly':
                k = re.sub("[0-9]", "", k)
                
            k = k.strip()                
            if re.match("^.{4,}$", k):
                words.append(k.lower())
        
        return words
    
    def extractData(self, type):
        stats = {}
        stats['total'] = 0
        stats['words'] = {}
        stats['normalized'] = {}
        
        rows = self.db.selectAll(self.getSQL(type))
        
        for row in rows:
            words = self.getDescription(row[0])
            if words:
                idx=0
                for k in words:
                    if k not in stats['words']:
                        stats['words'][k] = 0
                        
                    idx+=1
                    #stats['words'][k]+= float(1)/(float(idx)/(idx*1.1))
                    #stats['words'][k]+= float(idx)/(float(idx)*1.9)
                    #stats['words'][k]+= float(idx)/(float(idx)*0.5)
                    stats['words'][k]+= 1
                    
                stats['total']+=1
            
        for k in stats['words']:
            stats['normalized'][k] = float(stats['words'][k]) / stats['total']
            
        return stats
        
    def printData(self, stats):
        fmt = "%-40s: % 8s"
        print (fmt) % ("word", "encounters")
        
        def sort_fcn(x):
            if x:
                return float(x[1])
            
            return x
        
        fmt = "%-40s: % 8f"
        for key, value in sorted(stats['words'].iteritems(), key=sort_fcn, reverse=True):
            #print fmt % (key, locale.format("%.*f", (0, value/stats['total']), True))
            print fmt % (key, float(value)/stats['total'])
        

    def getAvgScore(self, todoReport, hideReport, type):
        stats = {}
        scores = []
        
        rows = self.db.selectAll(self.getSQL(type))
        for row in rows:
            words = self.getDescription(row[0])
            if words:
                score = 0
                for w in words:
                    if w in todoReport['normalized'] and w in hideReport['normalized']:
                        score+=(todoReport['normalized'][w] - hideReport['normalized'][w])*self.knobs_commonKeywordsmultipler
                    elif w in todoReport['normalized']:
                        score+=todoReport['normalized'][w]
                    elif w in hideReport['normalized']:
                        score-=hideReport['normalized'][w]
                
                scores.append(score)
                
                        
        stats['sum_score'] = numpy.sum(scores)
        stats['avg_score'] = numpy.average(scores)
        stats['median_score'] = numpy.median(scores)
        stats['min_score'] = numpy.min(scores)
        stats['max_score'] = numpy.max(scores)
        
        return stats
    
    def runTest(self):
        if self.args.train:
            if self.args.outputFormat=="default":
                logging.debug('training on the TODO dataset')
            todoReport = self.extractData("datasetTODO")
        
            if self.args.outputFormat=="default":
                logging.debug('training on the HIDE dataset')
            hideReport = self.extractData("datasetHIDE")
            
            if self.args.outputFormat=="default":
                logging.debug('calculate averages(TODO & HIDE)')
            stats_todo = self.getAvgScore(todoReport, hideReport, "datasetTODO")
            stats_hide = self.getAvgScore(todoReport, hideReport, "datasetHIDE")
            
            bigState = [todoReport, hideReport, stats_todo, stats_hide]
            open(self.args.stateFile, "wt").write(json.dumps(bigState))
        else:
            (todoReport, hideReport, stats_todo, stats_todo) = json.loads(open(self.args.stateFile).read())

        stats_todo['cutoff'] = (self.knobs_cutoffMultiplier*stats_todo['median_score']+stats_hide['median_score'])/(self.knobs_cutoffMultiplier+1)
        stats_hide['cutoff'] = (stats_todo['median_score']+self.knobs_cutoffMultiplier*stats_hide['median_score'])/(self.knobs_cutoffMultiplier+1)
        
        if self.args.outputFormat=="default":
            print("got avegages: \n\t TODO: %+.4f (%+.4f, %+.4f, %+.4f ... %+.4f)\n\t HIDE: %+.4f (%+.4f, %+.4f, %+.4f ... %+.4f)" % (
                stats_todo['cutoff'], stats_todo['median_score'], stats_todo['avg_score'], stats_todo['min_score'], stats_todo['max_score'],
                stats_hide['cutoff'], stats_hide['median_score'], stats_hide['avg_score'], stats_hide['min_score'], stats_hide['max_score']
            ))
        
        rows = self.db.selectAll(self.getSQL("datasetTEST"))
        for row in rows:
            words = self.getDescription(row[0])
            if words:
                item = self.getItem(row[0])
                
                suggestedCategory = None
                
                score = []
                for w in words:
                    if w in todoReport['normalized'] and w in hideReport['normalized']:
                        score.append((todoReport['normalized'][w] - hideReport['normalized'][w])*self.knobs_commonKeywordsmultipler)
                    elif w in todoReport['normalized']:
                        score.append(todoReport['normalized'][w])
                    elif w in hideReport['normalized']:
                        score.append(-hideReport['normalized'][w])
                    else:
                        score.append(0)
                
                score_sum = sum(score)
                if score_sum>stats_todo['cutoff']:
                    suggestedCategory = "todo"
                elif score_sum<stats_hide['cutoff']:
                    suggestedCategory = "hide"
                
                if self.args.outputFormat=="default":
                    wordsFormatted = []
                    for i,w in enumerate(words):
                        wordsFormatted.append("%s(%.4f)" % (w, score[i]))
                        
                    print "[%s][%+.4f] \n->%s\n->%s" % (
                          suggestedCategory.upper() if suggestedCategory else "----", 
                          score_sum, " ".join(wordsFormatted), item['description'])
                        
                    print ""
                elif self.args.outputFormat=="json":
                    if suggestedCategory:
                        self.results[row[0]] = suggestedCategory
                
        
    def printFooter(self):
        if self.args.outputFormat=="json":
            print json.dumps(self.results)
        
            
parser = argparse.ArgumentParser(description='Filter gatherer results.')
parser.add_argument('-datasetTEST', dest='datasetTEST',   action='store',   type=str, default=None,     help='TODO')
parser.add_argument('-datasetTODO', dest='datasetTODO',   action='store',   type=str, default=None,     help='TODO')
parser.add_argument('-datasetHIDE', dest='datasetHIDE',   action='store',   type=str, default=None,     help='TODO')
parser.add_argument('--outputFormat', dest='outputFormat',   action='store', type=str, default="default",     help='TODO')

parser.add_argument('-stateFile',   dest='stateFile',   action='store',     type=str, default="/tmp/suggestions.pickle",     help='TODO')
parser.add_argument('-train',       dest='train',       action='store',     type=int,default=None,     help='TODO')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
locale.setlocale(locale.LC_NUMERIC, '')

# change the output encoding to utf8
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

db = DB("../db/main.sqlite")
stats = Stats(db, args)

#stats.printData(stats.extractData())
stats.runTest()
stats.printFooter()
    
sys.stdout.write("\n")
raise SystemExit
