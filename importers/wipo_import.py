#!/usr/bin/python
#
#
#####

import os
import sys
sys.path.append("..")
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
import csv 
from diriwa.models import *
import settings
from django.db import transaction
from dateutil.parser import parse as dparse
settings.DEBUG = False

csvfile = open("../data/wipo_treaties.csv")
dialect = csv.Sniffer().sniff(csvfile.read(1024))
csvfile.seek(0)
reader = csv.reader(csvfile, dialect=dialect)
headers = reader.next()

# Status,url,Country,Date,treaty
# In Force,http://www.wipo.int/treaties/en/Remarks.jsp?cnty_id=903C,Albania,"March 6, 1994",Berne Convention

treatytype, created = RegionType.objects.get_or_create(name="Treaty")

with transaction.commit_on_success():
   for line in reader:
      treaty, created = Region.objects.get_or_create(name=line[4], type=treatytype)

      if created:
         print "Created treaty %s" % treaty.name

      if not line[2].strip(): continue
      try:	signatory = Region.objects.get(name=line[2])
      except:
         try:	signatory = Region.objects.get(shortname=line[2])
         except:
            print "Failed to recognize signatory '%s'" % line[2]
            continue

      # print signatory
      if line[0]:
         memrel, created = RegionMembership.objects.get_or_create(region=treaty, member=signatory)
         memrel.type = line[0]
         if line[3].strip():
             memrel.start = dparse(line[3])
         memrel.save()
         if created:
            print "Added %s to treaty %s" % (signatory, treaty.name)
