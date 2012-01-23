#!/usr/bin/env python
from datetime import date, datetime, time, timedelta
from tmitweets.models import TMITweet, Winner
from django.core.management import setup_environ
import settings

def yesterdays_winner():
    yest = date.today() - timedelta(1)
    start = datetime.combine(yest, time.min)
    end = datetime.combine(yest, time.max)
    yest_tweets = TMITweet.objects.filter(
        created__gte=start, created__lte=end)
    if yest_tweets: 
        winningest = max(yest_tweets, key=lambda t: t.ups)
        winner = Winner(tweet=winningest, day=yest)
        winner.save()

if __name__ == '__main__':
    setup_environ(settings)
    yesterdays_winner()
