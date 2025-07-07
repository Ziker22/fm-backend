from django.contrib import admin

from place.models import Place


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'location',  'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
