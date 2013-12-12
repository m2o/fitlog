import simplejson as json

from datetime import date
from datetime import time
from datetime import timedelta
from operator import attrgetter

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext

from fitlogmodel.models import Route
from fitlogmodel.models import Event
from fitlogapp.forms import RouteForm
from fitlogapp.forms import EventForm
from fitlogapp import utils
from fitlogapp.templatetags.fitlogapp_extras import prettyduration

def get_routes_response(request,route_add_form=None,route_edit_form=None):
    route_list = Route.objects.all()
    route_list = sorted(route_list,key=attrgetter('name'))
    
    return render_to_response('routes.html', 
                               {'route_list': route_list,
                                'route_add_form': route_add_form,
                                'route_edit_form': route_edit_form},
                               context_instance=RequestContext(request))

def routes(request):
    return get_routes_response(request,route_add_form = RouteForm())

def route_delete(request):
    id = request.POST['id']
    Route.objects.get(pk=id).delete()
    return HttpResponseRedirect(reverse('fitlogapp.views.views2.routes'))

def route_add(request):
    
    if request.method == 'POST':
        f = RouteForm(request.POST)
        if f.is_valid():            
            route = f.save()
            route.tagstrs = f.cleaned_data['tags']
            return HttpResponseRedirect(reverse('fitlogapp.views.views2.routes'))
        
        return get_routes_response(request,f)
    
def route_edit(request):
    
    if request.method == 'GET':
        route_id = request.GET['id']
        route = Route.objects.get(pk=route_id)
        tags = ' '.join(route.tagstrs)
        f = RouteForm(instance=route,initial={'tags': tags})
        return get_routes_response(request,route_add_form=None,route_edit_form=f)
    elif request.method == 'POST':
        route_id = request.POST['id']
        route = Route.objects.get(pk=route_id)
        
        f = RouteForm(request.POST,instance=route)
        if f.is_valid():
            route = f.save()
            route.tagstrs = f.cleaned_data['tags']
            return HttpResponseRedirect(reverse('fitlogapp.views.views2.routes'))
        
        return get_routes_response(request,route_edit_form=f)
    
def route_detail(request):
    
    route = Route.objects.get(pk=request.GET['id'])
    events = route.events.order_by('-date').all()

    if events:
        pb_index = 0
        min_duration = events[0].duration
        
        for (i,event) in enumerate(events):
            if event.duration < min_duration:
                min_duration = event.duration
                pb_index = i
                
        events[pb_index].is_pb = True
    
    return render_to_response('routedetail.html', 
                               {'route': route,
                                'event_list':events},
                               context_instance=RequestContext(request))
       
def get_events_response(request,event_add_form=None,event_edit_form=None):
    event_list = Event.objects.order_by('-date').all()
    
    summary_dict = dict()
    
    today = date.today()
    weekday = (int(today.strftime('%w'))-1)%7 #0-monday
    startweek = today - timedelta(days=weekday)
    startweek_next = startweek+timedelta(days=7)
    startweek_prev = startweek-timedelta(days=7)
    startyear = today.replace(day=1,month=1)
    
    startmonth = today.replace(day=1)
    startmonth_prev = startmonth.replace(month=(startmonth.month-2)%12+1)
    if startmonth_prev > startmonth:
        startmonth_prev = startmonth.replace(year=startmonth.year-1)
    
    start7days = today - timedelta(days=7)
    start30days = today - timedelta(days=30)
    
    this_week_events = Event.objects.filter(date__gte=startweek)\
                  .filter(date__lt=startweek_next)\
                  .all()
    
    last_week_events = Event.objects.filter(date__gte=startweek_prev)\
                 .filter(date__lt=startweek)\
                 .all()
    
    this_month_events = Event.objects.filter(date__gte=startmonth)\
                  .filter(date__lt=today)\
                  .all()
    
    last_month_events = Event.objects.filter(date__gte=startmonth_prev)\
                  .filter(date__lt=startmonth)\
                  .all()

    last_7days_events = Event.objects.filter(date__gte=start7days)\
                  .filter(date__lt=today)\
                  .all()
    
    last_30days_events = Event.objects.filter(date__gte=start30days)\
                  .filter(date__lt=today)\
                  .all()
    
    this_year_events = Event.objects.filter(date__gte=startyear)\
                  .filter(date__lt=today)\
                  .all()
    
    summary_dict['this_week'] = make_summary(this_week_events)
    summary_dict['last_week'] = make_summary(last_week_events)
    summary_dict['this_month'] = make_summary(this_month_events)
    summary_dict['last_month'] = make_summary(last_month_events)
    summary_dict['last_7days'] = make_summary(last_7days_events)
    summary_dict['last_30days'] = make_summary(last_30days_events)
    summary_dict['this_year'] = make_summary(this_year_events)
    
    return render_to_response('events.html', 
                               {'event_list': event_list,
                                'summary_dict': summary_dict,
                                'event_add_form': event_add_form,
                                'event_edit_form': event_edit_form},
                               context_instance=RequestContext(request))

