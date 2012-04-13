#!/usr/bin/env python
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
settings.DEBUG = False

csvfile = open("../data/wto_members.csv")
dialect = csv.Sniffer().sniff(csvfile.read(1024))
csvfile.seek(0)
reader = csv.reader(csvfile, dialect=dialect)
headers = reader.next()

# Albania,2000 September 8

treatytype, created = RegionType.objects.get_or_create(name="Treaty")

with transaction.commit_on_success():
   treaty, created = Region.objects.get_or_create(name="TRIPS", type=treatytype)
   for line in reader:
      if not line[0].strip(): continue
      try:	signatory = Region.objects.get(name=line[0])
      except:
         try:	signatory = Region.objects.get(shortname=line[0])
         except:
            print "Failed to recognize signatory '%s'" % line[0]
            continue

      # print signatory
      memrel, created = RegionMembership.objects.get_or_create(region=treaty, member=signatory)
      memrel.type = line[1]
      memrel.save()
      if created:
          print "Added %s to treaty %s" % (signatory.shortname, treaty.name)
