from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('fitlogapp.views.views2',
    url(r'^routes/$', 'routes'),
    url(r'^routes/add$', 'route_add'),
    url(r'^routes/delete$', 'route_delete'),
    url(r'^routes/edit$', 'route_edit'),
    url(r'^routes/detail$', 'route_detail'),
    url(r'^events/$', 'events'),
    url(r'^events/add$', 'event_add'),
    url(r'^events/delete$', 'event_delete'),
    url(r'^events/edit$', 'event_edit'),
    url(r'^ajax/events/calendar/data$', 'event_calendar_data'),
)

urlpatterns += patterns('fitlogapp.views.graphs',
    url(r'^ajax/graph/event$', 'graph_event'),
    url(r'^ajax/graph/summary$', 'graph_summary')
)
