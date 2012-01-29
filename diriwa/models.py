from django.db import models
from django.contrib.auth.models import User


class Language(models.Model):
	name		= models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

class Entry(models.Model):
	pass


class RegionalEntity(Entry):
	name		= models.CharField(max_length=200)
	shortname	= models.CharField(max_length=70, blank=True)
	isocode		= models.CharField(max_length=3, blank=True)
	map			= models.FileField(upload_to="static/img/maps/", blank=True)

	class Meta:
		ordering	= ["shortname"]

	def __unicode__(self):
		return self.name
		

class RegionType(models.Model):
	name		= models.CharField(max_length=50)
	in_menu		= models.BooleanField(default=False)
	
	def __unicode__(self):
		return self.name


class Region(RegionalEntity):
	type			= models.ForeignKey(RegionType)
	
	class Meta:
		ordering	= ["name"]
		
	def population(self):
		return sum([x.population for x in self.country_set.all()])
			
	def agreements(self):
		agreements = []
		for i in self.country_set.all():
			agreements.extend(i.treaties())
			agreements.extend(i.unions())
		return set(agreements)
		
	def __unicode__(self):
		return self.name



class RegionalEntityLocalName(models.Model):
	language		= models.ForeignKey(Language)
	entity		= models.ForeignKey(RegionalEntity)
	name		= models.CharField(max_length=200, blank=True)


class Country(RegionalEntity):
	population	= models.IntegerField(blank=True, default=0)
	regions		= models.ManyToManyField(Region)
	languages	= models.ManyToManyField(Language, blank=True)
	
	
	def safe(self):
		if self.shortname == "":
			self.shortname = self.name
		super(self, save)()
		
	
	def longname(self):
		return not (self.name == self.shortname)
		
	def treaties(self):
		return self.regions.filter(type__name="Treaty")

	def unions(self):
		return self.regions.filter(type__name="Union")

	def geographical(self):
		return self.regions.filter(type__name__in=["Block", "Geographic region"])

	def __unicode__(self):
		return self.shortname


class Topic(Entry):
	name			= models.CharField(max_length=100)
	
	class Meta:
		ordering	= ["name"]
		
	def __unicode__(self):
		return self.name

class EntityTopic(Entry):
	country			= models.ForeignKey(RegionalEntity)
	topic			= models.ForeignKey(Topic)
	text			= models.TextField()
	

	def wikitext(self):
		from mwlib.uparser import simpleparse
		from htmlwriter import HTMLWriter
		from StringIO import StringIO
		out = StringIO()
		print "Unwikified text: %s" % (self.text)
		w = HTMLWriter(out)
		w.write(simpleparse(self.text))
		return out.getvalue()


	def severity(self):
		votes = self.entitytopicvote_set.all()
		count = votes.count()
		if count == 0:
			return 1
		return sum([x.value for x in votes])/count # Simple average


	def votes(self):
		return self.entitytopicvote_set.all().count()
		
	
	class Meta:
		unique_together	=	(("country", "topic"),)


class EntityTopicVote(models.Model):
	section			= models.ForeignKey(EntityTopic)
	user			= models.ForeignKey(User)
	value			= models.IntegerField(default=1)

	class Meta:
		unique_together	=	(("section", "user"),)


class Tag(models.Model):
	name			= models.CharField(max_length = 40)
	description		= models.TextField()


class EntityTag(models.Model):
	pass
	

class CourtCase(Entry):
	country			= models.ForeignKey(RegionalEntity)
	
	
class NewsItem(models.Model):
	headline		= models.CharField(max_length=200)
	text			= models.TextField()
	itemref			= models.ForeignKey(Entry, blank=True, null=True)
	author			= models.ForeignKey(User)
	timestamp_submitted	= models.DateTimeField(auto_now_add=True)
	timestamp_edited	= models.DateTimeField(auto_now=True)


class Link(models.Model):
	title			= models.CharField(max_length=200)
	url			= models.URLField()
	description		= models.TextField()
	itemref			= models.ForeignKey(Entry, blank=True, null=True)
	author			= models.ForeignKey(User)
	timestamp_submitted	= models.DateTimeField(auto_now_add=True)
	timestamp_edited	= models.DateTimeField(auto_now=True)
	
	
