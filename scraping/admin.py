from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.html import format_html
import json

from ai.open_ai_client import OpenAIClient
from ai.prompts import get_place_review_prompt
from .models import ScrapedPlace, ScrapedPost

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

        context = {
            'place': place,
            'post': place.post,
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

admin.site.register(ScrapedPlace, ScrapedPlaceAdmin)
