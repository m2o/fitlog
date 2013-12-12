from __future__ import division

from datetime import date
from datetime import time
from django.db import models
from fitlogapp import utils
from fitlogapp.templatetags.fitlogapp_extras import prettydistance,prettyduration

class Route(models.Model):

    TYPE_TAGS = set(('#running','#cycling','#gym','#tennis','#soccer'))
    ROUTE_TYPE_TAGS = set(('#running','#cycling'))
    
    _name = models.CharField(max_length=256)
    distance = models.IntegerField(help_text='enter distance in meters')
    elevation = models.IntegerField(default=0)
    location = models.CharField(max_length=256)
    
    @property
    def name(self):
        _type = '?'

        for typetag in self.ROUTE_TYPE_TAGS:
            if typetag in self.tagstrs:
                _type = typetag[1]
                break
            
        location = self.location.lower()
        location = location[0]+location[-1]
    
        return '%s_%s_%s' % (_type,location,self._name.lower())
    
    def __unicode__(self):
        return self.name
    
    @property
    def tagstrs(self):
        return [t.name for t in self.tags]

    @tagstrs.setter
    def tagstrs(self,tags):
        self.tags = ','.join(tags)
    
    @property
    def events_count(self):
        return self.events.count()
    
    class Meta:
        app_label = 'fitlogmodel'
        
import tagging
tagging.register(Route)
    