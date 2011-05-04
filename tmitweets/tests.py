from models import * 
from django.test import TestCase
from django.core.urlresolvers import reverse
from datetime import datetime, date, timedelta
import views
import json

from scheduled import *

class EndpointTests(TestCase):
    fixtures = ['tweets']

    def setUp(self):
        # perform an initial request to set the cookie
        self.client.get(reverse(views.tweets))
        # set today's date for all tweets
        for tweet in TMITweet.objects.all():
            tweet.created = datetime.now()
            tweet.save()
    
    def vote(self, id, vote=1):
        return self.client.post(reverse(views.vote, 
                kwargs={'tweet_id': id}), 
                data={'vote': vote})

    def test_tweets(self):
        response = self.client.get(reverse(views.tweets))
        tweets = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(6, len(tweets['tweets']))

    def test_vote_up(self):
        response = self.vote('63934172120625152') 
        json_resp = json.loads(response.content)
        self.assertEqual(1, json_resp['acceptedVote'])
        self.assertEqual(1, 
            TMITweet.objects.get(pk=63934172120625152).ups)

    def test_multiple_up_vote_on_different_tweets(self):
        response = self.vote('63934172120625152') 
        self.assertEqual(200, response.status_code)
        response = self.vote('63929359576219648') 
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, TMITweet.objects.get(pk=63929359576219648).ups)

    def test_multiple_up_vote(self):
        response = self.vote('63934172120625152') 
        self.assertEqual(200, response.status_code)
        response = self.vote('63934172120625152') 
        self.assertEqual(400, response.status_code)
        self.assertEqual(1, TMITweet.objects.get(pk=63934172120625152).ups)
    
    def test_can_vote_down_if_voted_up(self):
        self.vote('63934172120625152') 
        self.assertEqual(1, TMITweet.objects.get(pk=63934172120625152).ups)
        response = self.vote('63934172120625152', vote=-1) 
        json_resp = json.loads(response.content)
        self.assertEqual(-1, json_resp['acceptedVote'])
        self.assertEqual(0, TMITweet.objects.get(pk=63934172120625152).ups)

    def test_can_not_vote_down_if_not_voted_up(self):
        response = self.vote('63934172120625152', vote=-1) 
        self.assertEqual(400, response.status_code)

    def test_vote_with_no_vote_specified(self):
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'639341721206251'}))
        json_resp = json.loads(response.content)
        self.assertTrue(json_resp.has_key('error'))
        self.assertEqual(400, response.status_code)

    def test_vote_on_nonexistent(self):
        response = self.vote('634172120625152', vote=-1) 
        json_resp = json.loads(response.content)
        self.assertTrue(json_resp.has_key('error'))
        self.assertEqual(400, response.status_code)

    def test_vote_bad_data(self):
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63934172120625152'}), 
                data={'vote': -10000000000000000000})
        json_resp = json.loads(response.content)
        self.assertTrue(json_resp.has_key('error'))
        self.assertEqual(400, response.status_code)

from winner import *
class WinnerTests(TestCase):
    fixtures = ['scored_tweets']

    def setUp(self):
        # set today's date for all tweets
        for tweet in TMITweet.objects.all():
            tweet.created = datetime.now() - timedelta(1)
            tweet.save()

    def test_yesterdays_winner(self):
        yesterday = date.today() - timedelta(1)
        self.assertEqual(0, len(Winner.objects.all()))
        yesterdays_winner()
        winner = Winner.objects.get(day=yesterday)
        self.assertEqual(63928730023759872, winner.tweet.tweet_id) 

    def test_get_winner_no_winner(self):
        response = self.client.get(reverse(views.get_winner))
        self.assertEqual(400, response.status_code)

    def test_get_winner(self):
        yesterdays_winner()
        response = self.client.get(reverse(views.get_winner))
        self.assertEqual(200, response.status_code)
        json_resp = json.loads(response.content)
        self.assertEqual(str(63928730023759872), 
            json_resp['winner']['tweetId'])

class CookieTests(TestCase):
    fixtures = ['tweets']

    def vote(self, id, vote=1):
        return self.client.post(reverse(views.vote, 
                kwargs={'tweet_id': id}), 
                data={'vote': vote})

    def test_sets_cookie_after_request_if_none(self):
        response = self.client.get(reverse(views.tweets))
        self.assertEqual('', self.client.cookies['displayvotes'].value)

    def test_vote_fails_without_cookie(self):
        response = self.vote('63934172120625152')
        self.assertEqual(400, response.status_code)

    def test_vote_succeeds_with_cookie(self):
        response = self.client.get(reverse(views.tweets))
        response = self.vote('63934172120625152')
        self.assertEqual(200, response.status_code)
        self.assertEqual('63934172120625152', 
                self.client.cookies['displayvotes'].value)
 
    def test_cookie_same_after_tweets_call(self):
        self.client.get(reverse(views.tweets))
        self.vote('63934172120625152')
        #second call should not change cookie val
        self.client.get(reverse(views.tweets))
        self.assertEqual('63934172120625152', 
                self.client.cookies['displayvotes'].value)

    def test_down_vote_removes_id_from_cookie(self):
        response = self.client.get(reverse(views.tweets))
        response = self.vote('63934172120625152')
        self.assertEqual('63934172120625152', 
                self.client.cookies['displayvotes'].value)
        response = self.vote('63934172120625152', vote=-1)
        self.assertEqual('', self.client.cookies['displayvotes'].value)

    def test_vote_succeeds_with_cookie(self):
        response = self.client.get(reverse(views.tweets))
        response = self.vote('63934172120625152')
        self.assertEqual(200, response.status_code)
        self.assertEqual('63934172120625152', 
                self.client.cookies['displayvotes'].value)

    def test_cookie_after_multiple_votes(self):
        response = self.client.get(reverse(views.tweets))
        response = self.vote('63934172120625152')
        response = self.vote('63929359576219648')
        self.assertEqual('63929359576219648|63934172120625152', 
                self.client.cookies['displayvotes'].value)
 
class ScheduledTests(TestCase):
    def load_json(self, filename):
        with open('tmitweets/fixtures/' + filename, 'r') as f:
            return json.loads(f.read())

    def test_result_to_tmi(self):
        result = self.load_json('standard_tweet.json')
        tmi_tweet = result_to_tmi_tweet(result)
        tmi_tweet.save()
    
    def test_filter_pass(self):
        result = self.load_json('standard_tweet.json')
        self.assertTrue(filter_result(result))

    def test_filter_to_user(self):
        result = self.load_json('tweet_with_to_user.json')
        self.assertFalse(filter_result(result))
    
    def test_filter_unwanted_user(self):
        result = self.load_json('tweet_from_unwanted_user.json')
        self.assertFalse(filter_result(result))
        
    def test_filter_length(self):
        result = self.load_json('short_tweet.json')
        self.assertFalse(filter_result(result))
    
    def test_filter_at_reply(self):
        result = self.load_json('at_reply_tweet.json')
        self.assertFalse(filter_result(result))
    
    def test_filter_RT(self):
        result = self.load_json('retweet.json')
        self.assertFalse(filter_result(result))
 
    def test_filter_link(self):
        result = self.load_json('link_tweet.json')
        self.assertFalse(filter_result(result))
