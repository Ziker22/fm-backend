from django.contrib import admin
from django.contrib.gis.geos import Point
from django import forms
from mapwidgets.widgets import MapboxPointFieldStaticWidget

from place.models import Place


class PlaceAdminForm(forms.ModelForm):
    lat = forms.CharField(required=False, help_text='Latitude coordinate')
    lon = forms.CharField(required=False, help_text='Longitude coordinate')

    class Meta:
        model = Place
        fields = '__all__'
        widgets = {
            "location": MapboxPointFieldStaticWidget # or use OSMPointWidget
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.location:
            self.fields['lat'].initial = self.instance.location.y
            self.fields['lon'].initial = self.instance.location.x


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    form = PlaceAdminForm
    list_display = ('name', 'location', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        lat = form.cleaned_data.get('lat')
        lon = form.cleaned_data.get('lon')

        if lat and lon:
            try:
                obj.location = Point(float(lon), float(lat))
            except (ValueError, TypeError):
                # If conversion fails, keep the existing location
                pass

        super().save_model(request, obj, form, change)
