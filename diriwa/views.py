from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.db.models import Q

from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, ListView

from datetime import datetime, timedelta, date
import settings

from diriwa.models import *
from diriwa.forms import *

import simplejson as json


def jsonize(f):
   def wrapped(*args, **kwargs):
      return HttpResponse(json.dumps(f(*args, **kwargs)))

   return wrapped

class RegionDetailView(DetailView):
    context_object_name = "region"
    model = Region
    def get_context_data(self, **kwargs):
        context = super(RegionDetailView, self).get_context_data(**kwargs)
        res={}
        for c in Citation.objects.filter(region=kwargs['object']):
            solo=False
            try: kwargs['object'].section_set.get(topic=c.topic)
            except: solo=True
            if not c.topic.name in res: res[c.topic.name]={'topic': c.topic,
                                                           'solo': solo,
                                                           'citations': []}
            res[c.topic.name]['citations'].append(c)
        context['citations'] = res
        return context

class TopicDetailView(DetailView):
    context_object_name = "topic"
    model = Topic

    def get_context_data(self, **kwargs):
        context = super(TopicDetailView, self).get_context_data(**kwargs)
        res={}
        for c in Citation.objects.filter(topic=kwargs['object']):
            if not c.region in res: res[c.region]={'region': c.region,
                                                   'citations': []}
            res[c.region]['citations'].append(c)
        for c in kwargs['object'].section_set.all():
            if not c.region in res: res[c.region]={'region': c.region}
            res[c.region]['section']=c
        context['citations'] = [y for _, y in sorted(res.items())]
        return context

class SectionCreateView(CreateView):
   context_object_name = "section"
   template_name = "diriwa/section_new.html"
   form_class = SectionForm
   success_url = "/regions/%(region)d/"

   def dispatch(self, *args, **kwargs):
      self.region = get_object_or_404(Region, id=kwargs["region"])
      return super(SectionCreateView, self).dispatch(*args, **kwargs)

   def get_context_data(self, *args, **kwargs):
      context_data = super(SectionCreateView, self).get_context_data(*args, **kwargs)
      context_data.update({'region': self.region})
      return context_data

   def form_valid(self, form):
      self.object = form.save(commit=False)
      self.object.region = self.region
      self.object.save()
      return HttpResponseRedirect(self.get_success_url())


class SectionDetailView(DetailView):
   context_object_name = "section"
   model = Section


class NewsItemCreateView(CreateView):
   context_object_name = "newsitem"
   template_name = "diriwa/newsitem_new.html"
   form_class = NewsItemForm
   success_url = "/news/%(id)d/"

   def dispatch(self, *args, **kwargs):
      self.entityid = int(kwargs.get("entity", 0))
      res = super(NewsItemCreateView, self).dispatch(*args, **kwargs)

      return res

   def form_valid(self, form):
      self.object = form.save(commit=False)

      if self.entityid == None:
         self.entityid = int(self.request.REQUEST.get("entity", 0))

      print "Entity id: %d" % self.entityid

      self.object.itemref = get_object_or_404(Entity, id=self.entityid)
      self.object.author = self.request.user
      self.save()

      return HttpResponseRedirect(self.get_success_url())


class NewsListView(ListView):
        context_object_name = "newsitems"
        template_name = "diriwa/newsitem_list.html"

        def get_queryset(self):
                self.entity = get_object_or_404(Entity, id=self.kwargs["entity"])
                return self.entity.relitem.all()

        def get_context_data(self, *args, **kwargs):
                context_data = super(NewsListView, self).get_context_data(*args, **kwargs)
                context_data.update({'entity': self.entity})
                return context_data


def search(request):
        ctx = {}
        q = request.REQUEST.get("q", "")
        ctx["q"] = q
        ctx["results"] = Region.objects.filter(Q(name__icontains=q) | Q(shortname__icontains=q))

        if len(ctx["results"]) == 1:
                return HttpResponseRedirect("/regions/%d/" % ctx["results"][0].id)

        return render_to_response("diriwa/searchresults.html", ctx)

@login_required
@jsonize
def section_vote(request):
   ctx = {"ok": True}

   user = request.user
   section = request.REQUEST.get("section", 0)
   vote = int(request.REQUEST.get("vote", 5))

   if section == 0:
      return {"ok": False, "error": "Invalid section (zero)"}

   try:
      v, created = SectionVote.objects.get_or_create(user=user, section_id=section)
   except Exception, e:
      return {"ok": False, "error": "Invalid section (%s)" % e}

   v.value = vote
   v.save()

   ctx["section"] = section
   ctx["vote"] = vote
   ctx["user"] = user.username
   ctx["severity"] = v.section.severity()
   ctx["votes"] = v.section.votes()

   return ctx

@jsonize
def topic_ratings(request, pk):
    ctx = {"ok": True}

    user = request.user
    try:
        topic = Topic.objects.get(id=pk)
    except Exception, e:
        return {"ok": False, "error": "Invalid topic (%s)" % e}

    try:
        quotes = Citation.objects.filter(topic=topic)
    except Exception, e:
        return {"ok": False, "error": "Invalid citation (%s)" % e}

    res={}
    for q in quotes:
        if not q.source.url in res:
            res[q.source.url]={}
        if not q.region.isocode in res[q.source.url]:
            res[q.source.url][q.region.isocode]={'id': q.region.isocode,}
        if q.score!=None:
            res[q.source.url][q.region.isocode][q.rating_label]=q.score
    return dict([(k, [x for _, x in sorted(v.items())]) for k, v in res.items()])
