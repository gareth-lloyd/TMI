from models import TMITweet
from django.test import TestCase
from django.core.urlresolvers import reverse
import views
import json

from scheduled import *

class EndpointTests(TestCase):
    fixtures = ['tweets']
    def test_tweets(self):
        response = self.client.get(reverse(views.tweets))
        tweets = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(6, len(tweets['tweets']))

    def test_vote_up(self):
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63934172120625152'}), 
                data={'vote': 1})
        json_resp = json.loads(response.content)
        self.assertEqual(1, json_resp['acceptedVote'])
        self.assertEqual(1, 
            TMITweet.objects.get(pk=63934172120625152).ups)

    def test_vote_down(self):
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63934172120625152'}), 
                data={'vote': -1})
        json_resp = json.loads(response.content)
        self.assertEqual(-1, json_resp['acceptedVote'])
        self.assertEqual(1, 
            TMITweet.objects.get(pk=63934172120625152).downs)

    def test_multiple_up_vote_on_different_tweets(self):
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63934172120625152'}), 
                data={'vote': 1})
        self.assertEqual(200, response.status_code)
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63929359576219648'}), 
                data={'vote': 1})
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, 
            TMITweet.objects.get(pk=63929359576219648).ups)

    def test_multiple_up_vote(self):
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63934172120625152'}), 
                data={'vote': 1})
        self.assertEqual(200, response.status_code)
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63934172120625152'}), 
                data={'vote': 1})
        self.assertEqual(400, response.status_code)
        self.assertEqual(1, 
            TMITweet.objects.get(pk=63934172120625152).ups)
    
    def test_multiple_down_vote(self):
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63934172120625152'}), 
                data={'vote': -1})
        self.assertEqual(200, response.status_code)
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63934172120625152'}), 
                data={'vote': -1})
        self.assertEqual(400, response.status_code)
        self.assertEqual(1, 
            TMITweet.objects.get(pk=63934172120625152).downs)
        
    def test_can_vote_down_if_voted_up(self):
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63934172120625152'}), 
                data={'vote': 1})
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'63934172120625152'}), 
                data={'vote': -1})
        json_resp = json.loads(response.content)
        self.assertEqual(-1, json_resp['acceptedVote'])
        self.assertEqual(0, 
            TMITweet.objects.get(pk=63934172120625152).ups)
        self.assertEqual(1, 
            TMITweet.objects.get(pk=63934172120625152).downs)

    def test_vote_with_no_vote_specified(self):
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'639341721206251'}))
        json_resp = json.loads(response.content)
        self.assertTrue(json_resp.has_key('error'))
        self.assertEqual(400, response.status_code)


    def test_vote_on_nonexistent(self):
        response = self.client.post(reverse(views.vote, 
                kwargs={'tweet_id':'639341721206251'}), 
                data={'vote': -1})
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

class ScheduledTests(TestCase):
    def test_result_to_tmi(self):
        result = json.loads("""{"from_user_id_str": "162143438",
            "profile_image_url": "http://a1.twimg.com/profile_images/1331393601/JM0_MiNAj_normal.jpg",
            "created_at": "Sat, 30 Apr 2011 10:44:20 +0000",
            "from_user": "JM0_MiNAj",
            "id_str": "64278906122944512",
              "metadata": {
                  "result_type": "recent"
              },
            "to_user_id": null,
            "text": "I feel like massaging my clit...#TMI and Idk!!!",
            "id": 64278906122944510,
            "from_user_id": 162143438,
            "geo": null,
            "iso_language_code": "en",
            "to_user_id_str": null,
            "source": "&lt;a href=&quot;http://levelupstudio.com&quot; rel=&quot;nofollow&quot;&gt;Plume  &lt;/a&gt;"
        }""")
        tmi_tweet = result_to_tmi_tweet(result)
        tmi_tweet.save()
        
        
