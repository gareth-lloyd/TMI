from django.db import models

class TMITweet(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True)
    twitter_user_id = models.CharField(max_length=12)
    twitter_username= models.CharField(max_length=100)
    image_url = models.CharField(max_length=200)
    created = models.DateTimeField()
    text = models.CharField(max_length=200)
    ups = models.IntegerField()
    
    class Meta:
        ordering = ['-created']

class Winner(models.Model):
    tweet = models.ForeignKey(TMITweet)
    day = models.DateField(unique=True)
