import simplejson as json
from operator import itemgetter

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
from fitlogapp.templatetags.fitlogapp_extras import prettydistance

def graph_event(request):
    events = Event.objects.filter(route___name='nasip_8670').order_by("date").all()
    data = [(utils.datetime2ts(e.date)*1000,e.pace*1000*1000,{'eventdata':e.caldata}) for e in events if e.pace is not None]
    data = [data]
    
    options = {'series':{
                    'lines':{'show':False},
                    'points':{'show':True}
                },
                'xaxis':{
                    'mode':'time'
                },
                'yaxis':{
                    'mode':'time',
                    'timeformat':'%M:%S',
                    'min': 0
                },
                'grid': { 
                    'hoverable': True, 
                    'clickable': False 
                }
            }
    
    response = {'data':data,'options':options}
    return HttpResponse(json.dumps(response), mimetype="application/json")
     
def data_trunc_week(dt):
    weekday = (int(dt.strftime('%w'))-1)%7 #0-monday
    return dt - timedelta(days=weekday)

SUMMARY_TYPES = ('time','distance')
GRANULARITIES = {'day': {
                        'data_trunc': lambda dt:dt
                  },
                 'week':{
                        'data_trunc': data_trunc_week
                  },
                 'month':{
                        'data_trunc': lambda dt: dt.replace(day=1)
                  },
                 'year':{
                        'data_trunc': lambda dt: dt.replace(day=1,month=1)
                  }
            }
     
def graph_summary(request):
    
    granularity = request.GET.get('granularity','month')
    _type = request.GET.get('type','time')
    
    today = date.today()
    tomorrow = today+timedelta(days=1)
    twelveMonthsAgo = today-timedelta(days=365)
    sixMonthsAgo = today-timedelta(days=180)
    oneMonthsAgo = today-timedelta(days=30)
    twoMonthsAgo = today-timedelta(days=60)
    startyear = today.replace(day=1,month=1)
    weekday = (int(today.strftime('%w'))-1)%7 #0-monday
    startweek = today - timedelta(days=weekday)
    startweek_next = startweek+timedelta(days=7)
    startweek_2next = startweek+timedelta(days=14)

    if granularity == 'day':
        start = oneMonthsAgo
        stop = tomorrow
    elif granularity == 'week':
        start = sixMonthsAgo
        stop = startweek_next
    elif granularity == 'month':
        start = twelveMonthsAgo
        stop = startweek_next
    else:
        start = twoMonthsAgo
        stop = startweek_next
    
    assert granularity in GRANULARITIES.keys(), 'invalid granularity: ' + granularity
    assert _type in SUMMARY_TYPES, 'invalid type: ' + _type
    
    granularity = GRANULARITIES[granularity]
    data_trunc = granularity['data_trunc']
    
    pstart = utils.datetime2ts(data_trunc(start))*1000
    pstop = utils.datetime2ts(data_trunc(stop))*1000
    
    totaltime = {}
    rundata = {}
    cycledata = {}
    
    for event in Event.objects.all():
        tags = event.tagstrs
        pts = utils.datetime2ts(data_trunc(event.date))*1000
        
        totaltime.setdefault(pts,0)
        
        if _type == 'time':
            totaltime[pts] += event.duration*1000
            
            if '#running' in tags:
                rundata.setdefault(pts,0)
                rundata[pts] += event.duration*1000
            if '#cycling' in tags:
                cycledata.setdefault(pts,0)
                cycledata[pts] += event.duration*1000
                
        if _type == 'distance':
            if '#running' in tags:
                rundata.setdefault(pts,0)
                rundata[pts] += event.distance
            if '#cycling' in tags:
                cycledata.setdefault(pts,0)
                cycledata[pts] += event.distance
            
    keys = sorted(totaltime.keys())
    
    if _type == 'time':
        pretty = lambda v:prettyduration(v/1000)
    else:
        pretty = lambda v:prettydistance(v)
    
    maketooltip = lambda k,v:pretty(v)
        
    if _type == 'time':
        totaltimedata = [(k,totaltime[k],{'tooltip':maketooltip(k,totaltime[k])}) for k in keys]
    rundata = [(k,rundata.get(k,0),{'tooltip':maketooltip(k,rundata.get(k,0))}) for k in keys]
    cycledata = [(k,cycledata.get(k,0),{'tooltip':maketooltip(k,cycledata.get(k,0))}) for k in keys]
    
    summary = {}
    summary['avg(run)'] = pretty(sum(map(itemgetter(1),rundata))/len(rundata))
    summary['avg(cycle)'] = pretty(sum(map(itemgetter(1),cycledata))/len(cycledata))
            
    data = []
    if _type == 'time':
        data.append({'label':'total','data':totaltimedata})
    data.append({'label':'run','data':rundata})
    data.append({'label':'cycle','data':cycledata})
    
    options = {'series':{
                'lines':{'show':True},
                'points':{'show':True}
                },
                'xaxis':{
                    'mode':'time',
                    'min':pstart,
                    'max':pstop
                },
                'yaxis':{
                    'mode':'time' if _type == 'time' else None,
                    'min': 0
                },
                'grid': { 
                    'hoverable': True, 
                    'clickable': False 
                }
            }
    
    response = {'data':data,'options':options,'summary':summary}
    return HttpResponse(json.dumps(response), mimetype="application/json")
