from django.db import models

class TMITweet(models.Model):
    user_id = models.CharField(max_length=12)
    user_name = models.CharField(max_length=100)
    image_url = models.CharField(max_length=200)
    created = models.DateTimeField()
    tweet_id = models.CharField(max_length=20)
    text = models.CharField(max_length=150)


