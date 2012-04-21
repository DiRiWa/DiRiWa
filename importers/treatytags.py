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

csvfile = open("../data/treaty-tags.csv")
dialect = csv.Sniffer().sniff(csvfile.read(2048))
csvfile.seek(0)
reader = csv.reader(csvfile, dialect=dialect)
headers = reader.next()

# "DiRiWa Sections"       Treaty
# privacy "Additional Protocol to the Convention for the Protection of Individuals with regard to Automatic Processing of Personal Data, regarding supervisory authorities and transborder data flows"

treatytype, created = RegionType.objects.get_or_create(name="Treaty")
if created: treatytype.save()

with transaction.commit_on_success():
    for line in reader:
        try: treaty = Region.objects.get(name=line[1], type=treatytype)
        except:
            print "Failed to recognize: %s" % line[1]
            continue
        for tag in line[0].split(', '):
            if tag=="?": continue
            tag,created = Tag.objects.get_or_create(name=tag)
            if created: tag.save()
            etag,created = EntityTag.objects.get_or_create(tag=tag, entity=treaty)
            if created:
                etag.save()
                print "%s tagged: %s" % (tag, treaty)
