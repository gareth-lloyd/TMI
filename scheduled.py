from tmitweets.models import TMITweet
from scripts import twitter
from datetime import datetime
from urllib import unquote

from django.core.management import setup_environ
import settings

TMI_SEARCH = "#tmi"
"Sat, 30 Apr 2011 10:44:20 +0000"
TWITTER_FORMAT = "%a, %d %b %Y %H:%M:%S "

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
    return TMITweet(
           tweet_id=result['id'],
           twitter_user_id=result['from_user_id_str'],
           twitter_username=result['from_user'],
           image_url=result['profile_image_url'],
           created=date_from_twitter(result['created_at']),
           text=unquote(result['text']),
           ups=0, downs=0
        )

def latest_tmi():
    last_seen = LastSeen()
    json_response = twitter.search(TMI_SEARCH, last_seen.id)
    results = json_response['results']
    [tt.save() for tt in map(result_to_tmi_tweet, results)]
    last_seen.id = max(map(lambda t: t['id'], results))
    return len(results)

if __name__ == '__main__':
    setup_environ(settings)
    print 'found %s new TMITweets' % latest_tmi()
