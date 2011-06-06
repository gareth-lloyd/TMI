#!/usr/bin/env python
from tmitweets.models import TMITweet
from scripts import twitter
from datetime import datetime

from django.core.management import setup_environ
import settings
import re
import os

TMI_SEARCH = "#tmi"
TWITTER_FORMAT = "%a, %d %b %Y %H:%M:%S "

AT_REPLY_RE = re.compile(r'@\w+')
RETWEET_RE = re.compile(r'^RT ', re.IGNORECASE)
# don't need to identify whole url, just enough to reject tweet
LINK_RE = re.compile(r'https?://|bit\.ly/', re.IGNORECASE)
TMI_RE = re.compile(r'#tmi', re.IGNORECASE)

def load_unwanted_users():
    unwanted = []
    with open('unwanted_users.txt') as f:
        for line in f: 
            unwanted.append(line.strip())
    return unwanted
UNWANTED_USERS = load_unwanted_users()

class LastSeen(object):
    "Last seen is persisted. Hide this with a property"
    LS_FILE = 'last_seen_persisted.txt'
    
    def _get(self):
        try: 
            with open(LastSeen.LS_FILE) as f:
                return int(f.read())
        except (ValueError, IOError):
            return -1

    def _set(self, id):
        with open(LastSeen.LS_FILE, 'w') as f:
            f.write(str(id))
    
    id = property(_get, _set)

def date_from_twitter(date_str):
    date_str = date_str.split('+')[0]
    return datetime.strptime(date_str, TWITTER_FORMAT)

def result_to_tmi_tweet(result):
    text = TMI_RE.sub('', result['text'])
    return TMITweet(
           tweet_id=result['id'],
           twitter_user_id=result['from_user_id_str'],
           twitter_username=result['from_user'],
           image_url=result['profile_image_url'],
           created=date_from_twitter(result['created_at']),
           text=text,
           ups=0
        )

def filter_result(result):
    print result
    if result['to_user_id'] is not None:
        return False
    if result['from_user'] in UNWANTED_USERS:
        return False
    if result.get('iso_language_code', 'en') != 'en':
        return False
    text = result['text']
    if len(text) < 32:
        return False
    if RETWEET_RE.match(text):
        return False
    if LINK_RE.search(text):
        return False
    if AT_REPLY_RE.search(text):
        return False
    return True

def latest_tmi():
    last_seen = LastSeen()
    json_response = twitter.search(TMI_SEARCH, last_seen.id)
    results = json_response['results']
    results = filter(filter_result, results)
    if results:
        [tt.save() for tt in map(result_to_tmi_tweet, results)]
        last_seen.id = max(map(lambda t: t['id'], results))
    return len(results)

if __name__ == '__main__':
    setup_environ(settings)
    print 'found %s new TMITweets' % latest_tmi()