def make_summary(events):
    
    #r120km / r3:40 / r#5 / c10km / c3:40 / c#5 / t5:00 / t#10

    rd = 0
    cd = 0
    rt = 0
    ct = 0
    tt = 0
    rn = 0
    cn = 0
    tn = 0

    for event in events:
        event_tags_strs = event.tagstrs
        
        if '#running' in event_tags_strs:
            assert event.distance is not None, 'distance is None'
            rd += event.distance
            rt += event.duration
            rn += 1
        if '#cycling' in event_tags_strs:
            assert event.distance is not None, 'distance is None'
            cd += event.distance
            ct += event.duration
            cn += 1
            
        tt += event.duration
        tn += 1
        
    
    return {'rd':rd,'rt':rt,'rn':rn,'cd':cd,'ct':ct,'cn':cn,'tt':tt,'tn':tn}

def add_time(time1,time2):
    return 0

def events(request):
    return get_events_response(request,event_add_form = EventForm())

def event_delete(request):
    id = request.POST['id']
    Event.objects.get(pk=id).delete()
    return HttpResponseRedirect(reverse('fitlogapp.views.views2.events'))

def event_add(request):
    
    if request.method == 'POST':
        f = EventForm(request.POST)
        if f.is_valid():
            event = f.save()
            event.tagstrs = f.cleaned_data['tags']
            return HttpResponseRedirect(reverse('fitlogapp.views.views2.events'))
        
        return get_events_response(request,f)
    
def event_edit(request):
    
    if request.method == 'GET':
        event_id = request.GET['id']
        event = Event.objects.get(pk=event_id)
        route = event.route
        tags = set(event.tagstrs)
        if route:
            tags -= set(event.route.tagstrs)
        duration = prettyduration(event.duration)
        f = EventForm(instance=event,initial={'tags': ' '.join(tags),'duration':duration})
        return get_events_response(request,event_add_form=None,event_edit_form=f)
    elif request.method == 'POST':
        event_id = request.POST['id']
        event = Event.objects.get(pk=event_id)
        
        f = EventForm(request.POST,instance=event)
        if f.is_valid():
            event = f.save()
            event.tagstrs = f.cleaned_data['tags']
            return HttpResponseRedirect(reverse('fitlogapp.views.views2.events'))
        
        return get_events_response(request,event_edit_form=f)
    
def event_calendar_data(request):
    frmts = int(request.GET['start'])
    tots = int(request.GET['end'])
    frm = utils.ts2datetime(frmts)
    to = utils.ts2datetime(tots)
    events = Event.objects.filter(date__gte=frm,date__lte=to).all()    
    caldata = map(attrgetter('caldata'),events)
    return HttpResponse(json.dumps(caldata), mimetype="application/json")
    
