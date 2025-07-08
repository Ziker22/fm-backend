from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.html import format_html
import json
from django.contrib.gis.geos import Point

from ai.open_ai_client import OpenAIClient
from ai.prompts import get_place_review_prompt
from common.geocoding import geocode_address
from .models import ScrapedPlace, ScrapedPost
from place.models import Place
import logging

logger = logging.getLogger(__name__)

@admin.register(ScrapedPost)
class ScrapedPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'third_party_type', 'probability')
    search_fields = ('title', 'content')

class ScrapedPlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'processed')
    ordering = ('name',)
    list_filter = ('processed',)
    search_fields = ('name',)

    def response_change(self, request, obj):
        """Add a review button to the response"""
        response = super().response_change(request, obj)
        if '_review' in request.POST:
            return HttpResponseRedirect(
                reverse('admin:scraping_scrapedplace_review_specific', args=[obj.pk])
            )
        return response

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['review_button_html'] = format_html(
            '<a href="{}" class="button">Review Places</a>',
            reverse("admin:scraping_scrapedplace_review")
        )
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('review/', self.admin_site.admin_view(self.review_view), name='scraping_scrapedplace_review'),
            path('review/<int:place_id>/', self.admin_site.admin_view(self.review_view), name='scraping_scrapedplace_review_specific'),
            path('mark_processed/<int:place_id>/', self.admin_site.admin_view(self.mark_processed), name='scraping_scrapedplace_mark_processed'),
            path('ask_ai/<int:place_id>/', self.admin_site.admin_view(self.ask_ai), name='scraping_scrapedplace_ask_ai'),
            path('ask_ai_from_selection/', self.admin_site.admin_view(self.ask_ai_from_selection), name='scraping_scrapedplace_ask_ai_from_selection'),
            path('save_as_place/<int:place_id>/', self.admin_site.admin_view(self.save_as_place), name='scraping_scrapedplace_save_as_place'),
            path('geocode/<int:place_id>/', self.admin_site.admin_view(self.geocode_place), name='scraping_scrapedplace_geocode'),
        ]
        return custom_urls + urls

    def review_view(self, request, place_id=None):
        """View to review ScrapedPlace entries one by one"""
        if place_id:
            # Get the specific ScrapedPlace
            place = get_object_or_404(ScrapedPlace, id=place_id)
        else:
            # Get the first unprocessed ScrapedPlace
            place = ScrapedPlace.objects.filter(processed=False).order_by("name").first()
            if not place:
                self.message_user(request, "No unprocessed places found.")
                return HttpResponseRedirect(reverse('admin:scraping_scrapedplace_changelist'))

        # Get related places
        related_places = Place.objects.filter(scraped_id=place)

        context = {
            'place': place,
            'post': place.post,
            'related_places': related_places,
            'opts': self.model._meta,
            'title': 'Review Scraped Place',
            'app_label': self.model._meta.app_label,
            'original': place,
            'has_view_permission': self.has_view_permission(request, place),
        }

        return TemplateResponse(request, 'admin/scraping/scrapedplace/review.html', context)

    def mark_processed(self, request, place_id):
        """Mark a ScrapedPlace as processed and redirect to the next one"""
        place = get_object_or_404(ScrapedPlace, id=place_id)
        place.processed = True
        place.save()

        self.message_user(request, f"Place '{place.name}' marked as processed.")
        return HttpResponseRedirect(reverse('admin:scraping_scrapedplace_review'))

    def ask_ai(self, request, place_id):
        """Generate AI response for a ScrapedPlace"""
        place = get_object_or_404(ScrapedPlace, id=place_id)

        try:
            # Create OpenAI client
            client = OpenAIClient(model="gpt-4.1")

            # Generate prompt using place data
            prompt = get_place_review_prompt(
                name=place.name,
                city=place.city or "",
                types=place.types
            )

            # Get response from OpenAI
            response = client.get_websearch_response(prompt,True)

            # Parse the response as JSON
            if isinstance(response, str):
                response_data = json.loads(response)
            else:
                response_data = response

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def ask_ai_from_selection(self, request):

        try:
            # Get the selected text from the request
            data = json.loads(request.body)
            selected_text = data.get('selected_text', '')

            if not selected_text:
                return JsonResponse({"error": "No text selected"}, status=400)

            # Create OpenAI client
            client = OpenAIClient(model="gpt-4.1")

            logger.info(f"Getting AI response from selection {selected_text} ...")
            prompt = get_place_review_prompt(
                name=selected_text,
                city="",
                types=[]
            )

            # Get response from OpenAI
            response = client.get_websearch_response(prompt, True)

            # Parse the response as JSON
            if isinstance(response, str):
                response_data = json.loads(response)
            else:
                response_data = response

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def save_as_place(self, request, place_id):
        """Save AI response as a Place"""
        if request.method != 'POST':
            return JsonResponse({"error": "Only POST method is allowed"}, status=405)

        scraped_place = get_object_or_404(ScrapedPlace, id=place_id)

        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)

            # Create a Point object from lat and lon
            if 'lat' in data and 'lon' in data:
                location = Point(float(data['lon']), float(data['lat']))
            else:
                return JsonResponse({"error": "Latitude and longitude are required"}, status=400)

            # Map season value to PlaceSeasonType
            season_mapping = {
                'winter': Place.PlaceSeasonType.WINTER,
                'summer': Place.PlaceSeasonType.SUMMER,
                'all': Place.PlaceSeasonType.ALL
            }
            season = season_mapping.get(data.get('season', '').lower(), Place.PlaceSeasonType.ALL)

            # Map types to PlaceType
            types = []
            if 'types' in data and isinstance(data['types'], list):
                for type_name in data['types']:
                    type_upper = type_name.upper()
                    if hasattr(Place.PlaceType, type_upper):
                        types.append(getattr(Place.PlaceType, type_upper))

            # Create and save the Place object
            place = Place(
                name=data.get('name', ''),
                scraped_id=scraped_place,
                type=types,
                description=data.get('description', ''),
                location=location,
                country_code=data.get('country_code', ''),
                city=data.get('city', ''),
                min_age=data.get('min_age'),
                max_age=data.get('max_age'),
                website=data.get('website', ''),
                street=data.get('street', ''),
                zip_code=data.get('zip_code', ''),
                season=season,
                is_admission_free=data.get('is_admission_free', False)
            )
            place.save()

            # Get all Places related to this ScrapedPlace
            related_places = Place.objects.filter(scraped_id=scraped_place)

            # Prepare the response data
            response_data = {
                "success": True,
                "message": f"Place '{place.name}' saved successfully",
                "place": {
                    "id": place.id,
                    "name": place.name,
                    "type": place.type,
                    "description": place.description,
                    "city": place.city,
                    "country_code": place.country_code,
                    "min_age": place.min_age,
                    "max_age": place.max_age,
                    "website": place.website,
                    "season": place.season,
                    "is_admission_free": place.is_admission_free
                },
                "related_places": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "type": p.type,
                        "city": p.city
                    } for p in related_places
                ]
            }

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def geocode_place(self, request, place_id):
        """Geocode a place using the geocode_address function"""
        if request.method != 'POST':
            return JsonResponse({"error": "Only POST method is allowed"}, status=405)

        try:
            # Parse the JSON data from the request
            data = json.loads(request.body)

            # Extract address components
            street = data.get('street', '')
            zip_code = data.get('zip_code', '')
            city = data.get('city', '')
            place_name = data.get('place_name', '')
            country_code = data.get('country_code', 'us')

            # Call the geocode_address function
            point, response_data = geocode_address(
                street=street,
                zip_code=zip_code,
                city=city,
                place_name=place_name,
                country_code=country_code
            )

            if point:
                # Return the coordinates
                return JsonResponse({
                    "success": True,
                    "lat": point.y,
                    "lon": point.x
                })
            else:
                # Return error if geocoding failed
                return JsonResponse({
                    "success": False,
                    "error": "Geocoding failed. Please check the address."
                })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

admin.site.register(ScrapedPlace, ScrapedPlaceAdmin)
