import logging
import time
from django.utils import simplejson as json

import oauth2 as oauth

import httplib2

import urllib
from urllib import quote

import twitter_settings

SEARCH = "http://search.twitter.com/search.json?q="
API = "http://api.twitter.com/"

def search(term, since=-1):
    client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
    term = quote(term)

    if since > -1:
        resp, content = client.request(SEARCH + "%s&rpp=100&since_id=%s" % (term, since), "GET")
    else:
        resp, content = client.request(SEARCH + "%s&rpp=100" % term, "GET")

    return json.loads(content)

def get_timeline_tweets_since(since_id=-1):
    client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
    tweets = []

    if since_id < 0:
        resp, content = client.request('http://api.twitter.com/1/statuses/friends_timeline.json', "GET")
        tweets.extend(json.loads(content))
    else:
        # TODO 1 or 0?
        current_page = 0
        while len(tweets) == 0 or not since_id >= max(map(lambda t:int(t['id']), tweets)):
            resp, content = client.request('http://api.twitter.com/1/statuses/friends_timeline.json?count=800&page=' + str(current_page), "GET")
            new_tweets = json.loads(content)
            if len(new_tweets) == 0:
                break
            tweets.extend(new_tweets)
            current_page += 1
            
    return tweets 

def post_tweet(text):
    client = oauth.Client(twitter_settings.consumer, twitter_settings.token)
    resp, content = client.request("http://api.twitter.com/1/statuses/update.json", "POST", urllib.urlencode([("status", text)]))

    return content
