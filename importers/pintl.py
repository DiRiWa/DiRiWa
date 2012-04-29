#!/usr/bin/env python
#
#
#####

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

csvfile = open("../data/pintl.csv")
dialect = csv.Sniffer().sniff(csvfile.read(65535))
csvfile.seek(0)
reader = csv.reader(csvfile, dialect=dialect)
headers = reader.next()

# data_id,url,country,chapter
# 1,https://www.privacyinternational.org/reports/armenia/i-legal-framework,Armenia, Legal Framework

topic, _ = Topic.objects.get_or_create(name='Privacy')

with transaction.commit_on_success():
   for line in reader:
      if not line[2].strip(): continue

      line[2]=line[2].strip().decode('utf8')
      if line[2][0]=='[': line[2]=line[2][1:]
      try:	country = Region.objects.get(name=line[2])
      except:
         try:	country = Region.objects.get(shortname=line[2])
         except:
            print (u"Failed to recognize signatory '%s'" % line[2]).encode('utf8')
            continue
      s=Section.objects.get_or_create(topic=topic, region=country)[0]
      link, created = Link.objects.get_or_create(title=line[3],url=line[1],itemref=s)
      if created:
          link.description="Report by Privacy International"
          link.save()
          print 'Created link to %s for %s' % (line[3], line[2])

