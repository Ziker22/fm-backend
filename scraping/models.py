from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import OneToOneField


class ScrapedPlace(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)

class ScrapedPost(models.Model):
    third_party_id = models.CharField(max_length=255)
    third_party_type = models.CharField(max_length=255)
    title = models.CharField()
    content = models.TextField()
    comments = ArrayField(models.CharField(default=list))
    probability = models.FloatField()
    places = OneToOneField(ScrapedPlace, on_delete=models.CASCADE)

