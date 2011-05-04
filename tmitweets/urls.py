from django.conf.urls.defaults import *

from tmi.tmitweets import views

urlpatterns = patterns('',
    (r'^$', views.tweets),
    (r'^winner/$', views.get_winner),
    (r'^(?P<tweet_id>\d+)/vote/$', views.vote),
)
