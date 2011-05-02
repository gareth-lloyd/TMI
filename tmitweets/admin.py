from django.contrib import admin
from tmi.tmitweets.models import TMITweet

class TMITweetAdmin(admin.ModelAdmin):
    display = ('user_name',)

admin.site.register(TMITweet, TMITweetAdmin)
