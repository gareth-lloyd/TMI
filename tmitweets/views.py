from models import TMITweet

from django.utils import simplejson
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.functional import wraps
from django.http import HttpResponse
from datetime import datetime, date, timedelta

def return_json(view):
    def wrapper(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        if 'error' in response:
            status = 400
        else:
            status = 200
        json = simplejson.dumps(response, cls=TMIEncoder)
        return HttpResponse(json, mimetype='application/json', status=status)
    return wraps(view)(wrapper)

@return_json
def tweets(request):
    start = datetime.now() - timedelta(1)
    tweets = list(TMITweet.objects.filter(created__gte=start))
    return {'tweets': tweets}

@return_json
def vote(request, tweet_id=None):
    try:
        vote = int(request.POST['vote'])
        if vote != 1 and vote != -1:
            raise ValueError
    except (ValueError, MultiValueDictKeyError):
        return {'error': 'must vote up or down by one'}
    reverse_vote = False
    if tweet_id in request.session:
        if vote == request.session[tweet_id]:
            return {'error': 'only one vote allowed per tweet'}
        else:
            reverse_vote = True
    try:
        tweet = TMITweet.objects.get(tweet_id=int(tweet_id))
        if vote == 1:
            tweet.ups += 1
            if reverse_vote:
                tweet.downs -= 1
        else:
            tweet.downs += 1
            if reverse_vote:
                tweet.ups -= 1
        tweet.save()
        request.session[tweet_id] = vote
    except TMITweet.DoesNotExist:
        return {'error': 'that tweet does not exist'} 
    return {'acceptedVote': vote}


class TMIEncoder(simplejson.JSONEncoder):
    def default(self, o):
        if isinstance(o, TMITweet):
            return {'twitterUserId': o.twitter_user_id,
                   'twitterUsername': o.twitter_username,
                   'imageUrl': o.image_url,
                    'created': o.created.isoformat(),
                    'tweetId': str(o.tweet_id),
                    'text': o.text}
        else:
            return simplejson.JSONEncoder.default(self, o)
