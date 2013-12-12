import re

from django import forms

from fitlogmodel.models import Route
from fitlogmodel.models import Event

def check_has_type_tag(tags,type_tags=Route.ROUTE_TYPE_TAGS):
    inter = type_tags & tags
    if len(inter)!=1:
        raise forms.ValidationError('must contain 1 type tag: %s' % (type_tags,))
    
def check_hashtag(tags):
    if filter(lambda x: not x.startswith('#'),tags):
        raise forms.ValidationError('tags must start with #')
    
def _clean_tags(tagstr):
    return set([t for t in re.split('\s+',tagstr) if t])

class RouteForm(forms.ModelForm):

    tags = forms.CharField()
    
    def clean_tags(self):
        cleaned_tags = _clean_tags(self.cleaned_data['tags'])
        check_hashtag(cleaned_tags)
        check_has_type_tag(cleaned_tags)
        return cleaned_tags
    
    class Meta:
        model = Route
        
class EventForm(forms.ModelForm):
    
    tags = forms.CharField(required=False)
    duration = forms.CharField(required=True,initial="00:00:00")
    route = forms.ModelChoiceField(queryset=Route.objects.order_by('location','_name').all(), empty_label='-- no route --', required=False)
    
    def clean_tags(self):
        cleaned_tags = _clean_tags(self.cleaned_data['tags'])
        check_hashtag(cleaned_tags)
        return cleaned_tags
    
    def clean_duration(self):
        durationstr = self.cleaned_data['duration']
        m = re.match('^(\d{2}):(\d{2}):(\d{2})$',durationstr)
        if not m:
            raise forms.ValidationError('invalid duration')
        
        hours = int(m.group(1))
        minutes = int(m.group(2))
        seconds = int(m.group(3))
        
        if minutes > 59 or seconds > 59:
            raise forms.ValidationError('invalid duration')
        
        durationsecs = hours*3600 + minutes*60 + seconds
        return durationsecs
    
    def clean(self):
        cleaned_data = super(EventForm, self).clean()
        
        route = cleaned_data.get('route')
        tags = set(cleaned_data.get('tags',[]))
        distance = cleaned_data.get('_distance')
        
        if route is not None:
            tags -= Route.ROUTE_TYPE_TAGS
            tags |= set(route.tagstrs)
            cleaned_data['tags'] = tags
        else:
            check_has_type_tag(tags,Route.TYPE_TAGS)
            #if distance is None:
            #   raise forms.ValidationError('distance required')
        
        return cleaned_data
        
    
    class Meta:
        model = Event
