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

csvfile = open("../data/ONI/oni_country_data_2011-11-08.csv")
dialect = csv.Sniffer().sniff(csvfile.read(65535))
csvfile.seek(0)
reader = csv.reader(csvfile, dialect=dialect)
headers = reader.next()


# country_code,country,political_score,political_description,social_score,social_description,tools_score,tools_description,conflict/security_score,conflict_security_description,transparency,consistency,testing_date,url
# AE,United Arab Emirates,3,substantial,4,pervasive,4,pervasive,2,selective,Medium,High,2009,http://opennet.net/research/profiles/uae

descs={'political': "This category is focused primarily on Web sites that express views in opposition to those of the current government. Content more broadly related to human rights, freedom of expression, minority rights, and religious movements is also considered here.",
       'social': "This group covers material related to sexuality, gambling, and illegal drugs and alcohol, as well as other topics that may be socially sensitive or perceived as offensive.",
       'conflict/security': "Content related to armed conflicts, border disputes, separatist movements, and militant groups is included in this category.",
       'tools': "Web sites that provide e-mail, Internet hosting, search, translation, Voice-over Internet Protocol (VoIP) telephone service, and circumvention methods are grouped in this category."}

severities=["ONI testing did not uncover any evidence of websites being blocked.",
            " Connectivity abnormalities are present that suggest the presence of filtering, although diagnostic work was unable to confirm conclusively that inaccessible websites are the result of deliberate tampering.",
            "Narrowly targeted filtering that blocks a small number of specific sites across a few categories or filtering that targets a single category or issue.",
            "Filtering that has either depth or breadth: either a number of categories are subject to a medium level of filtering or a low level of filtering is carried out across many categories.",
            "Filtering that is characterized by both its depth—a blocking regime that blocks a large portion of the targeted content in a given category—and its breadth—a blocking regime that includes filtering in several categories in a given theme."]

oni, created = Source.objects.get_or_create(url='http://opennet.net',
                                   attribution='\n'.join(["This data is licensed under a Creative Commons attribution license",
                                                          "(http://creativecommons.org/licenses/by/3.0/us/), meaning you're free",
                                                          "to reuse it as long as you attribute the data to the OpenNet Initiative",
                                                          "and provide a link back to http://opennet.net."]))
if created: oni.save()
topic = Topic.objects.get(name='Censorship')

with transaction.commit_on_success():
    for line in reader:
        try:   country = Region.objects.get(name=line[1])
        except:
            try:   country = Region.objects.get(shortname=line[1])
            except:
                print (u"Failed to recognize country '%s'" % line[1]).encode('utf8')
                continue
        for (type, score, text) in ((headers[i*2].split('_',1)[0],line[i*2], line[i*2+1]) for i in xrange(1,5)):
            quote, created = Citation.objects.get_or_create(region=country, source=oni, topic=topic, rating_text=type)
            if created:
                print "Adding: %s %s: %s(%s)" % (country, type, score, text)
                quote.score=score
                quote.text="%s\nScore: %s (%s) - %s" % (descs[type], score, text, severities[int(score)])
                quote.save()
