from django.contrib import admin
from django import forms
from django.contrib.gis.geos import Point

from place.models import Place


from django import forms
from django.contrib.gis.geos import Point
from place.models import Place

class PlaceForm(forms.ModelForm):
    lat = forms.FloatField(required=True)
    lon = forms.FloatField(required=True)

    class Meta:
        model = Place
        exclude = ['lat','lon', 'location']
        widgets = {
            'location': forms.HiddenInput()
        }

    class Media:
        js = ('admin/js/place_location_autofill.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill lat/lon from instance.location if editing
        if self.instance and self.instance.location:
            self.initial['lat'], self.initial['lon'] = self.instance.location.tuple

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('lat')
        lon = cleaned_data.get('lon')
        self.cleaned_data['location'] = Point(lon, lat)
        return self.cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.location = self.cleaned_data['location']
        if commit:
            instance.save()
        return instance

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'location','google_maps_url')
    form = PlaceForm
