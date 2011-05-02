import settings
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^tweets/', include('tmi.tmitweets.urls')),
    (r'^admin/', include(admin.site.urls)),
)
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/glloyd/projects/tmi/static'}),
    )   

