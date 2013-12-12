from __future__ import division

from django import template

register = template.Library()

@register.filter
def prettydistance(value):
    if value is not None:
        distance = int(value)
        if distance < 1000:
            return '%s m' % (distance,)
        else:
            return '%s km' % (distance/1000,)

@register.filter
def prettyduration(value):
    if value is not None:        
        hours = value // 3600
        minutes = (value % 3600) // 60
        seconds = value % 60
        return "%02d:%02d:%02d" % (hours,minutes,seconds)

@register.filter
def prettypace(pace):
    if pace:
        pace *= 1000
        minutes = pace//60
        seconds = int(pace)%60
        return "%d:%02d / km" % (minutes,seconds)
    
@register.filter
def prettysummarydict(v):
    
    temp = 'r(%s,%s,#%d) / c(%s,%s,#%d) / t(%s,#%d)'
    
    return temp % (prettydistance(v['rd']),prettyduration(v['rt']),v['rn'],\
                   prettydistance(v['cd']),prettyduration(v['ct']),v['cn'],
                   prettyduration(v['tt']),v['tn'])