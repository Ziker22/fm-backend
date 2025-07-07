from django.contrib.postgres.fields import ArrayField
from django.db import models


class ScrapedPost(models.Model):
    third_party_id = models.CharField(max_length=255)
    third_party_type = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    content = models.TextField()
    comments = ArrayField(models.TextField(default=list))
    probability = models.FloatField()

class ScrapedPlace(models.Model):
    name = models.CharField(max_length=255)
    types = ArrayField(models.CharField(max_length=255), default=list)
    post = models.ForeignKey(ScrapedPost, on_delete=models.CASCADE, related_name='places', null=True)
    processed = models.BooleanField(default=False)
