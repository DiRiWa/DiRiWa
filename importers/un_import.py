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
from dateutil.parser import parse as dparse
settings.DEBUG = False
from django.db import transaction

csvfile = open("../data/un_treaties.csv")
dialect = csv.Sniffer().sniff(csvfile.read(65535))
csvfile.seek(0)
reader = csv.reader(csvfile, dialect=dialect)
headers = reader.next()

#Chapter,City,Country,Treaty,Ratification,PDF,Signature
#Charter of the United Nations and Statute of the International Court of Justice,"San Francisco, 26 June 1945",Argentina,Charter of the United Nations (deposited in the archives of the Government of the United States of America).,24 Sep 1945,http://treaties.un.org/doc/Publication/MTDSG/Volume%20I/Chapter%20I/I-1.en.pdf,

treatytype, created = RegionType.objects.get_or_create(name="Treaty")

with transaction.commit_on_success():
   for line in reader:
      if not line[2].strip(): continue

      treaty, created = Region.objects.get_or_create(name=line[3].decode('utf8') , type=treatytype)

      if created:
         print (u"Created treaty %s" % treaty.name).encode('utf8')
         desc=[]
         if line[1]:
             desc.append(u"City, Date: %s" % line[1])
         if line[0]:
             desc.append(u"Chapter: %s" % line[0])
         if line[5]:
             desc.append(u"Treaty(PDF): %s" % line[5])
         treaty.description='\n\n'.join(desc)
         treaty.save()

      line[2]=line[2].decode('utf8')
      if line[2][0]=='[': line[2]=line[2][1:]
      try:	signatory = Region.objects.get(name=line[2])
      except:
         try:	signatory = Region.objects.get(shortname=line[2])
         except:
            print (u"Failed to recognize signatory '%s'" % line[2]).encode('utf8')
            continue

      # print signatory
      if line[4].strip():
         memrel, created = RegionMembership.objects.get_or_create(region=treaty, member=signatory)
         memrel.type = 'Ratified'
         try:
             date=line[4].strip()
             if date[0]=='[' and date[-1]==']': date=date[1:-1]
             date=' '.join(date.split(' ')[:3])
             memrel.start = dparse(date,fuzzy=True)
         except:
             print line[4]
             raise
         memrel.save()
         if created:
            print (u"Added %s to treaty %s" % (signatory, treaty.name)).encode('utf8')
