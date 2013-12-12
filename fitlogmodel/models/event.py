from __future__ import division

from datetime import date
from datetime import time
from django.db import models
from fitlogmodel.models import Route
from fitlogapp import utils
from fitlogapp.templatetags.fitlogapp_extras import prettydistance,prettyduration,prettypace

WHITE = '#FFFFFF'
BLACK = '#000000'
BLUE = '#001DF9'
DARK_BLUE = '#00108C'
LIGHT_BLUE = '#94A0FD'
PURPLE = '#61357A'
ORANGE = '#FF9200'
RED = 'red'
GREEN = 'green'

class Event(models.Model):
    date = models.DateField(default=lambda: date.today())
    route = models.ForeignKey(Route,null=True,blank=True,related_name='events')
    duration = models.IntegerField(null=False)
    _distance = models.IntegerField(null=True,blank=True)
    
    is_pb = False
    
    @property
    def distance(self):
        if self.route:
            return self._distance if self._distance is not None else self.route.distance
        else:
            return self._distance
    
    @property
    def pace(self):
        '''seconds / meter'''
        return self.duration/self.distance if self.distance else None
       
    @property
    def tagstrs(self):
        return [t.name for t in self.tags]

    @tagstrs.setter
    def tagstrs(self,tags):
        self.tags = ','.join(tags)
        
    @property
    def ratiostr(self):
        return '%.2f%%' % ((self.ratio-1)*100,)
    
    def __unicode__(self):

        distance = self.distance
        duration = self.duration
        tags = self.tagstrs
        
        #if distance:
            #pdis = prettydistance(self.distance)
            #pdur = prettyduration(self.duration)
            
            #if '#running' in tags:
                #action = 'run'
            #elif '#cycling' in tags:
                #action = 'cycle'
            #else:
                #action = '?'
            #val = '%s %s in %s' % (action,pdis,pdur)
        #else:
            #val = "?"
            
        (action,sdistance,sduration) = (None,None,None)
            
        if '#running' in tags:
            action = 'run'
        elif '#cycling' in tags:
            action = 'cycle'
        elif '#orbitrek' in tags:
            action = 'orbitrek'
        elif '#gym' in tags:
            action = 'gym'
        elif '#tennis' in tags:
            action = 'tennis'
        elif '#soccer' in tags:
            action = 'soccer'
        else:
            assert False, 'unknown action'
       
        if distance:
            sdistance = prettydistance(self.distance)
        if duration:
            sduration = prettyduration(self.duration)
        
        if sdistance:
            return '%s(%s,%s)' % (action,sdistance,sduration)
        else:
            return '%s(%s)' % (action,sduration)

    @property
    def caldata(self):

        tags = self.tagstrs
        
        data = {}
        data['id'] = self.pk
        data['title'] = str(self)
        data['allDay'] = True
        data['start'] = utils.datetime2ts(self.date)
        data['end'] = data['start']
        
        dialogparts = []
        dialogparts.append(data['title'])
        dialogparts.append(str(self.date))
        dialogparts.append('route:%s' % (self.route.name if self.route else '-',))
        dialogparts.append('pace:%s' % prettypace(self.pace))
        dialogparts.append('tags:%s' % str(self.tagstrs))
        data['dialogstr'] = '<br/>'.join(dialogparts)

        color = WHITE
        textColor = BLACK
        
        if '#running' in tags:
            textColor = WHITE
            if '#race' in tags:
                color = BLACK
            elif '#trek' in tags or '#trail' in tags or '#hill' in tags:
                color = GREEN
            elif '#fatburn' in tags:
                color = ORANGE
            elif '#easy' in tags:
                color = LIGHT_BLUE
            elif '#long' in tags:
                color = DARK_BLUE
            elif '#intervals' in tags:
                color = RED
            else:
                color = BLUE
                
        if '#gym' in tags:
            if '#legs' in tags:
                color = ORANGE
                textColor = WHITE
            elif '#intervals' in tags:
                color = RED

        data['color'] = color
        data['textColor'] = textColor
        
        return data;
    
    class Meta:
        app_label = 'fitlogmodel'
        
import tagging
tagging.register(Event)
