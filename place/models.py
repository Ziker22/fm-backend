from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.db.models import OneToOneField

from common.models import CreatedUpdatedModel
from scraping.models import ScrapedPlace


class Place(CreatedUpdatedModel):
    class PlaceType(models.TextChoices):
        PLAYGROUND = "PLAYGROUND"
        INDOOR_PLAYGROUND = "INDOOR_PLAYGROUND"
        KINDERGARTEN = "KINDERGARTEN"
        CAFE = "CAFE"
        RESTAURANT = "RESTAURANT"
        SHOP = "SHOP"
        AMUSEMENT_PARK = "AMUSEMENT_PARK"
        MUSEUM = "MUSEUM"
        GALLERY = "GALLERY"
        ZOO = "ZOO"
        AQUAPARK = "AQUAPARK"
        COMMUNITY_CENTER = "COMMUNITY_CENTER"
        KIDS_PLAYROOM = "KIDS_PLAYROOM"
        CASTLE = "CASTLE"
        HOTEL = "HOTEL"
        ATTRACTION = "ATTRACTION"
        NATURAL_ATTRACTION = "NATURAL_ATTRACTION"

    class PlaceSeasonType(models.TextChoices):
        WINTER = "WINTER"
        SUMMER = "SUMMER"
        ALL = "ALL"

    name = models.CharField(max_length=255, null=False, blank=False)
    scraped_id = OneToOneField(ScrapedPlace, on_delete=models.SET_NULL, null=True, blank=True)
    type = ArrayField(models.CharField(max_length=255, choices=PlaceType.choices), default=list,db_index=True)
    description = models.TextField(null=True, blank=True)
    location = gis_models.PointField(null=False, blank=False)
    country_code = models.CharField(max_length=255, null=False, blank=False)
    city = models.CharField(max_length=255, null=False, blank=False)
    street = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    min_age = models.IntegerField(null=True, blank=True)
    max_age = models.IntegerField(null=True, blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    season = models.CharField(max_length=255, choices=PlaceSeasonType.choices, null=True, blank=True)
    is_admission_free = models.BooleanField(default=False,null=True)
    is_visible = models.BooleanField(default=True,db_index=True)

