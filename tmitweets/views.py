from models import TMITweet, Winner

from django.utils import simplejson
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.functional import wraps
from django.http import HttpResponse
from datetime import datetime, date, timedelta

V_CKIE = 'displayvotes'
ERROR = 'error'
DELIM = '|'

def return_json(view):
    def wrapper(request, *args, **kwargs):
        data = view(request, *args, **kwargs)
        if ERROR in data:
            status = 400
        else:
            status = 200
        json = simplejson.dumps(data, cls=TMIEncoder)
        return HttpResponse(json, mimetype='application/json', status=status)
    return wraps(view)(wrapper)

def votes_cookie(view):
    def wrapper(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        if not V_CKIE in request.COOKIES:
            response.set_cookie(V_CKIE, '', max_age=86400)
        elif 'tweet_id' in kwargs and response.status_code == 200:
            val = DELIM.join(request.session.keys())
            response.set_cookie(V_CKIE, val, max_age=86400)
        return response
    return wraps(view)(wrapper)

@votes_cookie
@return_json
def tweets(request):
    start = datetime.now() - timedelta(1)
    tweets = list(TMITweet.objects.filter(created__gte=start))
    return {'tweets': tweets[:20]}

@return_json
def get_winner(request):
    yesterday = date.today() - timedelta(1)
    try:
        winner = Winner.objects.get(day=yesterday)
    except Winner.DoesNotExist:
        return {ERROR: 'No Winner Found'}
    return {'winner': winner.tweet} 

@votes_cookie
@return_json
def vote(request, tweet_id=None):
    if not V_CKIE in request.COOKIES:
        return {ERROR: 'You must have cookies enabled to vote.'}
    try:
        vote = int(request.POST['vote'])
        if vote != 1 and vote != -1:
            raise ValueError
    except (ValueError, MultiValueDictKeyError):
        return {ERROR: 'You must vote up or down by one'}
    if tweet_id in request.session:
        # vote reversal is allowed, but not double voting
        if not vote == -1:
            return {ERROR: 'You can only vote once per tweet.'}
    elif vote == -1:
        # negative voting not valid unless it's a reversal
        return {ERROR: 'You cannot unvote unless you have voted.'}
    try:
        tweet = TMITweet.objects.get(tweet_id=int(tweet_id))
        tweet.ups += vote 
        tweet.save()
        if vote == 1:
            request.session[tweet_id] = vote
        else:
            del(request.session[tweet_id])
    except TMITweet.DoesNotExist:
        return {ERROR: 'That tweet does not exist.'} 
    return {'acceptedVote': vote}

class TMIEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if isinstance(o, TMITweet):
            return {'twitterUserId': o.twitter_user_id,
                   'twitterUsername': o.twitter_username,
                   'imageUrl': o.image_url,
                    'created': o.created.isoformat(),
                    'tweetId': str(o.tweet_id),
                    'text': o.text,
                    'upVotes': o.ups}
        else:
            return simplejson.JSONEncoder.default(self, o)
