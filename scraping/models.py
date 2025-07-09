from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.models import CreatedUpdatedModel


class ScrapedPost(CreatedUpdatedModel,models.Model):
    third_party_id = models.CharField(max_length=255)
    third_party_type = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    content = models.TextField()
    comments = ArrayField(models.TextField(default=list))
    probability = models.FloatField()
    original_created_at = models.DateTimeField()
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.third_party_type})"



class ScrapedPlace(models.Model,):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255,null=True,blank=True)
    types = ArrayField(models.CharField(max_length=255), default=list)
    post = models.ForeignKey(ScrapedPost, on_delete=models.CASCADE, related_name='places', null=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.city})"
