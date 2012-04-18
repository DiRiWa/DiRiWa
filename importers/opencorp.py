#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append("..")
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
import csv 
from diriwa.models import *
import settings
settings.DEBUG = False
from django.db import transaction

csvfile = open("../data/opencorp/data.csv")
dialect = csv.Sniffer().sniff(csvfile.read(65535))
csvfile.seek(0)
reader = csv.reader(csvfile, dialect=dialect)
headers = reader.next()

#,"Free and open search for a company (30 pts)","Licensing: Explicit open licence = 30, no licence info = 5, explicit closed licence/no data = 0","Data: Openly licensed data dump available or open api (20 points)","Detailed data available: Directors (10 pts)","Detailed data available: Statutory Filings (10 pts)","Detailed data available: Shareholders (10 pts)","Total (out of max 100 points)"
#ALBANIA,20,5,0,10,0,10,45

headers=["Free and open search for a company (30 pts)",
         "Licensing: Explicit open licence = 30, no licence info = 5, explicit closed licence/no data = 0",
         "Data: Openly licensed data dump available or open api (20 points)",
         "Detailed data available: Directors (10 pts)",
         "Detailed data available: Statutory Filings (10 pts)",
         "Detailed data available: Shareholders (10 pts)"]
scores=[30, 30, 20, 10, 10, 10]

opencorp, created = Source.objects.get_or_create(
    url='http://http://OpenCorporates.com',
    attribution='\n'.join(["This document and the information contained in it is published under the Creative Commons Share-Alike",
                           "Attribution Licence (http://creativecommons.org/licenses/by-sa/3.0/), allowing it to be freely reused. Attribution",
                           "should be to OpenCorporates with a hyperlink to the OpenCorporates website (http://OpenCorporates.com),",
                           "where such a link is possible (e.g. web pages, PDFs, Word documents).",
                           "In addition, the underlying data is licensed under the Share-Alike Attribution Open Database Licence",
                           "(http://opendatacommons.org/licenses/odbl/). Attribution should similarly be to OpenCorporates with a",
                           "hyperlink to the OpenCorporates website (http://OpenCorporates.com), where such a link is possible (e.g.",
                           "web pages, PDFs, Word documents)."]))

if created: opencorp.save()
topic = Topic.objects.get(name='Right to Data')

with transaction.commit_on_success():
    for line in reader:
        if line[0] != 'UK':
            line[0]=line[0].title().replace(' & ', ' and ')
        try:   country = Region.objects.get(name=line[0])
        except:
            try:   country = Region.objects.get(shortname=line[0])
            except:
                print (u"Failed to recognize country '%s'" % line[0]).encode('utf8')
                continue

        for (type, score, max) in ((headers[i-1],line[i],scores[i-1]) for i in xrange(1,7)):
            quote, created = Citation.objects.get_or_create(region=country, source=opencorp, topic=topic, rating_label=type)
            if created:
                print "Adding: %s %s (max: %s) %s" % (country, score, max, type)
                quote.score=score
                quote.text="Score: %s (max: %s)\n%s" % (score, max, type )
                quote.save()
