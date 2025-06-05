from django.db import models
from django.contrib.gis.db import models as gis_models
from common.models import CreatedUpdatedModel

class Place(CreatedUpdatedModel):
    class PlaceType(models.TextChoices):
        INDOOR_PLAYGROUND = "INDOOR_PLAYGROUND"
        PLAYGROUND = "PLAYGROUND"
        RESTAURANT = "RESTAURANT"
        FAMILY_SPOT= "FAMILY_SPOT"
        CAFE = "CAFE"
        KINDERGARTEN = "KINDERGARTEN"

    name = models.CharField(max_length=255, null=False, blank=False)
    location = gis_models.PointField(null=False, blank=False)
    google_maps_url = models.URLField(max_length=255)
    website = models.URLField(max_length=255)
    note = models.TextField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, choices=PlaceType.choices, null=False, blank=False)
